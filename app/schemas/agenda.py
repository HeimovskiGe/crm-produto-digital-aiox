"""Pydantic schemas pra integracao com Google Calendar."""
from pydantic import BaseModel


class AgendaStatus(BaseModel):
    conectado: bool


class HorarioLivre(BaseModel):
    inicio: str
    fim: str


class CriarEventoPayload(BaseModel):
    lead_id: int
    inicio: str
    fim: str


class EventoCriado(BaseModel):
    evento_id: str
    link: str | None = None
