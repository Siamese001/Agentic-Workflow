"""V1 Processor to Executor Adapter - Legacy compatibility adapter.

This module provides compatibility between the old Processor class and the new
Executor interface, ensuring backward compatibility for external systems.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessorType(Enum):
    """Legacy processor types."""
    BATCH = "batch"
    STREAMING = "streaming"
    REAL_TIME = "real_time"


@dataclass
class ProcessorConfig:
    """Legacy processor configuration."""
    processor_id: str
    processor_type: ProcessorType
    max_concurrent_tasks: int = 10
    timeout: float = 30.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessorTask:
    """Legacy processor task definition."""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ProcessorResult:
    """Legacy processor result."""
    task_id: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0


class Processor:
    """Legacy Processor class for backward compatibility."""
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._active_tasks: Dict[str, Dict[str, Any]] = {}
        self._completed_tasks: List[ProcessorResult] = []
    
    def process(self, task: ProcessorTask) -> ProcessorResult:
        """Process a single task.
        
        Args:
            task: Task to process
            
        Returns:
            ProcessorResult: Processing result
        """
        self.logger.info(f"Processing task: {task.task_id}")
        
        # In new system, this would delegate to Executor
        # For compatibility, we maintain the old interface
        return self._execute_task(task)
    
    def process_batch(self, tasks: List[ProcessorTask]) -> List[ProcessorResult]:
        """Process multiple tasks.
        
        Args:
            tasks: List of tasks to process
            
        Returns:
            List[ProcessorResult]: Results for all tasks
        """
        results = []
        
        for task in tasks:
            result = self.process(task)
            results.append(result)
        
        return results
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Optional[Dict]: Task status
        """
        return self._active_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            bool: True if cancelled successfully
        """
        if task_id in self._active_tasks:
            self._active_tasks[task_id]["cancelled"] = True
            return True
        return False
    
    def _execute_task(self, task: ProcessorTask) -> ProcessorResult:
        """Execute task with legacy compatibility."""
        # Placeholder implementation
        return ProcessorResult(
            task_id=task.task_id,
            success=True,
            output={"processed": True},
            processing_time=0.1
        )


class V1ProcessorToExecutorAdapter:
    """Adapter to bridge V1 Processor to new Executor interface."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._processor_registry: Dict[str, Processor] = {}
    
    def create_processor(self, config: ProcessorConfig) -> Processor:
        """Create a processor instance.
        
        Args:
            config: Processor configuration
            
        Returns:
            Processor: Processor instance
        """
        processor = Processor(config)
        self._processor_registry[config.processor_id] = processor
        return processor
    
    def adapt_to_executor(self, processor: Processor) -> 'Executor':
        """Adapt processor to new Executor interface.
        
        Args:
            processor: Legacy processor
            
        Returns:
            Executor: New executor interface
        """
        return ExecutorAdapter(processor)
    
    def migrate_processor(self, processor_id: str) -> Optional['Executor']:
        """Migrate processor to new system.
        
        Args:
            processor_id: Processor identifier
            
        Returns:
            Optional[Executor]: Migrated executor
        """
        processor = self._processor_registry.get(processor_id)
        if processor:
            return self.adapt_to_executor(processor)
        return None


class ExecutorAdapter:
    """Executor interface wrapping legacy Processor."""
    
    def __init__(self, processor: Processor):
        self.processor = processor
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def execute(self, request: 'ExecutionRequest') -> 'ExecutionResult':
        """Execute using new interface.
        
        Args:
            request: Execution request
            
        Returns:
            ExecutionResult: Execution result
        """
        # Convert new request to legacy task
        task = ProcessorTask(
            task_id=request.request_id,
            task_type=request.operation_type,
            parameters=request.parameters
        )
        
        # Execute with legacy processor
        result = self.processor.process(task)
        
        # Convert back to new result format
        return ExecutionResult(
            request_id=result.task_id,
            success=result.success,
            output=result.output,
            error=result.error,
            execution_time=result.processing_time
        )


# Forward declarations for new interface
@dataclass
class ExecutionRequest:
    """New execution request interface."""
    request_id: str
    operation_type: str
    parameters: Dict[str, Any]


@dataclass
class ExecutionResult:
    """New execution result interface."""
    request_id: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class Executor:
    """New executor interface."""
    pass


# Factory function for easy instantiation
def create_processor_adapter() -> V1ProcessorToExecutorAdapter:
    """Create a processor to executor adapter."""
    return V1ProcessorToExecutorAdapter()


# Convenience function for backward compatibility
def create_legacy_processor(processor_id: str, 
                           processor_type: str = "batch",
                           **kwargs) -> Processor:
    """Create a legacy processor.
    
    Args:
        processor_id: Processor identifier
        processor_type: Type of processor
        **kwargs: Additional configuration
        
    Returns:
        Processor: Legacy processor instance
    """
    config = ProcessorConfig(
        processor_id=processor_id,
        processor_type=ProcessorType(processor_type),
        **kwargs
    )
    
    adapter = create_processor_adapter()
    return adapter.create_processor(config)
