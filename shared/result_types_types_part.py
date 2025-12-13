"""Split module 1 for result_types_types."""

from typing import Any, Dict, List, Optional
from enum import Enum

class ResultStatus(Enum):
    """Status of an operation result."""
    SUCCESS = 'success'
    FAILURE = 'failure'
    PARTIAL = 'partial'
    PENDING = 'pending'

@dataclass
class Result:
    """Generic result wrapper for operations."""
    status: ResultStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def is_success(self) -> bool:
        """Check if result is successful."""
        return self.status == ResultStatus.SUCCESS

    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return self.status == ResultStatus.FAILURE

@dataclass
class ValidationResult(Result):
    """Result for validation operations."""
    valid: bool = True
    violations: List[str] = None

    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        self.valid = len(self.violations) == 0
        if not self.valid and self.status == ResultStatus.SUCCESS:
            self.status = ResultStatus.FAILURE

@dataclass
class ProcessingResult(Result):
    """Result for data processing operations."""
    processed_count: int = 0
    total_count: int = 0
    processed_items: List[Any] = None

    def __post_init__(self):
        if self.processed_items is None:
            self.processed_items = []

    @property
    def completion_rate(self) -> float:
        """Get completion rate as percentage."""
        if self.total_count == 0:
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
            self.affected_entities = []

@dataclass
class ExecutionResult(Result):
    """Result for workflow execution."""
    workflow_id: str = ''
    step_results: List[Result] = None
    total_steps: int = 0
    completed_steps: int = 0

    def __post_init__(self):
        if self.step_results is None:
            self.step_results = []
        self.completed_steps = len([r for r in self.step_results if r.is_success()])
        if self.completed_steps == self.total_steps and self.total_steps > 0:
            self.status = ResultStatus.SUCCESS
        elif self.completed_steps > 0:
            self.status = ResultStatus.PARTIAL
        else:
            self.status = ResultStatus.FAILURE
