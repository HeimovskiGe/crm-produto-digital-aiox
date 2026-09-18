"""Google Calendar - horarios livres reais pra agendar Reuniao de Venda
direto no lead, sem sair do CRM (Horas de Ouro/Platina do livro viram
'candidato a modulo futuro' no schema, isso aqui e so o agendamento).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.lead import Lead
from app.schemas.agenda import AgendaStatus, CriarEventoPayload, EventoCriado, HorarioLivre
from app.services import google_calendar_client as gcal

router = APIRouter(prefix="/api/agenda", tags=["agenda"])


@router.get("/status", response_model=AgendaStatus)
async def status(db: AsyncSession = Depends(get_db)):
    return AgendaStatus(conectado=await gcal.is_connected(db))


@router.get("/conectar")
async def conectar(db: AsyncSession = Depends(get_db)):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=400, detail="GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET nao configurados")
    url = await gcal.build_auth_url(db)
    return RedirectResponse(url)


@router.get("/callback")
async def callback(code: str = "", state: str = "", error: str = "", db: AsyncSession = Depends(get_db)):
    if error:
        return RedirectResponse(f"/?agenda=erro&motivo={error}")
    try:
        await gcal.exchange_code(db, code, state)
    except Exception as e:
        return RedirectResponse(f"/?agenda=erro&motivo={type(e).__name__}")
    return RedirectResponse("/?agenda=conectado")


@router.post("/desconectar")
async def desconectar(db: AsyncSession = Depends(get_db)):
    await gcal.disconnect(db)
    return {"ok": True}


@router.get("/horarios-livres", response_model=list[HorarioLivre])
async def horarios_livres(dias: int = Query(3, ge=1, le=10), db: AsyncSession = Depends(get_db)):
    if not await gcal.is_connected(db):
        raise HTTPException(status_code=400, detail="Google Calendar nao conectado")
    try:
        slots = await gcal.listar_horarios_livres(db, dias)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro consultando o Google Calendar: {e}")
    return [HorarioLivre(inicio=s["inicio"], fim=s["fim"]) for s in slots]


@router.post("/eventos", response_model=EventoCriado)
async def criar_evento(payload: CriarEventoPayload, db: AsyncSession = Depends(get_db)):
    if not await gcal.is_connected(db):
        raise HTTPException(status_code=400, detail="Google Calendar nao conectado")

    lead = await db.get(Lead, payload.lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead nao encontrado")

    titulo = f"Reuniao de Venda - {lead.nome}"
    partes_descricao = [p for p in [lead.empresa, lead.telefone, lead.territorio] if p]
    descricao = " · ".join(partes_descricao)

    try:
        evento = await gcal.criar_evento(db, titulo, descricao, payload.inicio, payload.fim)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro criando evento no Google Calendar: {e}")

    return EventoCriado(evento_id=evento.get("id", ""), link=evento.get("htmlLink"))
