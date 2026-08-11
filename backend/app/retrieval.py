"""Cosine similarity search over stored chunk embeddings.

Computed fresh, in-memory, on every query. Fine at this scale
(hundreds of chunks); see README for what changes at larger scale.
"""
import json

import numpy as np

from app.database import get_cursor

TOP_K = 4
MIN_SCORE = 0.35


def retrieve_relevant_chunks(query_vector: list[float], top_k: int = TOP_K) -> list[dict]:
    with get_cursor() as cursor:
        rows = cursor.execute(
            """
            SELECT chunks.item_id, chunks.text, chunks.embedding,
                   items.source_type, items.source_url
            FROM chunks
            JOIN items ON items.id = chunks.item_id
            """
        ).fetchall()

    if not rows:
        return []

    query_vec = np.array(query_vector)
    query_norm = np.linalg.norm(query_vec)

    scored = []
    for row in rows:
        chunk_vec = np.array(json.loads(row["embedding"]))
        chunk_norm = np.linalg.norm(chunk_vec)
        similarity = (
            0.0
            if query_norm == 0 or chunk_norm == 0
            else float(np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm))
        )
        scored.append(
            {
                "item_id": row["item_id"],
                "text": row["text"],
                "source_type": row["source_type"],
                "source_url": row["source_url"],
                "score": similarity,
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    relevant = [chunk for chunk in scored if chunk["score"] >= MIN_SCORE]
    return relevant[:top_k]
