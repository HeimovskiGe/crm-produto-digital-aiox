"""Cliente HTTP pro Supabase do pam-geh - leitura/escrita direto na fonte.

Nao migra nada pra este projeto: as 6 bases de empresarios (Prudentopolis,
Ponta Grossa, Estetica, Sao Jose, Paroquias-PR, Trafego Curitiba) continuam
no Supabase original (amsdxyoeeqszlnbozixo), acessadas via PostgREST com a
service_role key (bypassa RLS, uso server-side apenas - nunca exposta ao
navegador).
"""
import httpx

from app.config import settings

SELECT_FIELDS = (
    "id,nome_fantasia,razao_social,cnpj,cnae,telefone,whatsapp,email,"
    "municipio,uf,bairro,cep,data_abertura,status,email_status,origem,"
    "ia_tag,ia_reason,last_reply,last_reply_at,obs,email_sent_at,"
    "created_at,updated_at"
)


class PamGehClient:
    def __init__(self) -> None:
        self.base_url = settings.pamgeh_supabase_url.rstrip("/")
        self.headers = {
            "apikey": settings.pamgeh_service_role_key,
            "Authorization": f"Bearer {settings.pamgeh_service_role_key}",
            "Content-Type": "application/json",
        }

    async def list_by_status(
        self,
        table: str,
        status: str,
        limit: int,
        offset: int,
        municipio: str | None = None,
        tag: str | None = None,
        select_fields: str = SELECT_FIELDS,
    ) -> tuple[list[dict], int]:
        params = {
            "status": f"eq.{status}",
            "order": "created_at.desc",
            "select": select_fields,
            "limit": str(limit),
            "offset": str(offset),
        }
        if municipio:
            params["municipio"] = f"eq.{municipio}"
        if tag:
            params["ia_tag"] = f"eq.{tag}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self.base_url}/rest/v1/{table}",
                headers={**self.headers, "Prefer": "count=exact"},
                params=params,
            )
            resp.raise_for_status()
            content_range = resp.headers.get("content-range", "")
            total_str = content_range.split("/")[-1] if "/" in content_range else "0"
            total = int(total_str) if total_str.isdigit() else 0
            return resp.json(), total

    async def list_distinct(self, table: str, column: str) -> list[str]:
        """Valores distintos de uma coluna, pra popular selects de filtro.
        PostgREST nao tem DISTINCT nativo simples; traz a coluna sozinha
        (ate 20k linhas) e faz o distinct em Python."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self.base_url}/rest/v1/{table}",
                headers=self.headers,
                params={"select": column, "limit": "20000"},
            )
            resp.raise_for_status()
            values = {row[column] for row in resp.json() if row.get(column)}
            return sorted(values)

    async def update_status(self, table: str, record_id: str, status: str) -> None:
        await self.update_fields(table, record_id, {"status": status})

    async def update_fields(self, table: str, record_id: str, fields: dict) -> None:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.patch(
                f"{self.base_url}/rest/v1/{table}",
                headers=self.headers,
                params={"id": f"eq.{record_id}"},
                json=fields,
            )
            resp.raise_for_status()


pamgeh_client = PamGehClient()
