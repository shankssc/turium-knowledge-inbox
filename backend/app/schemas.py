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
                "Provide exactly one of 'text' or 'url', not both or neither.")
        return self


class ItemResponse(BaseModel):
    id: int
    content: str
    source_type: str
    source_url: str | None
    created_at: str
