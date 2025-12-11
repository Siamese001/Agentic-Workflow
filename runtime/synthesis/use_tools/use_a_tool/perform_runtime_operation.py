"""Perform Runtime Operation - Runtime operation execution adapter.

This module provides adapters for executing runtime operations with proper
error handling, logging, and resource management.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum
import asyncio
import traceback

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of runtime operations."""
    COMPUTE = "compute"
    IO = "io"
    NETWORK = "network"
    MEMORY = "memory"
    CUSTOM = "custom"


class OperationStatus(Enum):
    """Status of runtime operations."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OperationRequest:
    """Request for runtime operation."""
    operation_id: str
    operation_type: OperationType
    parameters: Dict[str, Any]
    timeout: Optional[float] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationResult:
    """Result of runtime operation."""
    operation_id: str
    status: OperationStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeConfig:
    """Configuration for runtime operations."""
    default_timeout: float = 30.0
    max_retries: int = 3
    enable_async: bool = True
    log_operations: bool = True
    resource_limits: Dict[str, Any] = field(default_factory=dict)


class RuntimeOperationAdapter:
    """Main adapter for runtime operations."""

    def __init__(self, config: Optional[RuntimeConfig] = None):
        self.config = config or RuntimeConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._operation_handlers: Dict[OperationType, Callable] = {}
        self._running_operations: Dict[str, asyncio.Task] = {}
        self._initialize_handlers()

    def register_handler(self, operation_type: OperationType, 
                        handler: Callable) -> None:
        """Register a handler for operation type.
        
        Args:
            operation_type: Type of operation
            handler: Handler function
        """
        self._operation_handlers[operation_type] = handler
        self.logger.info(f"Registered handler for {operation_type.value}")

    def execute_operation(self, request: OperationRequest) -> OperationResult:
        """Execute a runtime operation.
        
        Args:
            request: Operation request
            
        Returns:
            OperationResult: Result of operation
        """
        self.logger.info(f"Executing operation: {request.operation_id}")
        
        try:
            start_time = datetime.utcnow()
            
            # Get handler for operation type
            handler = self._operation_handlers.get(request.operation_type)
            if not handler:
                return OperationResult(
                    operation_id=request.operation_id,
                    status=OperationStatus.FAILED,
                    error=f"No handler for operation type: {request.operation_type.value}"
                )
            
            # Execute operation
            if self.config.enable_async:
                result = self._execute_async(handler, request)
            else:
                result = self._execute_sync(handler, request)
            
            # Calculate execution time
            end_time = datetime.utcnow()
            result.execution_time = (end_time - start_time).total_seconds()
            
            # Log operation if configured
            if self.config.log_operations:
                self._log_operation(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Operation execution failed: {str(e)}")
            return OperationResult(
                operation_id=request.operation_id,
                status=OperationStatus.FAILED,
                error=str(e),
                metadata={"traceback": traceback.format_exc()}
            )

    def execute_operation_async(self, request: OperationRequest) -> asyncio.Task:
        """Execute operation asynchronously.
        
        Args:
            request: Operation request
            
        Returns:
            asyncio.Task: Async task for operation
        """
        async def _async_wrapper():
            return self.execute_operation(request)
        
        task = asyncio.create_task(_async_wrapper())
        self._running_operations[request.operation_id] = task
        return task

    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a running operation.
        
        Args:
            operation_id: ID of operation to cancel
            
        Returns:
            bool: True if cancelled successfully
        """
        if operation_id in self._running_operations:
            task = self._running_operations[operation_id]
            task.cancel()
            del self._running_operations[operation_id]
            self.logger.info(f"Cancelled operation: {operation_id}")
            return True
        return False

    def get_operation_status(self, operation_id: str) -> Optional[OperationStatus]:
        """Get status of running operation.
        
        Args:
            operation_id: ID of operation
            
        Returns:
            Optional[OperationStatus]: Current status
        """
        if operation_id in self._running_operations:
            task = self._running_operations[operation_id]
            if task.done():
                if task.cancelled():
                    return OperationStatus.CANCELLED
                elif task.exception():
                    return OperationStatus.FAILED
                else:
                    return OperationStatus.COMPLETED
            else:
                return OperationStatus.RUNNING
        return None

    def batch_execute(self, requests: List[OperationRequest]) -> List[OperationResult]:
        """Execute multiple operations.
        
        Args:
            requests: List of operation requests
            
        Returns:
            List[OperationResult]: Results for all operations
        """
        results = []
        
        for request in requests:
            result = self.execute_operation(request)
            results.append(result)
        
        return results

    def _execute_sync(self, handler: Callable, request: OperationRequest) -> OperationResult:
        """Execute operation synchronously."""
        try:
            result = handler(request.parameters)
            return OperationResult(
                operation_id=request.operation_id,
                status=OperationStatus.COMPLETED,
                result=result
            )
        except Exception as e:
            return OperationResult(
                operation_id=request.operation_id,
                status=OperationStatus.FAILED,
                error=str(e)
            )

    def _execute_async(self, handler: Callable, request: OperationRequest) -> OperationResult:
        """Execute operation asynchronously."""
        try:
            if asyncio.iscoroutinefunction(handler):
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(handler(request.parameters))
            else:
                result = handler(request.parameters)
            
            return OperationResult(
                operation_id=request.operation_id,
                status=OperationStatus.COMPLETED,
                result=result
            )
        except Exception as e:
            return OperationResult(
                operation_id=request.operation_id,
                status=OperationStatus.FAILED,
                error=str(e)
            )

    def _log_operation(self, request: OperationRequest, result: OperationResult) -> None:
        """Log operation details."""
        log_data = {
            "operation_id": request.operation_id,
            "type": request.operation_type.value,
            "status": result.status.value,
            "execution_time": result.execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if result.error:
            log_data["error"] = result.error
        
        self.logger.info(f"Operation completed: {log_data}")

    def _initialize_handlers(self) -> None:
        """Initialize default operation handlers."""
        # Compute operation handler
        def _compute_handler(params: Dict[str, Any]) -> Any:
            operation = params.get("operation")
            operands = params.get("operands", [])
            
            if operation == "add":
                return sum(operands)
            elif operation == "multiply":
                result = 1
                for op in operands:
                    result *= op
                return result
            elif operation == "process":
                # Generic processing
                data = params.get("data")
                if isinstance(data, list):
                    return [x * 2 for x in data]
                return data
            
            raise ValueError(f"Unknown compute operation: {operation}")
        
        # IO operation handler
        def _io_handler(params: Dict[str, Any]) -> Any:
            operation = params.get("operation")
            path = params.get("path")
            
            if operation == "read":
                # Simulate file read
                return {"content": f"Mock content from {path}", "size": 1024}
            elif operation == "write":
                # Simulate file write
                content = params.get("content")
                return {"bytes_written": len(str(content))}
            
            raise ValueError(f"Unknown IO operation: {operation}")
        
        # Network operation handler
        def _network_handler(params: Dict[str, Any]) -> Any:
            operation = params.get("operation")
            url = params.get("url")
            
            if operation == "fetch":
                # Simulate network fetch
                return {"status": 200, "data": f"Mock response from {url}"}
            elif operation == "post":
                # Simulate network post
                data = params.get("data")
                return {"status": 201, "response": "Created"}
            
            raise ValueError(f"Unknown network operation: {operation}")
        
        # Register default handlers
        self.register_handler(OperationType.COMPUTE, _compute_handler)
        self.register_handler(OperationType.IO, _io_handler)
        self.register_handler(OperationType.NETWORK, _network_handler)


# Factory function for easy instantiation
def create_runtime_operation_adapter(
    default_timeout: float = 30.0,
    max_retries: int = 3,
    enable_async: bool = True,
    **kwargs
) -> RuntimeOperationAdapter:
    """Create a configured runtime operation adapter."""
    config = RuntimeConfig(
        default_timeout=default_timeout,
        max_retries=max_retries,
        enable_async=enable_async,
        **kwargs
    )
    return RuntimeOperationAdapter(config)


# Convenience function for direct usage
def perform_runtime_operation(
    operation_id: str,
    operation_type: str,
    parameters: Dict[str, Any],
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """Perform a runtime operation.
    
    Args:
        operation_id: Unique operation identifier
        operation_type: Type of operation to perform
        parameters: Operation parameters
        timeout: Optional timeout in seconds
        
    Returns:
        Dict: Operation result
    """
    adapter = create_runtime_operation_adapter()
    
    request = OperationRequest(
        operation_id=operation_id,
        operation_type=OperationType(operation_type),
        parameters=parameters,
        timeout=timeout
    )
    
    result = adapter.execute_operation(request)
    
    return {
        "operation_id": result.operation_id,
        "status": result.status.value,
        "result": result.result,
        "error": result.error,
        "execution_time": result.execution_time,
        "metadata": result.metadata
    }
