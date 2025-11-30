"""
L2 Execution Layer

Provides execution orchestration for agentic workflows across
the L1-L5 architecture with task scheduling and resource management.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
import uuid


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents an executable task."""
    id: str
    name: str
    description: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ExecutionContext:
    """Context for task execution."""
    session_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None


@dataclass
class ExecutionPlan:
    """Represents an execution plan for tasks."""
    plan_id: str
    tasks: List[Task] = field(default_factory=list)
    estimated_duration: float = 0.0
    priority: int = 0
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.plan_id:
            self.plan_id = str(uuid.uuid4())


@dataclass
class ExecutionResult:
    """Represents the result of task execution."""
    execution_id: str
    status: ExecutionStatus
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.execution_id:
            self.execution_id = str(uuid.uuid4())


class ExecutionEngine:
    """Engine for executing tasks with dependency management."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.execution_queue: List[Task] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Any] = {}
        
    def add_task(self, task: Task) -> str:
        """Add a task to the execution queue."""
        self.tasks[task.id] = task
        return task.id
    
    def execute_task(self, task_id: str, context: ExecutionContext) -> Any:
        """Execute a single task."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.status = ExecutionStatus.RUNNING
        task.started_at = time.time()
        
        try:
            result = task.function(*task.args, **task.kwargs)
            task.result = result
            task.status = ExecutionStatus.COMPLETED
            task.completed_at = time.time()
            return result
        except Exception as e:
            task.error = str(e)
            task.status = ExecutionStatus.FAILED
            task.completed_at = time.time()
            raise
    
    async def execute_async(self, task_id: str, context: ExecutionContext) -> Any:
        """Execute a task asynchronously."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.execute_task, task_id, context
        )


# Global execution engine
_execution_engine: Optional[ExecutionEngine] = None


def get_execution_engine() -> ExecutionEngine:
    """Get the global execution engine instance."""
    global _execution_engine
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    return _execution_engine


__all__ = [
    "ExecutionEngine",
    "Task", 
    "ExecutionContext",
    "ExecutionStatus",
    "get_execution_engine",
]
