"""Configuracao de produto/oferta - singleton, usado pra personalizar o
roteiro dos 7 Passos.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.produto import ConfiguracaoProduto
from app.schemas.produto import ProdutoOut, ProdutoUpdate

router = APIRouter(prefix="/api/produto", tags=["produto"])


async def _get_or_create(db: AsyncSession) -> ConfiguracaoProduto:
    result = await db.execute(select(ConfiguracaoProduto).where(ConfiguracaoProduto.id == 1))
    produto = result.scalar_one_or_none()
    if produto is None:
        produto = ConfiguracaoProduto(id=1)
        db.add(produto)
        await db.flush()
        await db.refresh(produto)
    return produto


@router.get("", response_model=ProdutoOut)
async def get_produto(db: AsyncSession = Depends(get_db)):
    return await _get_or_create(db)


@router.put("", response_model=ProdutoOut)
async def update_produto(payload: ProdutoUpdate, db: AsyncSession = Depends(get_db)):
    produto = await _get_or_create(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(produto, field, value)
    await db.flush()
    await db.refresh(produto)
    return produto
