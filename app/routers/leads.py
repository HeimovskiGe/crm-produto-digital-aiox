"""Endpoints de Leads - funil de prospeccao (Piramide da Prospeccao)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.atividade import AtividadeProspeccao
from app.models.lead import Lead, PipelineStage
from app.schemas.atividade import AtividadeCreate, AtividadeOut
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate

router = APIRouter(prefix="/api/leads", tags=["leads"])

# Unica fonte de rotulo dos estagios - o frontend consome isto, nao duplica a lista.
PIPELINE_STAGE_LABELS = [
    {"value": PipelineStage.BASE_NAO_VERIFICADO.value, "label": "Base (nao verificado)"},
    {"value": PipelineStage.INFORMACAO_SOLIDA.value, "label": "Informacao solida"},
    {"value": PipelineStage.JANELA_IDENTIFICADA.value, "label": "Janela identificada"},
    {"value": PipelineStage.CONQUISTA_PRIORITARIA.value, "label": "Conquista prioritaria"},
    {"value": PipelineStage.INDICACAO_QUENTE.value, "label": "Indicacao quente"},
    {"value": PipelineStage.QUALIFICADO_PRONTO.value, "label": "Qualificado, pronto"},
]


async def _get_lead_or_404(lead_id: int, db: AsyncSession) -> Lead:
    lead = await db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead nao encontrado")
    return lead


@router.get("/meta/stages")
async def list_stages():
    return PIPELINE_STAGE_LABELS


@router.get("", response_model=list[LeadOut])
async def list_leads(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).order_by(Lead.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    lead = Lead(**payload.model_dump())
    db.add(lead)
    await db.flush()
    await db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_lead_or_404(lead_id, db)


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead(lead_id: int, payload: LeadUpdate, db: AsyncSession = Depends(get_db)):
    lead = await _get_lead_or_404(lead_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    await db.flush()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    lead = await _get_lead_or_404(lead_id, db)
    await db.delete(lead)


@router.post("/{lead_id}/atividades", response_model=AtividadeOut, status_code=201)
async def create_atividade(lead_id: int, payload: AtividadeCreate, db: AsyncSession = Depends(get_db)):
    lead = await _get_lead_or_404(lead_id, db)
    atividade = AtividadeProspeccao(lead_id=lead_id, **payload.model_dump())
    db.add(atividade)
    lead.tentativas_contato += 1
    await db.flush()
    await db.refresh(atividade)
    return atividade


@router.get("/{lead_id}/atividades", response_model=list[AtividadeOut])
async def list_atividades(lead_id: int, db: AsyncSession = Depends(get_db)):
    await _get_lead_or_404(lead_id, db)
    result = await db.execute(
        select(AtividadeProspeccao)
        .where(AtividadeProspeccao.lead_id == lead_id)
        .order_by(AtividadeProspeccao.data_hora.desc())
    )
    return result.scalars().all()
