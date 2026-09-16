"""Schemas de ReuniaoVenda (os 7 Passos, aula 3)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.reuniao_venda import EtapaReuniao, ResultadoReuniao


class ReuniaoVendaUpdate(BaseModel):
    etapa_atual: EtapaReuniao | None = None
    di_confirmada: bool | None = None
    resultado: ResultadoReuniao | None = None
    valor_fechado: float | None = None
    data_hora_fim: datetime | None = None


class ReuniaoVendaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    etapa_atual: EtapaReuniao
    di_confirmada: bool
    di_timestamp: datetime | None
    data_hora_inicio: datetime
    data_hora_fim: datetime | None
    resultado: ResultadoReuniao | None
    valor_fechado: float | None
