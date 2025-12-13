"""Split module 2 for workflow_types_types."""


@dataclass
class RetrievalSource:
    """Metadata about a data retrieval source."""
    id: str
    type: str
    confidence: float = 0.0
    status: str = 'UNKNOWN'
    specific_source: Optional[str] = None
