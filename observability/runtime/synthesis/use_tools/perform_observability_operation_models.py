"""Dataclass models for perform_observability_operation."""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
# from .perform_observability_operation_enums import *  # Star import removed

@dataclass
class OperationContext:
    """Context for observability operation."""
    operation_id: str
    category: OperationCategory
    scope: OperationScope
    target: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OperationParameters:
    """Parameters for observability operation."""
    operation_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    aggregation: Optional[str] = None
    time_range: Optional[Tuple[datetime, datetime]] = None
    limit: Optional[int] = None

@dataclass
class OperationConfig:
    """Configuration for operation execution."""
    timeout: float = 30.0
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl: float = 300.0
    enable_compression: bool = False

@dataclass
class OperationOutcome:
    """Outcome of observability operation."""
    operation_id: str
    success: bool
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    count: int = 0
    aggregated_values: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
