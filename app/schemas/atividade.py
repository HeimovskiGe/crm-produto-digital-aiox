"""Pydantic schemas para atividades de prospeccao."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.atividade import Canal, MotivoRecusa, ObjetivoContato, ResultadoContato, TecnicaBypass


class AtividadeCreate(BaseModel):
    canal: Canal
    canal_anterior: Canal | None = None
    objetivo_contato: ObjetivoContato
    resultado: ResultadoContato | None = None
    motivo_recusa: MotivoRecusa | None = None
    tecnica_bypass_usada: TecnicaBypass | None = None
    observacoes: str | None = None
    data_hora: datetime


class AtividadeOut(AtividadeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    created_at: datetime
