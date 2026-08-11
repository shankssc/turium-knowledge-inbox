"""Ingestion endpoint: save notes or fetched URL content."""
import logging

from fastapi import APIRouter

from app.database import get_cursor
from app.schemas import IngestRequest, ItemResponse
from app.url_fetcher import fetch_url_content

logger = logging.getLogger("app.routes.ingest")
router = APIRouter()


@router.post("/ingest", response_model=ItemResponse, status_code=201)
async def ingest(payload: IngestRequest) -> ItemResponse:
    if payload.url:
        content = await fetch_url_content(payload.url)
        source_type = "url"
        source_url = payload.url
    else:
        content = payload.text.strip()
        source_type = "note"
        source_url = None

    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO items (content, source_type, source_url) VALUES (?, ?, ?)",
            (content, source_type, source_url),
        )
        item_id = cursor.lastrowid
        row = cursor.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()

    logger.info("item_ingested", extra={
                "item_id": item_id, "source_type": source_type})
    return ItemResponse(**dict(row))


@router.get("/items", response_model=list[ItemResponse])
def list_items() -> list[ItemResponse]:
    with get_cursor() as cursor:
        rows = cursor.execute(
            "SELECT * FROM items ORDER BY created_at DESC").fetchall()
    return [ItemResponse(**dict(row)) for row in rows]
