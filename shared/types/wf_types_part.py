"""Split module 2 for workflow_types_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class RetrievalSource:
    """Metadata about a data retrieval source."""
    id: str
    type: str
    confidence: float = 0.0
    status: str = 'UNKNOWN'
    specific_source: Optional[str] = None
