"""Kanban por fonte de empresarios ja scraped (pam-geh) - sem migrar dado.

Le e atualiza direto nas 6 tabelas originais via PostgREST (service_role,
server-side). Cada fonte usa o proprio vocabulario de status que ja existe
la (novo/contatado/respondeu/negociando/fechado/perdido) - nao usa
etapa_processo nem pipeline_stage deste CRM.
"""
import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.atividade import AtividadeProspeccao, ObjetivoContato
from app.models.lead import EtapaProcesso, Lead
from app.schemas.atividade import AtividadeEmpresarioCreate, AtividadeOut
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
TODAS = "todas"


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
    # "Todas as Frentes" no fim: a fonte inicial ao abrir a aba continua
    # sendo uma unica tabela (leve). O combinado e' pesado (5x as chamadas
    # por status) e e' escolha explicita do usuario.
    fontes = [{"value": k, "label": v["label"], "extra_field": v.get("extra_field")} for k, v in FONTES.items()]
    return fontes + [{"value": TODAS, "label": "🌐 Todas as Frentes", "extra_field": None}]


@router.get("/meta/status")
async def list_status_columns():
    return STATUS_COLUMNS


async def _distinct_all_fontes(column: str) -> list[str]:
    results = await asyncio.gather(
        *(pamgeh_client.list_distinct(v["table"], column) for v in FONTES.values())
    )
    merged: set[str] = set()
    for values in results:
        merged.update(values)
    return sorted(merged)


@router.get("/meta/{fonte}/municipios")
async def list_municipios(fonte: str):
    if fonte == TODAS:
        return await _distinct_all_fontes("municipio")
    table = _table_or_404(fonte)
    return await pamgeh_client.list_distinct(table, "municipio")


@router.get("/meta/{fonte}/tags")
async def list_tags(fonte: str):
    if fonte == TODAS:
        return await _distinct_all_fontes("ia_tag")
    table = _table_or_404(fonte)
    return await pamgeh_client.list_distinct(table, "ia_tag")


@router.get("/meta/{fonte}/cnaes")
async def list_cnaes(fonte: str):
    if fonte == TODAS:
        return await _distinct_all_fontes("cnae")
    table = _table_or_404(fonte)
    return await pamgeh_client.list_distinct(table, "cnae")


@router.get("/{fonte}")
async def list_por_status(
    fonte: str,
    status: str,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    municipio: str | None = None,
    tag: str | None = None,
    cnae: str | None = None,
):
    if fonte == TODAS:
        results = await asyncio.gather(
            *(
                pamgeh_client.list_by_status(
                    v["table"], status, limit, offset,
                    municipio=municipio, tag=tag, cnae=cnae,
                    select_fields=_select_fields_for(k),
                )
                for k, v in FONTES.items()
            )
        )
        items: list[dict] = []
        total = 0
        for (fonte_key, fonte_meta), (fonte_items, fonte_total) in zip(FONTES.items(), results):
            for item in fonte_items:
                item["_fonte"] = fonte_key
                item["_fonte_label"] = fonte_meta["label"]
            items.extend(fonte_items)
            total += fonte_total
        items.sort(key=lambda i: i.get("created_at") or "", reverse=True)
        return {"items": items, "total": total}

    table = _table_or_404(fonte)
    items, total = await pamgeh_client.list_by_status(
        table, status, limit, offset,
        municipio=municipio, tag=tag, cnae=cnae,
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


@router.post("/atividades", response_model=AtividadeOut, status_code=201)
async def registrar_atividade_empresario(
    payload: AtividadeEmpresarioCreate, db: AsyncSession = Depends(get_db)
):
    """Registra 1 toque (ex: clique no WhatsApp) num empresario cru, sem
    precisar promove-lo a Lead primeiro - e o que faz a visao 'Por Dia'
    contar tambem a prospeccao fria feita direto no funil de Empresarios."""
    _fonte_or_404(payload.fonte)
    atividade = AtividadeProspeccao(
        canal=payload.canal,
        objetivo_contato=ObjetivoContato.MARCAR_REUNIAO,
        data_hora=datetime.now(timezone.utc),
        empresario_fonte=payload.fonte,
        empresario_record_id=payload.record_id,
        empresario_nome=payload.nome,
    )
    db.add(atividade)
    await db.flush()
    await db.refresh(atividade)
    return atividade


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
