"""Database configuration - SQLAlchemy Async."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

# Engine
# NullPool + statement_cache_size=0 + prepared_statement_name_func: obrigatorio
# quando o DATABASE_URL aponta para o pooler de transacao do Supabase/pgbouncer
# (porta 6543), usado em producao (Vercel serverless). statement_cache_size=0
# sozinho NAO basta: o asyncpg ainda nomeia prepared statements de forma
# sequencial ("__asyncpg_stmt_1__"), e isso colide quando o pgbouncer entrega a
# mesma conexao fisica pra sessoes diferentes. Nome unico (uuid) elimina a
# colisao. Inofensivo contra conexao direta/session pooler (usada em dev local).
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    },
)

# Session factory
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for models
class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency: get database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
