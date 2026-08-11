"""AI Knowledge Inbox - FastAPI entrypoint.

Kept intentionally thin: this file wires up the app, middleware, and
routers. Business logic lives in dedicated modules under app/.
"""
import logging

from fastapi import FastAPI

from app.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("app.main")

app = FastAPI(
    title="AI Knowledge Inbox",
    description="Save notes/URLs, ask questions over them via a simple RAG pipeline.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    """Basic liveness check."""
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    logger.info("app_startup")
