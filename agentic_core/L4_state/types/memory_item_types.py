from typing import Any
from pydantic import BaseModel, Field, field_validator
from agentic_core.config.core.base_entity_config import BaseEntity
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class MemoryItem(BaseEntity):
    """
    Represents a single unit of semantic memory (e.g., a conversation turn, a fact).
    """
    content: str = Field(..., min_length=1, description='Text content of the memory')
    embedding: list[float] = Field(..., description='Vector representation')
    metadata: dict[str, Any] = Field(default_factory=dict, description='Filterable tags')
    score: float | None = Field(default=None, description='Similarity score (only on retrieval)')

    @field_validator('embedding')
    @classmethod
    def check_vector_integrity(cls, v: list[float]) -> list[float]:
        if not v:
            raise ValueError('Embedding vector cannot be empty')
        return v

class MemoryQuery(BaseModel):
    """
    Request object for semantic search.
    """
    vector: list[float] = Field(..., description='Query embedding')
    top_k: int = Field(default=5, ge=1, le=100)
    filter_metadata: dict[str, Any] | None = Field(default=None, description='Exact match filters')
