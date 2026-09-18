"""Cliente OAuth + Calendar API do Google, via httpx puro (sem SDK pesado,
mesmo padrao do cliente do pam-geh).

Fluxo: authorization code -> troca por access/refresh token -> guarda em
GoogleCalendarAuth (singleton, id=1) -> usa freeBusy pra calcular horarios
livres reais -> cria o evento na agenda quando o vendedor escolhe um.
"""
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.google_calendar_auth import GoogleCalendarAuth

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
FREEBUSY_URL = "https://www.googleapis.com/calendar/v3/freeBusy"
EVENTS_URL_TMPL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"

SCOPE = "https://www.googleapis.com/auth/calendar"
TZ = ZoneInfo("America/Sao_Paulo")
HORA_INICIO_EXPEDIENTE = 9
HORA_FIM_EXPEDIENTE = 18
DURACAO_SLOT_MINUTOS = 30


async def _get_or_create_auth(db: AsyncSession) -> GoogleCalendarAuth:
    auth = await db.get(GoogleCalendarAuth, 1)
    if auth is None:
        auth = GoogleCalendarAuth(id=1)
        db.add(auth)
        await db.flush()
    return auth


def build_redirect_uri() -> str:
    return f"{settings.app_base_url.rstrip('/')}/api/agenda/callback"


async def build_auth_url(db: AsyncSession) -> str:
    auth = await _get_or_create_auth(db)
    state = secrets.token_urlsafe(24)
    auth.oauth_state = state
    await db.flush()

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": build_redirect_uri(),
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"


async def exchange_code(db: AsyncSession, code: str, state: str) -> None:
    auth = await _get_or_create_auth(db)
    if not auth.oauth_state or auth.oauth_state != state:
        raise ValueError("state OAuth invalido - tente conectar de novo")

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": build_redirect_uri(),
            },
        )
        resp.raise_for_status()
        data = resp.json()

    auth.access_token = data["access_token"]
    auth.refresh_token = data.get("refresh_token") or auth.refresh_token
    auth.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])
    auth.oauth_state = None
    auth.connected_at = datetime.now(timezone.utc)
    await db.flush()


async def disconnect(db: AsyncSession) -> None:
    auth = await _get_or_create_auth(db)
    auth.access_token = None
    auth.refresh_token = None
    auth.token_expiry = None
    auth.connected_at = None
    await db.flush()


async def is_connected(db: AsyncSession) -> bool:
    auth = await db.get(GoogleCalendarAuth, 1)
    return bool(auth and auth.refresh_token)


async def _valid_access_token(db: AsyncSession) -> str:
    auth = await _get_or_create_auth(db)
    if not auth.refresh_token:
        raise ValueError("Google Calendar nao conectado")

    if auth.token_expiry and auth.token_expiry > datetime.now(timezone.utc) + timedelta(seconds=30):
        return auth.access_token

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": auth.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    auth.access_token = data["access_token"]
    auth.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])
    await db.flush()
    return auth.access_token


def _janelas_expediente(dias: int) -> list[tuple[datetime, datetime]]:
    """Janelas de expediente (9h-18h, seg-sex) pros proximos `dias` dias uteis."""
    janelas = []
    cursor = datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    if cursor.hour >= HORA_FIM_EXPEDIENTE:
        cursor = cursor + timedelta(days=1)
    dias_encontrados = 0
    tentativas = 0
    while dias_encontrados < dias and tentativas < dias * 3 + 7:
        tentativas += 1
        dia = (cursor + timedelta(days=tentativas - 1)).date()
        data_hora = datetime.combine(dia, datetime.min.time(), tzinfo=TZ)
        if data_hora.weekday() >= 5:  # sabado/domingo
            continue
        inicio = data_hora.replace(hour=HORA_INICIO_EXPEDIENTE)
        fim = data_hora.replace(hour=HORA_FIM_EXPEDIENTE)
        agora = datetime.now(TZ)
        if fim <= agora:
            continue
        if inicio < agora:
            inicio = agora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        if inicio >= fim:
            continue
        janelas.append((inicio, fim))
        dias_encontrados += 1
    return janelas


async def listar_horarios_livres(db: AsyncSession, dias: int = 3) -> list[dict]:
    auth = await _get_or_create_auth(db)
    access_token = await _valid_access_token(db)
    janelas = _janelas_expediente(dias)
    if not janelas:
        return []

    time_min = janelas[0][0]
    time_max = janelas[-1][1]

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            FREEBUSY_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "timeMin": time_min.isoformat(),
                "timeMax": time_max.isoformat(),
                "items": [{"id": auth.calendar_id}],
            },
        )
        resp.raise_for_status()
        data = resp.json()

    ocupados = [
        (datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"]))
        for b in data["calendars"].get(auth.calendar_id, {}).get("busy", [])
    ]

    slots = []
    for inicio_janela, fim_janela in janelas:
        cursor = inicio_janela
        while cursor + timedelta(minutes=DURACAO_SLOT_MINUTOS) <= fim_janela:
            slot_fim = cursor + timedelta(minutes=DURACAO_SLOT_MINUTOS)
            conflita = any(cursor < b_fim and slot_fim > b_inicio for b_inicio, b_fim in ocupados)
            if not conflita:
                slots.append({"inicio": cursor.isoformat(), "fim": slot_fim.isoformat()})
            cursor = slot_fim

    return slots


async def criar_evento(db: AsyncSession, titulo: str, descricao: str, inicio_iso: str, fim_iso: str) -> dict:
    auth = await _get_or_create_auth(db)
    access_token = await _valid_access_token(db)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            EVENTS_URL_TMPL.format(calendar_id=auth.calendar_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "summary": titulo,
                "description": descricao,
                "start": {"dateTime": inicio_iso, "timeZone": "America/Sao_Paulo"},
                "end": {"dateTime": fim_iso, "timeZone": "America/Sao_Paulo"},
            },
        )
        resp.raise_for_status()
        return resp.json()
