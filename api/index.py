"""Entry point for Vercel's Python serverless runtime.

Ve documentacao: https://vercel.com/docs/functions/runtimes/python
Reexporta o app ASGI existente - nenhuma logica nova aqui.
"""
from app.main import app  # noqa: F401
