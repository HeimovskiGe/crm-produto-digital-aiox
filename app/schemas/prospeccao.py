"""Schemas do Painel de Intencao de Prospeccao."""
from datetime import datetime

from pydantic import BaseModel


class MetaUpdate(BaseModel):
    meta_atividades: int


class IntencaoOut(BaseModel):
    meta_hoje: int
    feito_hoje: int
    streak_dias: int
    ultima_atividade_em: datetime | None
