"""
Task execution engine for the agentic runtime.

Provides high-level task execution with model invocation, context management,
and resource monitoring integrated with the budget management system.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, UTC
import logging
import time
import uuid

from .runtime_utils import ModelExecutor, SandboxConfig, ModelInvocationResult
from .execution_budget_manager import get_budget_manager, BudgetLimits

logger = logging.getLogger(__name__)


@dataclass
class TaskExecutionContext:
    """Context for task execution with metadata and constraints."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    task_type: str = "general"
    priority: str = "normal"  # low, normal, high, critical
    timeout_seconds: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class TaskExecutionResult:
    """Result of task execution with comprehensive metadata."""
    task_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    budget_consumed: Optional[float] = None
    context: Optional[TaskExecutionContext] = None
    model_invocations: List[ModelInvocationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class TaskExecutor:
    """
    High-level task execution engine with model invocation and budget management.
    
    Integrates model execution with budget constraints, context management,
    and comprehensive monitoring for agentic workflows.
    """

    def __init__(self, default_config: Optional[SandboxConfig] = None):
        """Initialize task executor with model configuration."""
        self.model_executor = ModelExecutor(default_config)
        self.budget_manager = get_budget_manager()
        self.execution_history: List[TaskExecutionResult] = []
        self.max_history = 100

    def execute_task(
        self,
        task: Dict[str, Any],
        context: Optional[TaskExecutionContext] = None,
        model_config: Optional[SandboxConfig] = None,
        **kwargs
    ) -> TaskExecutionResult:
        """
        Execute a task with model invocation and budget management.

        Args:
            task: Task specification with model, prompt, and parameters
            context: Execution context with metadata and constraints
            model_config: Sandbox configuration for model execution
            **kwargs: Additional execution parameters

        Returns:
            TaskExecutionResult with comprehensive execution metadata
        """
        # Initialize context if not provided
        execution_context = context or TaskExecutionContext()
        start_time = time.time()

        try:
            # Extract task parameters
            model = task.get("model", "gpt-3.5-turbo")
            prompt = task.get("prompt", "")
            task_type = task.get("task_type", "general")

            # Update context
            execution_context.task_type = task_type

            # Check budget constraints
            budget_limits = BudgetLimits(
                max_tokens=task.get("max_tokens", 1000),
                max_cost=task.get("max_cost", 0.10),
                timeout_seconds=execution_context.timeout_seconds
            )

            if not self.budget_manager.check_budget(execution_context.task_id, budget_limits):
                raise ValueError("Task exceeds budget limits")

            # Execute model invocation
            model_result = self.model_executor.invoke_model(
                model=model,
                prompt=prompt,
                config=model_config,
                **kwargs
            )

            # Update budget consumption
            budget_consumed = self.budget_manager.consume_budget(
                execution_context.task_id,
                model_result.tokens_used or 0,
                model_result.execution_time_ms or 0
            )

            # Create execution result
            execution_time_ms = (time.time() - start_time) * 1000

            result = TaskExecutionResult(
                task_id=execution_context.task_id,
                success=True,
                result=model_result.content,
                execution_time_ms=execution_time_ms,
                tokens_used=model_result.tokens_used,
                budget_consumed=budget_consumed,
                context=execution_context,
                model_invocations=[model_result],
                metadata={
                    "model": model,
                    "task_type": task_type,
                    "sandbox_used": model_result.sandbox_used,
                    "invocation_id": model_result.invocation_id
                }
            )

            # Store in history
            self._add_to_history(result)

            logger.info(f"Task executed successfully: {execution_context.task_id}, "
                       f"tokens: {model_result.tokens_used}, time: {execution_time_ms:.2f}ms")

            return result

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Task execution failed: {str(e)}"

            logger.error(f"Task execution failed: {execution_context.task_id}, error: {str(e)}")

            # Create error result
            result = TaskExecutionResult(
                task_id=execution_context.task_id,
                success=False,
                result=None,
                error=error_msg,
                execution_time_ms=execution_time_ms,
                context=execution_context,
                metadata={"error_type": type(e).__name__}
            )

            self._add_to_history(result)
            return result

    def execute_batch_tasks(
        self,
        tasks: List[Dict[str, Any]],
        context: Optional[TaskExecutionContext] = None,
        model_config: Optional[SandboxConfig] = None
    ) -> List[TaskExecutionResult]:
        """
        Execute multiple tasks in batch with shared context and budget management.

        Args:
            tasks: List of task specifications
            context: Shared execution context
            model_config: Model configuration for all tasks

        Returns:
            List of TaskExecutionResult objects
        """
        results = []
        batch_context = context or TaskExecutionContext()
        
        # Update context for batch execution
        batch_context.metadata["batch_size"] = len(tasks)
        batch_context.metadata["batch_execution"] = True

        for i, task in enumerate(tasks):
            # Create individual context for each task in batch
            task_context = TaskExecutionContext(
                user_id=batch_context.user_id,
                session_id=batch_context.session_id,
                task_type=task.get("task_type", "batch_item"),
                priority=batch_context.priority,
                timeout_seconds=batch_context.timeout_seconds,
                metadata={
                    **batch_context.metadata,
                    "batch_index": i,
                    "batch_id": batch_context.task_id
                }
            )

            result = self.execute_task(task, task_context, model_config)
            results.append(result)

        return results

    def _add_to_history(self, result: TaskExecutionResult) -> None:
        """Add execution result to history."""
        self.execution_history.append(result)
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics."""
        if not self.execution_history:
            return {"total_tasks": 0}

        total_tasks = len(self.execution_history)
        successful_tasks = sum(1 for r in self.execution_history if r.success)
        total_tokens = sum(r.tokens_used or 0 for r in self.execution_history)
        total_budget = sum(r.budget_consumed or 0 for r in self.execution_history)
        avg_time = sum(r.execution_time_ms or 0 for r in self.execution_history) / total_tasks

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "total_tokens_used": total_tokens,
            "total_budget_consumed": total_budget,
            "average_execution_time_ms": avg_time,
            "last_execution": self.execution_history[-1].timestamp.isoformat() if self.execution_history else None
        }

    def get_task_history(self, limit: Optional[int] = None) -> List[TaskExecutionResult]:
        """Get execution history with optional limit."""
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history.copy()

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()


# Global task executor instance
_task_executor = TaskExecutor()


def execute_task(
    task: Dict[str, Any],
    context: Optional[TaskExecutionContext] = None,
    model_config: Optional[SandboxConfig] = None,
    **kwargs
) -> TaskExecutionResult:
    """
    Execute a task using the global task executor.

    This is the main entry point for task execution used throughout the system.

    Args:
        task: Task specification with model, prompt, and parameters
        context: Execution context with metadata and constraints
        model_config: Model sandbox configuration
        **kwargs: Additional execution parameters

    Returns:
        TaskExecutionResult with comprehensive execution metadata
    """
    return _task_executor.execute_task(task, context, model_config, **kwargs)


def get_task_executor() -> TaskExecutor:
    """Get the global task executor instance."""
    return _task_executor


def configure_task_executor(config: SandboxConfig) -> None:
    """Configure the global task executor with new default settings."""
    global _task_executor
    _task_executor = TaskExecutor(config)


__all__ = [
    "TaskExecutionContext",
    "TaskExecutionResult", 
    "TaskExecutor",
    "execute_task",
    "get_task_executor",
    "configure_task_executor"
]
