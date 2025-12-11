"""V1 Run Result to Execution Result Adapter - Legacy compatibility adapter.

This module provides mapping between the old RunResult schema and the new
ExecutionResult schema for backward compatibility.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RunStatus(Enum):
    """Legacy run status values."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PENDING = "pending"


class ExecutionStatus(Enum):
    """New execution status values."""
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RUNNING = "running"


@dataclass
class RunResult:
    """Legacy RunResult schema."""
    run_id: str
    status: RunStatus
    output: Optional[Any] = None
    error_message: Optional[str] = None
    error_code: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """New ExecutionResult schema."""
    execution_id: str
    status: ExecutionStatus
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ResultMappingConfig:
    """Configuration for result mapping."""
    preserve_metadata: bool = True
    preserve_metrics: bool = True
    convert_timestamps: bool = True
    default_success_status: List[RunStatus] = field(default_factory=lambda: [RunStatus.SUCCESS])


class V1RunResultToExecutionResultAdapter:
    """Adapter to convert V1 RunResult to ExecutionResult."""
    
    def __init__(self, config: Optional[ResultMappingConfig] = None):
        self.config = config or ResultMappingConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def convert(self, run_result: RunResult) -> ExecutionResult:
        """Convert RunResult to ExecutionResult.
        
        Args:
            run_result: Legacy run result
            
        Returns:
            ExecutionResult: Converted execution result
        """
        self.logger.info(f"Converting RunResult {run_result.run_id} to ExecutionResult")
        
        # Map status
        execution_status = self._map_status(run_result.status)
        success = run_result.status in self.config.default_success_status
        
        # Calculate execution time
        execution_time = self._calculate_execution_time(run_result)
        
        # Create new result
        execution_result = ExecutionResult(
            execution_id=run_result.run_id,
            status=execution_status,
            success=success,
            output=run_result.output,
            error=run_result.error_message,
            exit_code=run_result.error_code,
            start_time=run_result.start_time,
            end_time=run_result.end_time,
            execution_time=execution_time,
            metadata=run_result.metadata if self.config.preserve_metadata else {},
            metrics=run_result.metrics if self.config.preserve_metrics else {}
        )
        
        return execution_result
    
    def convert_batch(self, run_results: List[RunResult]) -> List[ExecutionResult]:
        """Convert multiple RunResults.
        
        Args:
            run_results: List of legacy run results
            
        Returns:
            List[ExecutionResult]: Converted execution results
        """
        return [self.convert(result) for result in run_results]
    
    def revert(self, execution_result: ExecutionResult) -> RunResult:
        """Revert ExecutionResult back to RunResult.
        
        Args:
            execution_result: New execution result
            
        Returns:
            RunResult: Legacy run result
        """
        self.logger.info(f"Reverting ExecutionResult {execution_result.execution_id} to RunResult")
        
        # Map status back
        run_status = self._revert_status(execution_result.status)
        
        # Calculate end time if needed
        end_time = execution_result.end_time
        if execution_result.start_time and execution_result.execution_time > 0:
            end_time = execution_result.start_time.timestamp() + execution_result.execution_time
            end_time = datetime.fromtimestamp(end_time)
        
        # Create legacy result
        run_result = RunResult(
            run_id=execution_result.execution_id,
            status=run_status,
            output=execution_result.output,
            error_message=execution_result.error,
            error_code=execution_result.exit_code,
            start_time=execution_result.start_time,
            end_time=end_time,
            metadata=execution_result.metadata if self.config.preserve_metadata else {},
            metrics=execution_result.metrics if self.config.preserve_metrics else {}
        )
        
        return run_result
    
    def _map_status(self, run_status: RunStatus) -> ExecutionStatus:
        """Map legacy status to new status."""
        status_mapping = {
            RunStatus.SUCCESS: ExecutionStatus.COMPLETED,
            RunStatus.FAILURE: ExecutionStatus.FAILED,
            RunStatus.TIMEOUT: ExecutionStatus.TIMEOUT,
            RunStatus.CANCELLED: ExecutionStatus.CANCELLED,
            RunStatus.PENDING: ExecutionStatus.RUNNING
        }
        return status_mapping.get(run_status, ExecutionStatus.FAILED)
    
    def _revert_status(self, execution_status: ExecutionStatus) -> RunStatus:
        """Map new status back to legacy status."""
        status_mapping = {
            ExecutionStatus.COMPLETED: RunStatus.SUCCESS,
            ExecutionStatus.FAILED: RunStatus.FAILURE,
            ExecutionStatus.TIMEOUT: RunStatus.TIMEOUT,
            ExecutionStatus.CANCELLED: RunStatus.CANCELLED,
            ExecutionStatus.RUNNING: RunStatus.PENDING
        }
        return status_mapping.get(execution_status, RunStatus.FAILURE)
    
    def _calculate_execution_time(self, run_result: RunResult) -> float:
        """Calculate execution time from run result."""
        if run_result.start_time and run_result.end_time:
            return (run_result.end_time - run_result.start_time).total_seconds()
        return 0.0


# Factory function for easy instantiation
def create_run_result_adapter(
    preserve_metadata: bool = True,
    preserve_metrics: bool = True,
    **kwargs
) -> V1RunResultToExecutionResultAdapter:
    """Create a configured RunResult adapter."""
    config = ResultMappingConfig(
        preserve_metadata=preserve_metadata,
        preserve_metrics=preserve_metrics,
        **kwargs
    )
    return V1RunResultToExecutionResultAdapter(config)


# Convenience function for direct conversion
def convert_run_result_to_execution_result(
    run_id: str,
    status: str,
    output: Optional[Any] = None,
    error_message: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Convert legacy run result parameters to new format.
    
    Args:
        run_id: Run identifier
        status: Legacy status
        output: Optional output
        error_message: Optional error message
        **kwargs: Additional parameters
        
    Returns:
        Dict: Converted execution result
    """
    # Create legacy result
    run_result = RunResult(
        run_id=run_id,
        status=RunStatus(status),
        output=output,
        error_message=error_message,
        **kwargs
    )
    
    # Convert to new format
    adapter = create_run_result_adapter()
    execution_result = adapter.convert(run_result)
    
    return {
        "execution_id": execution_result.execution_id,
        "status": execution_result.status.value,
        "success": execution_result.success,
        "output": execution_result.output,
        "error": execution_result.error,
        "exit_code": execution_result.exit_code,
        "execution_time": execution_result.execution_time,
        "metadata": execution_result.metadata,
        "metrics": execution_result.metrics
    }
