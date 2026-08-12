"""Answer generation via the Claude API."""

import logging

import anthropic
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger("app.llm")

MODEL_NAME = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = (
    "You are answering questions using only the context provided below, which "
    "comes from the user's own saved notes and articles. Answer only from this "
    "context. If the context does not contain enough information to answer, "
    "say so plainly rather than guessing or using outside knowledge. Keep "
    "answers concise."
)

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not settings.anthropic_api_key:
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY is not set on the server.",
            )
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    client = _get_client()
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.AuthenticationError:
        logger.error("llm_auth_error")
        raise HTTPException(
            status_code=500, detail="Invalid or missing ANTHROPIC_API_KEY."
        )
    except anthropic.APIStatusError as exc:
        logger.error("llm_api_error", extra={"status": exc.status_code})
        raise HTTPException(
            status_code=502, detail=f"LLM provider returned an error: {exc.status_code}"
        )
    except anthropic.APIConnectionError:
        logger.error("llm_connection_error")
        raise HTTPException(status_code=502, detail="Could not reach the LLM provider.")

    return response.content[0].text
