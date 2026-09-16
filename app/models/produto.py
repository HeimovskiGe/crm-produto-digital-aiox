"""Configuracao do produto/oferta do vendedor - usada pra personalizar o
roteiro dos 7 Passos (aula 3) com a proposta de valor real, nao generica.

Singleton (uma linha so, id=1).
"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ConfiguracaoProduto(Base):
    __tablename__ = "configuracao_produto"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_produto: Mapped[str | None] = mapped_column(String(200), nullable=True)
    proposta_valor: Mapped[str | None] = mapped_column(Text, nullable=True)
    dor_resolvida: Mapped[str | None] = mapped_column(Text, nullable=True)
    entregavel_1: Mapped[str | None] = mapped_column(String(300), nullable=True)
    entregavel_2: Mapped[str | None] = mapped_column(String(300), nullable=True)
    entregavel_3: Mapped[str | None] = mapped_column(String(300), nullable=True)
    faixa_preco: Mapped[str | None] = mapped_column(String(100), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
