"""Kanban por fonte de empresarios ja scraped (pam-geh) - sem migrar dado.

Le e atualiza direto nas 6 tabelas originais via PostgREST (service_role,
server-side). Cada fonte usa o proprio vocabulario de status que ja existe
la (novo/contatado/respondeu/negociando/fechado/perdido) - nao usa
etapa_processo nem pipeline_stage deste CRM.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.pamgeh_client import pamgeh_client

router = APIRouter(prefix="/api/empresarios", tags=["empresarios"])

FONTES = {
    "prudentopolis": {"table": "leads_prudentopolis", "label": "Prudentopolis"},
    "pontagrossa": {"table": "leads_pontagrossa", "label": "Ponta Grossa"},
    "estetica": {"table": "leads_estetica", "label": "Estetica"},
    "paroquias": {"table": "leads_paroquias", "label": "Paroquias-PR"},
    "trafego": {"table": "leads_trafego", "label": "Trafego Curitiba"},
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


def _table_or_404(fonte: str) -> str:
    if fonte not in FONTES:
        raise HTTPException(status_code=404, detail="Fonte desconhecida")
    return FONTES[fonte]["table"]


@router.get("/meta/fontes")
async def list_fontes():
    return [{"value": k, "label": v["label"]} for k, v in FONTES.items()]


@router.get("/meta/status")
async def list_status_columns():
    return STATUS_COLUMNS


@router.get("/{fonte}")
async def list_por_status(fonte: str, status: str, limit: int = DEFAULT_LIMIT, offset: int = 0):
    table = _table_or_404(fonte)
    items, total = await pamgeh_client.list_by_status(table, status, limit, offset)
    return {"items": items, "total": total}


@router.patch("/{fonte}/{record_id}")
async def update_status(fonte: str, record_id: str, payload: StatusUpdate):
    table = _table_or_404(fonte)
    await pamgeh_client.update_status(table, record_id, payload.status)
    return {"ok": True}
