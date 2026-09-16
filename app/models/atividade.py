"""AtividadeProspeccao model - substitui interaction.py.

Campos e enums definidos em
docs/architecture/prospeccao-fanatica-schema.md#atividadeprospeccao.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Canal(str, enum.Enum):
    TELEFONE = "telefone"
    PRESENCIAL = "presencial"
    EMAIL = "email"
    VENDA_SOCIAL = "venda_social"
    MENSAGEM_TEXTO = "mensagem_texto"
    REFERENCIA = "referencia"
    NETWORKING = "networking"
    INDICACAO_INTERNA = "indicacao_interna"
    FEIRA_COMERCIAL = "feira_comercial"
    CHAMADA_FRIA = "chamada_fria"


class ObjetivoContato(str, enum.Enum):
    MARCAR_REUNIAO = "marcar_reuniao"
    QUALIFICAR_INFORMACAO = "qualificar_informacao"
    FECHAR_VENDA = "fechar_venda"
    CONSTRUIR_FAMILIARIDADE = "construir_familiaridade"
    ASSENTAMENTO = "assentamento"


class ResultadoContato(str, enum.Enum):
    RESPOSTA_REFLEXO = "resposta_reflexo"
    DISPENSA = "dispensa"
    OBJECAO = "objecao"
    REUNIAO_MARCADA = "reuniao_marcada"
    VENDA_FECHADA = "venda_fechada"
    SEM_RESPOSTA = "sem_resposta"


class MotivoRecusa(str, enum.Enum):
    SEM_INTERESSE = "sem_interesse"
    SEM_ORCAMENTO = "sem_orcamento"
    OCUPADO = "ocupado"
    PEDIDO_INFO = "pedido_info"
    SOBRECARGA = "sobrecarga"
    SO_OLHANDO = "so_olhando"


class TecnicaBypass(str, enum.Enum):
    OUTRO_RAMAL = "outro_ramal"
    VENDEDOR_AJUDA_VENDEDOR = "vendedor_ajuda_vendedor"
    ENTRADA_LATERAL = "entrada_lateral"
    LIGACAO_CEDO_TARDE = "ligacao_cedo_tarde"
    BILHETE_ESCRITO = "bilhete_escrito"


# Instancia unica reaproveitada nas duas colunas (canal / canal_anterior) para
# nao duplicar o CREATE TYPE do Postgres.
canal_enum = Enum(Canal, name="canal_enum", values_callable=lambda e: [x.value for x in e])


class AtividadeProspeccao(Base):
    __tablename__ = "atividades_prospeccao"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True
    )

    canal: Mapped[Canal] = mapped_column(canal_enum, nullable=False)
    canal_anterior: Mapped[Canal | None] = mapped_column(canal_enum, nullable=True)

    objetivo_contato: Mapped[ObjetivoContato] = mapped_column(
        Enum(ObjetivoContato, name="objetivo_contato_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    resultado: Mapped[ResultadoContato | None] = mapped_column(
        Enum(ResultadoContato, name="resultado_contato_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    motivo_recusa: Mapped[MotivoRecusa | None] = mapped_column(
        Enum(MotivoRecusa, name="motivo_recusa_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    tecnica_bypass_usada: Mapped[TecnicaBypass | None] = mapped_column(
        Enum(TecnicaBypass, name="tecnica_bypass_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
