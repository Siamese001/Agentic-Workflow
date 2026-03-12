from pydantic import Field
from agentic_core.config.core.base_entity_config import BaseEntity
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class SourceDocument(BaseEntity):
    """
    Metadata about an original file/URL before chunking.
    """
    title: str
    source_url: str | None = None
    file_type: str = Field(default='text', pattern='^(text|pdf|markdown|html)$')
    author: str | None = None

class KnowledgeChunk(BaseEntity):
    """
    A specific slice of a document prepared for embedding.
    """
    document_id: str = Field(..., description='Parent SourceDocument ID')
    chunk_index: int = Field(..., ge=0)
    text: str
    token_count: int = Field(default=0)
