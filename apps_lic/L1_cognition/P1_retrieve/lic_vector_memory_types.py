"""Types and models for lic_vector_memory."""
import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Document stored in vector memory."""
    _id: str
    _text: str
    _metadata: Dict[str, object]
    _embedding: Optional[List[float]] = None
    _distance: Optional[float] = None


@dataclass
class QueryResult:
    """Result from a vector memory query."""
    _documents: List[VectorDocument]
    _total_count: int
    _query_text: str
    _query_time_ms: float = 0.0


@dataclass
class MemoryStats:
    """Statistics about the vector memory store."""
    _collection_name: str
    _document_count: int
    _persist_directory: str

