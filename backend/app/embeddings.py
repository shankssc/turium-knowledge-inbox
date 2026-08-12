"""Local, free text embeddings via sentence-transformers.

Deliberately not calling a hosted embeddings API (OpenAI, Voyage,
etc.) to keep this project cost-free to run and demo. Tradeoff:
lower embedding quality than a hosted model, and this pulls in
PyTorch as a dependency. See README for the full rationale.
"""

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger("app.embeddings")

MODEL_NAME = "all-MiniLM-L6-v2"

# Loaded once at import time, not per-request — loading this model
# takes a noticeable moment, so paying that cost on every request
# would make /ingest and /query needlessly slow.
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("embedding_model_loading", extra={"model": MODEL_NAME})
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("embedding_model_ready", extra={"model": MODEL_NAME})
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns one vector per input text."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, convert_to_numpy=True)
    return vectors.tolist()
