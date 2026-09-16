"""Schema da configuracao de produto/oferta."""
from pydantic import BaseModel, ConfigDict


class ProdutoUpdate(BaseModel):
    nome_produto: str | None = None
    proposta_valor: str | None = None
    dor_resolvida: str | None = None
    entregavel_1: str | None = None
    entregavel_2: str | None = None
    entregavel_3: str | None = None
    faixa_preco: str | None = None


class ProdutoOut(ProdutoUpdate):
    model_config = ConfigDict(from_attributes=True)
