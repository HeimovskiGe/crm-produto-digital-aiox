"""Captura de Referidos - Passo 6/7 dos 7 Passos (aula 3, Lucas Carmo).

Referido se pega na hora, ainda na reuniao; a validacao (Passo 7) e so
marcar que a mensagem de pre-aviso foi enviada pro indicado.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.lead import Lead
from app.models.referido import Referido
from app.schemas.referido import ReferidoCreate, ReferidoOut, ReferidoUpdate

router = APIRouter(tags=["referidos"])


@router.get("/api/leads/{lead_id}/referidos", response_model=list[ReferidoOut])
async def list_referidos(lead_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Referido).where(Referido.lead_origem_id == lead_id).order_by(Referido.data_hora)
    )
    return result.scalars().all()


@router.post("/api/leads/{lead_id}/referidos", response_model=ReferidoOut, status_code=201)
async def create_referido(lead_id: int, payload: ReferidoCreate, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead nao encontrado")

    referido = Referido(
        lead_origem_id=lead_id,
        nome_indicado=payload.nome_indicado,
        contato_indicado=payload.contato_indicado,
        data_hora=datetime.now(timezone.utc),
    )
    db.add(referido)
    await db.flush()
    await db.refresh(referido)
    return referido


@router.patch("/api/referidos/{referido_id}", response_model=ReferidoOut)
async def update_referido(referido_id: int, payload: ReferidoUpdate, db: AsyncSession = Depends(get_db)):
    referido = await db.get(Referido, referido_id)
    if referido is None:
        raise HTTPException(status_code=404, detail="Referido nao encontrado")
    referido.mensagem_validacao_enviada = payload.mensagem_validacao_enviada
    await db.flush()
    await db.refresh(referido)
    return referido
