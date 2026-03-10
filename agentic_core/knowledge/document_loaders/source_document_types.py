# Document Hierarchies for RAG
# Strategy: Track provenance (source) to allow citations later

from pydantic import Field

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
