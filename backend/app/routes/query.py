"""Query endpoint: retrieval + LLM answer generation."""
import logging

from fastapi import APIRouter

from app.embeddings import embed_texts
from app.llm import generate_answer
from app.retrieval import retrieve_relevant_chunks
from app.schemas import QueryRequest, QueryResponse, SourceSnippet

logger = logging.getLogger("app.routes.query")
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    [query_vector] = embed_texts([payload.question])
    relevant_chunks = retrieve_relevant_chunks(query_vector)

    if not relevant_chunks:
        logger.info("query_no_relevant_chunks")
        return QueryResponse(
            answer="I couldn't find anything in your saved items relevant to that question.",
            sources=[],
        )

    answer = generate_answer(
        question=payload.question,
        context_chunks=[chunk["text"] for chunk in relevant_chunks],
    )

    logger.info("query_answered", extra={"chunks_used": len(relevant_chunks)})
    return QueryResponse(
        answer=answer,
        sources=[SourceSnippet(**chunk) for chunk in relevant_chunks],
    )
