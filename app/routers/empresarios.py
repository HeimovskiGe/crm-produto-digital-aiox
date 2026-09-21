"""Kanban por fonte de empresarios ja scraped (pam-geh) - sem migrar dado.

Le e atualiza direto nas 6 tabelas originais via PostgREST (service_role,
server-side). Cada fonte usa o proprio vocabulario de status que ja existe
la (novo/contatado/respondeu/negociando/fechado/perdido) - nao usa
etapa_processo nem pipeline_stage deste CRM.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.lead import EtapaProcesso, Lead
from app.services.pamgeh_client import SELECT_FIELDS, pamgeh_client

router = APIRouter(prefix="/api/empresarios", tags=["empresarios"])

FONTES = {
    "prudentopolis": {"table": "leads_prudentopolis", "label": "Prudentopolis"},
    "pontagrossa": {"table": "leads_pontagrossa", "label": "Ponta Grossa"},
    "estetica": {"table": "leads_estetica", "label": "Estetica"},
    "paroquias": {"table": "leads_paroquias", "label": "Paroquias-PR", "extra_field": "tipo"},
    "trafego": {"table": "leads_trafego", "label": "Trafego Curitiba", "extra_field": "nicho"},
}
# "saojose" (leads_saojose) tinha SQL local mas a tabela nunca foi aplicada
# no Supabase real do pam-geh (confirmado via /rest/v1/ - 404). Fora da
# lista ate existir de verdade.

STATUS_COLUMNS = [
    {"value": "novo", "label": "Novo Lead"},
    {"value": "contatado", "label": "Contatado"},
    {"value": "respondeu", "label": "Respondeu"},
    {"value": "negociando", "label": "Negociando"},
    {"value": "fechado", "label": "Fechado"},
    {"value": "perdido", "label": "Perdido"},
]

DEFAULT_LIMIT = 30


class StatusUpdate(BaseModel):
    status: str


class ObsUpdate(BaseModel):
    obs: str


class ProspectarPayload(BaseModel):
    nome_fantasia: str | None = None
    razao_social: str | None = None
    telefone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    municipio: str | None = None
    bairro: str | None = None
    cnae: str | None = None


def _fonte_or_404(fonte: str) -> dict:
    if fonte not in FONTES:
        raise HTTPException(status_code=404, detail="Fonte desconhecida")
    return FONTES[fonte]


def _table_or_404(fonte: str) -> str:
    return _fonte_or_404(fonte)["table"]


def _select_fields_for(fonte: str) -> str:
    extra = FONTES[fonte].get("extra_field")
    return f"{SELECT_FIELDS},{extra}" if extra else SELECT_FIELDS


@router.get("/meta/fontes")
async def list_fontes():
    return [{"value": k, "label": v["label"], "extra_field": v.get("extra_field")} for k, v in FONTES.items()]


@router.get("/meta/status")
async def list_status_columns():
    return STATUS_COLUMNS


@router.get("/meta/{fonte}/municipios")
async def list_municipios(fonte: str):
    table = _table_or_404(fonte)
    return await pamgeh_client.list_distinct(table, "municipio")


@router.get("/meta/{fonte}/tags")
async def list_tags(fonte: str):
    table = _table_or_404(fonte)
    return await pamgeh_client.list_distinct(table, "ia_tag")


@router.get("/{fonte}")
async def list_por_status(
    fonte: str,
    status: str,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    municipio: str | None = None,
    tag: str | None = None,
):
    table = _table_or_404(fonte)
    items, total = await pamgeh_client.list_by_status(
        table, status, limit, offset,
        municipio=municipio, tag=tag,
        select_fields=_select_fields_for(fonte),
    )
    return {"items": items, "total": total}


@router.patch("/{fonte}/{record_id}")
async def update_status(fonte: str, record_id: str, payload: StatusUpdate):
    table = _table_or_404(fonte)
    await pamgeh_client.update_status(table, record_id, payload.status)
    return {"ok": True}


@router.patch("/{fonte}/{record_id}/obs")
async def update_obs(fonte: str, record_id: str, payload: ObsUpdate):
    table = _table_or_404(fonte)
    await pamgeh_client.update_fields(table, record_id, {"obs": payload.obs})
    return {"ok": True}


@router.post("/{fonte}/{record_id}/prospectar")
async def prospectar(
    fonte: str, record_id: str, payload: ProspectarPayload, db: AsyncSession = Depends(get_db)
):
    """Promove um empresario da fonte pra um Lead de verdade neste CRM,
    pra poder rodar o funil (etapa_processo) e a Reuniao de Venda (7 Passos)
    nele. Nao apaga nem duplica nada na fonte - so marca como 'contatado' la,
    porque agora esta sendo trabalhado aqui."""
    table = _table_or_404(fonte)
    nome = payload.nome_fantasia or payload.razao_social or "(sem nome)"
    territorio = ", ".join(filter(None, [payload.bairro, payload.municipio])) or None

    lead = Lead(
        nome=nome,
        empresa=payload.razao_social,
        telefone=payload.telefone or payload.whatsapp,
        email=payload.email,
        territorio=territorio,
        vertical=payload.cnae,
        origem=f"pam-geh:{fonte}",
        etapa_processo=EtapaProcesso.PROSPECCAO,
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)

    try:
        await pamgeh_client.update_status(table, record_id, "contatado")
    except Exception:
        pass  # lead ja foi criado; falha em marcar a fonte nao desfaz isso

    return {"lead_id": lead.id}
