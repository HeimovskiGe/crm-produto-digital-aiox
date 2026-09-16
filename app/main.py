"""CRM Produto Digital - Main Application.

Workshop AIOX Produto Digital.
Construido com FastAPI + SQLAlchemy Async + AIOX.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import init_db

# Routers (descomentar conforme implementar)
from app.routers import empresarios, health, leads, prospeccao
# from app.routers import webhooks
# from app.routers import customers
# from app.routers import orders
# from app.routers import students
# from app.routers import recovery
# from app.routers import whatsapp
# from app.routers import metrics
# from app.routers import kanban

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info(f"Starting {settings.app_name}...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="CRM para Produto Digital - Workshop AIOX",
    version="1.0.0",
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parent

# Static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Register routers
app.include_router(health.router)
app.include_router(leads.router)
app.include_router(prospeccao.router)
app.include_router(empresarios.router)
# app.include_router(webhooks.router)
# app.include_router(customers.router)
# app.include_router(orders.router)
# app.include_router(students.router)
# app.include_router(recovery.router)
# app.include_router(whatsapp.router)
# app.include_router(metrics.router)
# app.include_router(kanban.router)


@app.get("/")
async def root():
    """Dashboard page."""
    from fastapi.responses import HTMLResponse
    return HTMLResponse((BASE_DIR / "templates" / "index.html").read_text())
