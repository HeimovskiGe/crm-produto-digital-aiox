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
    lead_id: int | None = None
    empresario_fonte: str | None = None
    empresario_record_id: str | None = None
    empresario_nome: str | None = None
    created_at: datetime


class AtividadeComLeadOut(AtividadeOut):
    """AtividadeOut + nome/empresa pra mostrar o card, seja de Lead ou de
    empresario cru (visao 'por dia' junta as duas pontas do funil)."""

    lead_nome: str
    lead_empresa: str | None = None


class AtividadeEmpresarioCreate(BaseModel):
    """Log de toque num empresario ainda nao promovido a Lead - 1 clique,
    sem formulario (o fluxo de prospeccao fria precisa ser rapido)."""

    fonte: str
    record_id: str
    nome: str
    canal: Canal = Canal.MENSAGEM_TEXTO
