"""Pydantic schemas para captura de Referidos (Passo 6/7 dos 7 Passos)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReferidoCreate(BaseModel):
    nome_indicado: str
    contato_indicado: str


class ReferidoUpdate(BaseModel):
    mensagem_validacao_enviada: bool


class ReferidoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_origem_id: int
    nome_indicado: str
    contato_indicado: str
    mensagem_validacao_enviada: bool
    data_hora: datetime
