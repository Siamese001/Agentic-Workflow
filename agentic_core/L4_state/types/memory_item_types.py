# Core Data Models for Semantic Memory
# Validation: Enforces vector consistency and metadata schemas

from typing import Any

from pydantic import BaseModel, Field, field_validator

from agentic_core.config.core.base_entity_config import BaseEntity


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class MemoryItem(BaseEntity):
    """
    Represents a single unit of semantic memory (e.g., a conversation turn, a fact).
    """

    content: str = Field(..., min_length=1, description="Text content of the memory")
    embedding: list[float] = Field(..., description="Vector representation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Filterable tags")
    score: float | None = Field(default=None, description="Similarity score (only on retrieval)")

    @field_validator("embedding")
    @classmethod
    def check_vector_integrity(cls, v: list[float]) -> list[float]:
        if not v:
            raise ValueError("Embedding vector cannot be empty")
        # In a real app, we would validate dimensions against Config here.
        # For now, we ensure it contains floats.
        return v


class MemoryQuery(BaseModel):
    """
    Request object for semantic search.
    """

    vector: list[float] = Field(..., description="Query embedding")
    top_k: int = Field(default=5, ge=1, le=100)
    filter_metadata: dict[str, Any] | None = Field(default=None, description="Exact match filters")
