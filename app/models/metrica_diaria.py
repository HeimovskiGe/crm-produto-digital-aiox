"""MetricaDiaria model - Eficiencia + Eficacia = Desempenho.

Campos definidos em docs/architecture/prospeccao-fanatica-schema.md#metricadiaria.
"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MetricaDiaria(Base):
    __tablename__ = "metricas_diarias"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[date] = mapped_column(Date, unique=True, nullable=False)

    # Meta pessoal do vendedor pro dia (Painel de Intencao de Prospeccao,
    # aula 2 - formula de proporcao pessoal, ex: 150 prospeccoes/dia).
    meta_atividades: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    ligacoes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contatos_efetivos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_enviados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    respostas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reunioes_agendadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vendas_fechadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    acoes_sociais: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mensagens_texto_enviadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    novos_dados_coletados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
