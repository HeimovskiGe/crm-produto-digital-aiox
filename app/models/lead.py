"""Lead model - Piramide da Prospeccao.

Campos e enums definidos em docs/architecture/prospeccao-fanatica-schema.md#lead.
"""
import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PapelDecisor(str, enum.Enum):
    DECISOR = "decisor"
    INFLUENCIADOR = "influenciador"
    USUARIO = "usuario"


class PipelineStage(str, enum.Enum):
    BASE_NAO_VERIFICADO = "base_nao_verificado"
    INFORMACAO_SOLIDA = "informacao_solida"
    JANELA_IDENTIFICADA = "janela_identificada"
    CONQUISTA_PRIORITARIA = "conquista_prioritaria"
    INDICACAO_QUENTE = "indicacao_quente"
    QUALIFICADO_PRONTO = "qualificado_pronto"


class NivelQualificacao(str, enum.Enum):
    NAO_QUALIFICADO = "nao_qualificado"
    SEMIQUALIFICADO = "semiqualificado"
    QUALIFICADO_SEM_JANELA = "qualificado_sem_janela"
    QUALIFICADO_NA_JANELA = "qualificado_na_janela"


class NivelFamiliaridade(str, enum.Enum):
    INATIVO = "inativo"
    FAMILIAR_NA_JANELA = "familiar_na_janela"
    FAMILIAR_FORA_JANELA = "familiar_fora_janela"
    INDICACAO_QUENTE = "indicacao_quente"
    POUCA_FAMILIARIDADE = "pouca_familiaridade"
    FRIO = "frio"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    empresa: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)

    papel_decisor: Mapped[PapelDecisor | None] = mapped_column(
        Enum(PapelDecisor, name="papel_decisor_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    pipeline_stage: Mapped[PipelineStage] = mapped_column(
        Enum(PipelineStage, name="pipeline_stage_enum", values_callable=lambda e: [x.value for x in e]),
        default=PipelineStage.BASE_NAO_VERIFICADO,
        nullable=False,
    )
    nivel_qualificacao: Mapped[NivelQualificacao | None] = mapped_column(
        Enum(NivelQualificacao, name="nivel_qualificacao_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    nivel_familiaridade: Mapped[NivelFamiliaridade | None] = mapped_column(
        Enum(NivelFamiliaridade, name="nivel_familiaridade_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    tentativas_contato: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    territorio: Mapped[str | None] = mapped_column(String(200), nullable=True)
    origem: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vertical: Mapped[str | None] = mapped_column(String(200), nullable=True)
    produto_interesse: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sazonal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    nome_guardiao: Mapped[str | None] = mapped_column(String(200), nullable=True)
    relacionamento_guardiao: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Referencia logica para customers.id (modulo pos-venda Kiwify).
    # NAO e uma ForeignKey de verdade: o model Customer ainda nao existe neste
    # projeto (fora de escopo desta story, ver AC 8). Vira FK real numa migration
    # futura quando o modulo pos-venda for implementado.
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
