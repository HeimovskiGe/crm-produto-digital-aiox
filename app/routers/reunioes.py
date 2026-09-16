"""Reuniao de Venda - os 7 Passos (aula 3, Lucas Carmo) - e o roteiro
personalizado de perguntas pra cada lead.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.lead import EtapaProcesso, Lead
from app.models.produto import ConfiguracaoProduto
from app.models.reuniao_venda import ResultadoReuniao, ReuniaoVenda
from app.schemas.reuniao_venda import ReuniaoVendaOut, ReuniaoVendaUpdate
from app.services.roteiro_7_passos import gerar_roteiro

router = APIRouter(tags=["reunioes"])


async def _get_lead_or_404(lead_id: int, db: AsyncSession) -> Lead:
    lead = await db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead nao encontrado")
    return lead


@router.get("/api/leads/{lead_id}/roteiro")
async def get_roteiro(lead_id: int, db: AsyncSession = Depends(get_db)):
    lead = await _get_lead_or_404(lead_id, db)
    produto_result = await db.execute(select(ConfiguracaoProduto).where(ConfiguracaoProduto.id == 1))
    produto = produto_result.scalar_one_or_none() or ConfiguracaoProduto(id=1)
    return gerar_roteiro(lead, produto)


@router.get("/api/leads/{lead_id}/reunioes/atual", response_model=ReuniaoVendaOut)
async def get_reuniao_atual(lead_id: int, db: AsyncSession = Depends(get_db)):
    await _get_lead_or_404(lead_id, db)
    result = await db.execute(
        select(ReuniaoVenda)
        .where(ReuniaoVenda.lead_id == lead_id, ReuniaoVenda.data_hora_fim.is_(None))
        .order_by(ReuniaoVenda.data_hora_inicio.desc())
    )
    reuniao = result.scalars().first()
    if reuniao is None:
        raise HTTPException(status_code=404, detail="Nenhuma reuniao em andamento pra este lead")
    return reuniao


@router.post("/api/leads/{lead_id}/reunioes", response_model=ReuniaoVendaOut, status_code=201)
async def create_reuniao(lead_id: int, db: AsyncSession = Depends(get_db)):
    lead = await _get_lead_or_404(lead_id, db)
    reuniao = ReuniaoVenda(lead_id=lead_id, data_hora_inicio=datetime.now(timezone.utc))
    db.add(reuniao)
    lead.etapa_processo = EtapaProcesso.REUNIAO_VENDA
    await db.flush()
    await db.refresh(reuniao)
    return reuniao


@router.patch("/api/reunioes/{reuniao_id}", response_model=ReuniaoVendaOut)
async def update_reuniao(reuniao_id: int, payload: ReuniaoVendaUpdate, db: AsyncSession = Depends(get_db)):
    reuniao = await db.get(ReuniaoVenda, reuniao_id)
    if reuniao is None:
        raise HTTPException(status_code=404, detail="Reuniao nao encontrada")

    updates = payload.model_dump(exclude_unset=True)

    if updates.get("di_confirmada") and not reuniao.di_confirmada:
        reuniao.di_timestamp = datetime.now(timezone.utc)

    for field, value in updates.items():
        setattr(reuniao, field, value)

    if reuniao.resultado in (ResultadoReuniao.GANHO, ResultadoReuniao.PERDIDO):
        if reuniao.data_hora_fim is None:
            reuniao.data_hora_fim = datetime.now(timezone.utc)
        lead = await db.get(Lead, reuniao.lead_id)
        if lead is not None:
            lead.etapa_processo = (
                EtapaProcesso.FECHADO_GANHO
                if reuniao.resultado == ResultadoReuniao.GANHO
                else EtapaProcesso.FECHADO_PERDIDO
            )

    await db.flush()
    await db.refresh(reuniao)
    return reuniao
