# Document Hierarchies for RAG
# Strategy: Track provenance (source) to allow citations later

from pydantic import Field
from agentic_core.domain.entities import BaseEntity


class SourceDocument(BaseEntity):
    """
    Metadata about an original file/URL before chunking.
    """

    title: str
    source_url: str | None = None
    file_type: str = Field(default="text", pattern=r"^(text|pdf|markdown|html)$")
    author: str | None = None


class KnowledgeChunk(BaseEntity):
    """
    A specific slice of a document prepared for embedding.
    """

    document_id: str = Field(..., description="Parent SourceDocument ID")
    chunk_index: int = Field(..., ge=0)
    text: str
    token_count: int = Field(default=0)
