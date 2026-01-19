from __future__ import annotations
"""Types and models for tools_routing_retry_task."""
import logging
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol, Union
Logger: Any = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Enumeration for execution status states."""
    PENDING: Any = 'pending'
    RUNNING: Any = 'running'
    SUCCESS: Any = 'success'
    FAILED: Any = 'failed'
    CANCELLED: Any = 'cancelled'

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
        self.status = ExecutionStatus.RUNNING
        self.start_time = time.time()
        LOGGER.info(f'Execution started for operation: {self.operation_id}')

    def complete(self, success: bool=True, error: Optional[Exception]=None) -> None:
        """Mark execution as completed."""
        self.end_time = time.time()
        self.status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
        if error:
            self.error_details = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
            LOGGER.error(f'Execution failed: {error}')
        else:
            LOGGER.info(f'Execution completed successfully in {self.end_time - self.start_time:.2f}s')

@dataclass
class ProcessingResult:
    """Standardized result container for all operations."""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    ExecutionContext: Optional[ExecutionContext] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
