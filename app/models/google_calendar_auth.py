"""Credenciais OAuth do Google Calendar do vendedor - usadas pra sugerir
horarios livres reais e criar o evento da Reuniao de Venda direto na agenda.

Singleton (uma linha so, id=1). access_token/refresh_token ficam nulos ate
o vendedor conectar a conta em Configuracoes.
"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GoogleCalendarAuth(Base):
    __tablename__ = "google_calendar_auth"

    id: Mapped[int] = mapped_column(primary_key=True)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    calendar_id: Mapped[str] = mapped_column(String(200), default="primary", nullable=False)
    oauth_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
