"""Cliente HTTP pro Supabase do pam-geh - leitura/escrita direto na fonte.

Nao migra nada pra este projeto: as 6 bases de empresarios (Prudentopolis,
Ponta Grossa, Estetica, Sao Jose, Paroquias-PR, Trafego Curitiba) continuam
no Supabase original (amsdxyoeeqszlnbozixo), acessadas via PostgREST com a
service_role key (bypassa RLS, uso server-side apenas - nunca exposta ao
navegador).
"""
import httpx

from app.config import settings

SELECT_FIELDS = "id,nome_fantasia,razao_social,telefone,whatsapp,email,status,municipio,bairro,cnae,created_at"


class PamGehClient:
    def __init__(self) -> None:
        self.base_url = settings.pamgeh_supabase_url.rstrip("/")
        self.headers = {
            "apikey": settings.pamgeh_service_role_key,
            "Authorization": f"Bearer {settings.pamgeh_service_role_key}",
            "Content-Type": "application/json",
        }

    async def list_by_status(self, table: str, status: str, limit: int, offset: int) -> tuple[list[dict], int]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self.base_url}/rest/v1/{table}",
                headers={**self.headers, "Prefer": "count=exact"},
                params={
                    "status": f"eq.{status}",
                    "order": "created_at.desc",
                    "select": SELECT_FIELDS,
                    "limit": str(limit),
                    "offset": str(offset),
                },
            )
            resp.raise_for_status()
            content_range = resp.headers.get("content-range", "")
            total_str = content_range.split("/")[-1] if "/" in content_range else "0"
            total = int(total_str) if total_str.isdigit() else 0
            return resp.json(), total

    async def update_status(self, table: str, record_id: str, status: str) -> None:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.patch(
                f"{self.base_url}/rest/v1/{table}",
                headers=self.headers,
                params={"id": f"eq.{record_id}"},
                json={"status": status},
            )
            resp.raise_for_status()


pamgeh_client = PamGehClient()
