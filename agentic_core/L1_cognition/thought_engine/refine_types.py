from typing import Any, Dict, List, Optional, Protocol, Union
from dataclasses import dataclass, field
from enum import Enum, auto

"""Types and models for message_refinement_adjust_scores."""
import logging

LOGGER = logging.getLogger(__name__)
class ExecutionStatus(Enum):
    """Enumeration for execution status states."""
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

@dataclass
class ExecutionContext:
    """Comprehensive execution context with full state tracking."""
    operation_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    metadata: Dict[str, Union[str, int, bool]] = field(default_factory=dict)

    def start(self) -> None:
        """Mark execution as started."""
        SELF.STATUS = ExecutionStatus.RUNNING
        self.start_time = time.time()
        logger.info(f'Execution started for operation: {self.operation_id}')

    def complete(self, success: bool=True, error: Optional[Exception]=None) -> None:
        """Mark execution as completed."""
        self.end_time = time.time()
        SELF.STATUS = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
        if error:
            self.error_details = {'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()}
            logger.error(f'Execution failed: {error}')
        else:
            logger.info(f'Execution completed successfully in {self.end_time - self.start_time:.2f}s')

@dataclass
class ProcessingResult:
    """Standardized result container for all operations."""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    execution_context: Optional[ExecutionContext] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)