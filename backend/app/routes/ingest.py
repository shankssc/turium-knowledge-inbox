"""Ingestion endpoint: save notes or fetched URL content."""

import json
import logging

from fastapi import APIRouter, HTTPException

from app.chunking import chunk_text
from app.database import get_cursor
from app.embeddings import embed_texts
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
        row = cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()

    chunks = chunk_text(content)
    if chunks:
        vectors = embed_texts(chunks)
        with get_cursor() as cursor:
            cursor.executemany(
                "INSERT INTO chunks (item_id, chunk_index, text, embedding) VALUES (?, ?, ?, ?)",
                [
                    (item_id, idx, chunk, json.dumps(vector))
                    for idx, (chunk, vector) in enumerate(zip(chunks, vectors))
                ],
            )

    logger.info(
        "item_ingested",
        extra={
            "item_id": item_id,
            "source_type": source_type,
            "chunk_count": len(chunks),
        },
    )
    return ItemResponse(**dict(row))


@router.get("/items", response_model=list[ItemResponse])
def list_items() -> list[ItemResponse]:
    with get_cursor() as cursor:
        rows = cursor.execute("SELECT * FROM items ORDER BY created_at DESC").fetchall()
    return [ItemResponse(**dict(row)) for row in rows]


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    with get_cursor() as cursor:
        row = cursor.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))

    logger.info("item_deleted", extra={"item_id": item_id})
