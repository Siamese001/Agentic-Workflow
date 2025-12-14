"""Types and models for lic_vector_memory."""
import logging



@dataclass
class VectorDocument:
    """Document stored in vector memory."""
    id: str
    text: str
    metadata: Dict[str, object]
    embedding: Optional[List[float]] = None
    distance: Optional[float] = None

@dataclass
class QueryResult:
    """Result from a vector memory query."""
    documents: List[VectorDocument]
    total_count: int
    query_text: str
    query_time_ms: float = 0.0

@dataclass
class MemoryStats:
    """Statistics about the vector memory store."""
    collection_name: str
    document_count: int
    persist_directory: str
