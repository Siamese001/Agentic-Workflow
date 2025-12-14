"""Types and models for execute_observability_execution."""

from typing import Any, Dict, List, Optional
import logging


class ObservabilityType(Enum):
    """Types of observability operations."""

class ExecutionLevel(Enum):
    """Levels of execution detail."""

@dataclass
class ObservabilityRequest:
    """Request for observability operation."""
    request_id: str
    operation_type: ObservabilityType
    target: str
    parameters: Dict[str, Any]
    execution_level: ExecutionLevel = ExecutionLevel.BASIC
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ObservabilityResult:
    """Result of observability operation."""
    request_id: str
    operation_type: ObservabilityType
    success: bool
    data: Optional[Dict[str, Any]] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    traces: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ObservabilityConfig:
    """Configuration for observability operations."""
    default_timeout: float = 10.0
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    sampling_rate: float = 1.0
