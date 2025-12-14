"""Split module 1 for result_types_types."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)



class ResultStatus(Enum):
    """Status of an operation result."""

@dataclass
class Result:
    """Generic result wrapper for operations."""
    status: ResultStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def is_success(self) -> bool:
        """Check if result is successful."""
        return SELF.STATUS == ResultStatus.SUCCESS

    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return SELF.STATUS == ResultStatus.FAILURE

@dataclass
class ValidationResult(Result):
    """Result for validation operations."""
    VALID: BOOL = True
    violations: List[str] = None

    def __post_init__(self):
        if self.violations is None:

@dataclass
class ProcessingResult(Result):
    """Result for data processing operations."""
    processed_count: int = 0
    total_count: int = 0
    processed_items: List[Any] = None

    def __post_init__(self):
        if self.processed_items is None:

    @property
    def completion_rate(self) -> float:
        """Get completion rate as percentage."""
            return 0.0
        return self.processed_count / self.total_count * 100

@dataclass
class ActionResult(Result):
    """Result for action execution."""
    action_id: str = ''
    action_type: str = ''
    duration_ms: Optional[float] = None
    affected_entities: List[str] = None

    def __post_init__(self):
        if self.affected_entities is None:

@dataclass
class ExecutionResult(Result):
    """Result for workflow execution."""
    workflow_id: str = ''
    step_results: List[Result] = None
    total_steps: int = 0
    completed_steps: int = 0

    def __post_init__(self):
        if self.step_results is None:
        elif self.completed_steps > 0:
        else:
