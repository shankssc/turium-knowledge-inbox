"""Pydantic request/response models."""

from pydantic import BaseModel, model_validator


class IngestRequest(BaseModel):
    text: str | None = None
    url: str | None = None

    @model_validator(mode="after")
    def exactly_one_source(self) -> "IngestRequest":
        provided = [v for v in (self.text, self.url) if v]
        if len(provided) != 1:
            raise ValueError(
                "Provide exactly one of 'text' or 'url', not both or neither."
            )
        return self


class ItemResponse(BaseModel):
    id: int
    content: str
    source_type: str
    source_url: str | None
    created_at: str


class QueryRequest(BaseModel):
    question: str

    @model_validator(mode="after")
    def non_empty_question(self) -> "QueryRequest":
        if not self.question or not self.question.strip():
            raise ValueError("Question must not be empty.")
        return self


class SourceSnippet(BaseModel):
    item_id: int
    source_type: str
    source_url: str | None
    text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
