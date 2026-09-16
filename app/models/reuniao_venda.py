"""ReuniaoVenda model - os 7 Passos da venda (aula 3, Lucas Carmo).

Campos definidos em docs/architecture/prospeccao-fanatica-schema.md#reuniaovenda.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EtapaReuniao(str, enum.Enum):
    APRESENTACAO = "apresentacao"
    CONEXAO = "conexao"
    DECISAO_IMEDIATA = "decisao_imediata"
    SHOWTIME = "showtime"
    FECHAMENTO = "fechamento"
    REFERIDOS = "referidos"
    VALIDACAO = "validacao"


class ResultadoReuniao(str, enum.Enum):
    GANHO = "ganho"
    PERDIDO = "perdido"
    EM_ANDAMENTO = "em_andamento"


class ReuniaoVenda(Base):
    __tablename__ = "reunioes_venda"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)

    etapa_atual: Mapped[EtapaReuniao] = mapped_column(
        Enum(EtapaReuniao, name="etapa_reuniao_enum", values_callable=lambda e: [x.value for x in e]),
        default=EtapaReuniao.APRESENTACAO,
        nullable=False,
    )
    di_confirmada: Mapped[bool] = mapped_column(default=False, nullable=False)
    di_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    data_hora_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_hora_fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    resultado: Mapped[ResultadoReuniao | None] = mapped_column(
        Enum(ResultadoReuniao, name="resultado_reuniao_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    valor_fechado: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
