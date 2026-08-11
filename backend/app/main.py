"""AI Knowledge Inbox - FastAPI entrypoint.

Kept intentionally thin: this file wires up the app, middleware, and
routers. Business logic lives in dedicated modules under app/.
"""
import logging

from fastapi import FastAPI

from app.database import init_db
from app.logging_config import configure_logging
from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router

configure_logging()
logger = logging.getLogger("app.main")

app = FastAPI(
    title="AI Knowledge Inbox",
    description="Save notes/URLs, ask questions over them via a simple RAG pipeline.",
    version="0.1.0",
)

app.include_router(ingest_router)
app.include_router(query_router)


@app.get("/health")
def health_check() -> dict:
    """Basic liveness check."""
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info("app_startup")
