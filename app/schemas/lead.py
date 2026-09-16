"""Pydantic schemas para o endpoint de Leads."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.lead import NivelFamiliaridade, NivelQualificacao, PapelDecisor, PipelineStage


class LeadBase(BaseModel):
    nome: str
    empresa: str | None = None
    cargo: str | None = None
    telefone: str | None = None
    email: str | None = None
    papel_decisor: PapelDecisor | None = None
    territorio: str | None = None
    origem: str | None = None
    vertical: str | None = None
    produto_interesse: str | None = None
    sazonal: bool = False
    nome_guardiao: str | None = None
    relacionamento_guardiao: str | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    nome: str | None = None
    empresa: str | None = None
    cargo: str | None = None
    telefone: str | None = None
    email: str | None = None
    papel_decisor: PapelDecisor | None = None
    pipeline_stage: PipelineStage | None = None
    nivel_qualificacao: NivelQualificacao | None = None
    nivel_familiaridade: NivelFamiliaridade | None = None
    tentativas_contato: int | None = None
    territorio: str | None = None
    origem: str | None = None
    vertical: str | None = None
    produto_interesse: str | None = None
    sazonal: bool | None = None
    nome_guardiao: str | None = None
    relacionamento_guardiao: str | None = None
    customer_id: int | None = None


class LeadOut(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pipeline_stage: PipelineStage
    nivel_qualificacao: NivelQualificacao | None
    nivel_familiaridade: NivelFamiliaridade | None
    tentativas_contato: int
    customer_id: int | None
    created_at: datetime
    updated_at: datetime
