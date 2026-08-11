"""Text chunking for the RAG pipeline.

Chunking strategy: fixed-size character windows with overlap. This is
the simplest strategy that still works reasonably well, and it's
content-agnostic (no need to detect sentence/paragraph boundaries).
The tradeoff: a chunk can cut a sentence or word in half at its edge,
which a sentence-aware splitter would avoid. For a single-user app
with informal notes and article text, that's an acceptable loss in
exchange for simplicity — see README for the full rationale.
"""

CHUNK_SIZE = 500
CHUNK_OVERLAP = 75


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        chunk = text[start: start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks
