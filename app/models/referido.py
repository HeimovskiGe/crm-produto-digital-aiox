"""Referido model - Passo 6/7 da venda: pega e valida indicacoes ao vivo.

Campos definidos em docs/architecture/prospeccao-fanatica-schema.md#referido.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Referido(Base):
    __tablename__ = "referidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_origem_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True
    )

    nome_indicado: Mapped[str] = mapped_column(String(200), nullable=False)
    contato_indicado: Mapped[str] = mapped_column(String(200), nullable=False)
    mensagem_validacao_enviada: Mapped[bool] = mapped_column(default=False, nullable=False)

    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
