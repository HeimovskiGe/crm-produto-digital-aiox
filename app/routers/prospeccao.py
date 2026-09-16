"""Painel de Intencao de Prospeccao - meta diaria, streak, tempo parado.

Cobra do vendedor a disciplina diaria (aula 2, Lucas Carmo: formula de
proporcao pessoal, ex. 150 prospeccoes/dia) sem inventar numero fixo -
o usuario define a propria meta.
"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.atividade import AtividadeProspeccao
from app.models.metrica_diaria import MetricaDiaria
from app.schemas.prospeccao import IntencaoOut, MetaUpdate

router = APIRouter(prefix="/api/prospeccao", tags=["prospeccao"])


async def _get_or_create_hoje(db: AsyncSession) -> MetricaDiaria:
    hoje = date.today()
    result = await db.execute(select(MetricaDiaria).where(MetricaDiaria.data == hoje))
    metrica = result.scalar_one_or_none()
    if metrica is None:
        metrica = MetricaDiaria(data=hoje)
        db.add(metrica)
        await db.flush()
        await db.refresh(metrica)
    return metrica


async def _calc_streak_dias(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.date(AtividadeProspeccao.data_hora))
        .distinct()
        .order_by(func.date(AtividadeProspeccao.data_hora).desc())
    )
    dias_com_atividade = {row[0] for row in result.all()}
    if not dias_com_atividade:
        return 0

    hoje = date.today()
    cursor = hoje if hoje in dias_com_atividade else hoje - timedelta(days=1)
    streak = 0
    while cursor in dias_com_atividade:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


@router.get("/intencao", response_model=IntencaoOut)
async def get_intencao(db: AsyncSession = Depends(get_db)):
    hoje = date.today()
    metrica = await _get_or_create_hoje(db)

    feito_result = await db.execute(
        select(func.count())
        .select_from(AtividadeProspeccao)
        .where(func.date(AtividadeProspeccao.data_hora) == hoje)
    )
    feito_hoje = feito_result.scalar() or 0

    ultima_result = await db.execute(select(func.max(AtividadeProspeccao.data_hora)))
    ultima_atividade_em = ultima_result.scalar()

    streak_dias = await _calc_streak_dias(db)

    return IntencaoOut(
        meta_hoje=metrica.meta_atividades,
        feito_hoje=feito_hoje,
        streak_dias=streak_dias,
        ultima_atividade_em=ultima_atividade_em,
    )


@router.patch("/intencao/meta", response_model=IntencaoOut)
async def set_meta(payload: MetaUpdate, db: AsyncSession = Depends(get_db)):
    metrica = await _get_or_create_hoje(db)
    metrica.meta_atividades = payload.meta_atividades
    await db.flush()
    await db.refresh(metrica)
    return await get_intencao(db)
