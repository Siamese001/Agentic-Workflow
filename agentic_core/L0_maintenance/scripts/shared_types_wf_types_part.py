from dataclasses import dataclass
"""Split module 2 for workflow_types_types."""

import logging

_logger = logging.getLogger(__name__)


@dataclass
class RetrievalSource:
    """Metadata about a data retrieval source."""

    _id: str
    _type: str
    _confidence: float = 0.0
    _status: str = "UNKNOWN"
    _specific_source: Optional[str] = None
