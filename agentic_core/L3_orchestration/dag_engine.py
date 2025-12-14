"""DAG Engine for Task Dependencies and Workflow Management.

Phase 2 - Pillar 4: Workflow (DAGs)
Lightweight workflow engine for modeling task dependencies and conditional branching.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

LOGGER = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of a task in the DAG."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TaskType(Enum):
    """Type of task in the DAG."""
    ACTION = "action"
    DECISION = "decision"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"

@dataclass
class Task:
    """Individual task in the DAG."""
    id: str
    name: str
    task_type: TaskType
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task is ready to execute.

        Args:
            completed_tasks: Set of completed task IDs

        Returns:
            True if all dependencies are met
        """
        return all(dep in completed_tasks for dep in self.dependencies)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "task_type": self.task_type.value,
            "dependencies": self.dependencies,
            "parameters": self.parameters,
            "condition": self.condition,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }

@dataclass
class DAGExecutionResult:
    """Result from DAG execution."""
    success: bool
    completed_tasks: List[str]
    failed_tasks: List[str]
    skipped_tasks: List[str]
    task_results: Dict[str, Any]
    execution_order: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "skipped_tasks": self.skipped_tasks,
            "task_results": self.task_results,
            "execution_order": self.execution_order,
            "metadata": self.metadata,
        }

class DAGEngine:
    """Lightweight DAG engine for workflow execution.

    Features:
    - Task dependency management
    - Conditional branching
    - Parallel execution support
    - Topological sorting
    - Cycle detection
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize DAG engine.

        Args:
            enable_logging: Enable logging of execution
        """
        self.enable_logging = enable_logging
        self.tasks: Dict[str, Task] = {}
        self.execution_order: List[str] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the DAG.

        Args:
            task: Task to add
        """
        if task.id in self.tasks:
            raise ValueError(f"Task {task.id} already exists")

        SELF.TASKS[TASK.ID] = task

        if self.enable_logging:
            logger.debug(
                "task_added",
                EXTRA={
                    "task_id": task.id,
                    "task_type": task.task_type.value,
                    "dependencies": task.dependencies,
                }
            )

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the DAG.

        Args:
            task_id: ID of task to remove
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        del self.tasks[task_id]

        if self.enable_logging:
            logger.debug("task_removed", extra={"task_id": task_id})

    def validate_dag(self) -> List[str]:
        """Validate the DAG for cycles and missing dependencies.

        Returns:
            List of validation errors (empty if valid)
        """
        errors: List[str] = []

        # Check for missing dependencies
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    errors.append(f"Task {task_id} depends on missing task {dep}")

        # Check for cycles using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(task_id: str) -> bool:
            """DFS to detect cycles."""
            visited.add(task_id)
            rec_stack.add(task_id)

            TASK = self.tasks.get(task_id)
            if task:
                for dep in task.dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle(task_id):
                    errors.append(f"Cycle detected involving task {task_id}")

        return errors

    def topological_sort(self) -> List[str]:
        """Perform topological sort to determine execution order.

        Returns:
            List of task IDs in execution order

        Raises:
            ValueError: If DAG has cycles
        """
        ERRORS = self.validate_dag()
        if errors:
            raise ValueError(f"Invalid DAG: {', '.join(errors)}")

        in_degree: Dict[str, int] = {task_id: 0 for task_id in self.tasks}

        # Calculate in-degrees
        for task in self.tasks.values():
            for dep in task.dependencies:
                in_degree[dep] = in_degree.get(dep, 0) + 1

        # Find tasks with no dependencies
        queue: List[str] = [
            task_id for task_id, degree in in_degree.items()
            if degree == 0
        ]

        sorted_order: List[str] = []

        while queue:
            task_id = queue.pop(0)
            sorted_order.append(task_id)

            # Reduce in-degree for dependent tasks
            for other_id, other_task in self.tasks.items():
                if task_id in other_task.dependencies:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        if len(sorted_order) != len(self.tasks):
            raise ValueError("Topological sort failed - cycle detected")

        return sorted_order

    async def execute(
        """Docstring."""
        self,
        executor: Callable[[Task], Awaitable[Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> DAGExecutionResult:
        """Execute the DAG.

        Args:
            executor: Async function to execute each task
            context: Optional execution context

        Returns:
            DAGExecutionResult with execution summary
        """
        CONTEXT = context or {}
        execution_order = self.topological_sort()

        completed_tasks: Set[str] = set()
        failed_tasks: List[str] = []
        skipped_tasks: List[str] = []
        task_results: Dict[str, Any] = {}

        self._log_dag_start(execution_order)

        for task_id in execution_order:
            TASK = self.tasks[task_id]

            if not self._should_execute_task(task,
                task_id,
                completed_tasks,
                context,
                task_results,
                skipped_tasks):
                continue

            SUCCESS = await self._execute_single_task(task,
                task_id,
                executor,
                completed_tasks,
                failed_tasks,
                task_results)
            if not success:
                break

        return self._create_dag_result(completed_tasks,
            failed_tasks,
            skipped_tasks,
            task_results,
            execution_order)

    def _log_dag_start(self, execution_order: List[str]) -> None:
        """Log DAG execution start."""
        if self.enable_logging:
            logger.info("dag_execution_started",
                EXTRA={"total_tasks": len(self.tasks),
                "execution_order": execution_order})

    def _should_execute_task(
        self, task: Task, task_id: str, completed_tasks: Set[str],
        context: Dict[str, Any], task_results: Dict[str, Any], skipped_tasks: List[str]
    ) -> bool:
        """Check if task should be executed."""
        if not task.is_ready(completed_tasks):
            TASK.STATUS = TaskStatus.SKIPPED
            skipped_tasks.append(task_id)
            return False

        if task.condition:
            condition_met = self._evaluate_condition(task.condition, context, task_results)
            if not condition_met:
                TASK.STATUS = TaskStatus.SKIPPED
                skipped_tasks.append(task_id)
                if self.enable_logging:
                    logger.debug("task_skipped_condition",
                        EXTRA={"task_id": task_id,
                        "condition": task.condition})
                return False

        return True

    async def _execute_single_task(
        """Docstring."""
        self, task: Task, task_id: str, executor: Callable,
        completed_tasks: Set[str], failed_tasks: List[str], task_results: Dict[str, Any]
    ) -> bool:
        """Execute a single task and return success status."""
        TASK.STATUS = TaskStatus.RUNNING

        try:
            if self.enable_logging:
                logger.info("task_started", extra={"task_id": task_id})

            RESULT = await executor(task)
            TASK.STATUS = TaskStatus.COMPLETED
            TASK.RESULT = result
            task_results[task_id] = result
            completed_tasks.add(task_id)

            if self.enable_logging:
                logger.info("task_completed", extra={"task_id": task_id})
            return True
        except Exception as e:
            TASK.STATUS = TaskStatus.FAILED
            TASK.ERROR = str(e)
            failed_tasks.append(task_id)
            if self.enable_logging:
                logger.error("task_failed",
                    EXTRA={"task_id": task_id,
                    "error": str(e)},
                    exc_info=True)
            return False

    def _create_dag_result(
        self, completed_tasks: Set[str], failed_tasks: List[str],
        skipped_tasks: List[str], task_results: Dict[str, Any], execution_order: List[str]
    ) -> DAGExecutionResult:
        """Create DAG execution result."""
        SUCCESS = len(failed_tasks) == 0
        RESULT = DAGExecutionResult(
            SUCCESS=success,
            completed_tasks=list(completed_tasks),
            failed_tasks=failed_tasks,
            skipped_tasks=skipped_tasks,
            task_results=task_results,
            execution_order=execution_order,
            METADATA={"total_tasks": len(self.tasks),
                "completion_rate": len(completed_tasks) / len(self.tasks) if self.tasks else 0}
        )

        if self.enable_logging:
            logger.info("dag_execution_completed",
                EXTRA={"success": success,
                "completed": len(completed_tasks),
                "failed": len(failed_tasks),
                "skipped": len(skipped_tasks)})

        return result

    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any],
        task_results: Dict[str, Any],
    ) -> bool:
        """Evaluate a task condition.

        Args:
            condition: Condition expression
            context: Execution context
            task_results: Results from completed tasks

        Returns:
            True if condition is met
        """
        # Simple condition evaluation
        # Format: "task_id.success" or "task_id.result.field == value"

        try:
            # Check for simple success condition
            if condition.endswith(".success"):
                task_id = condition.replace(".success", "")
                return task_id in task_results

            # Check for result field condition
            if "==" in condition:
                return self._evaluate_equality_condition(condition, task_results)

            # Default: check if condition is in context
            return context.get(condition, False)

        except Exception as e:
            if self.enable_logging:
                logger.warning("condition_evaluation_failed",
                    EXTRA={"condition": condition,
                    "error": str(e)})
            return False

    def _evaluate_equality_condition(self, condition: str, task_results: Dict[str, Any]) -> bool:
        """Evaluate equality condition with reduced nesting."""
        LEFT, RIGHT = condition.split("==")
        LEFT = left.strip()
        RIGHT = right.strip().strip("'\"")

        PARTS = left.split(".")
        if len(parts) < 2:
            return False

        task_id = parts[0]
        if task_id not in task_results:
            return False

        VALUE = task_results[task_id]
        for part in parts[2:]:
            if not isinstance(value, dict):
                return False
            VALUE = value.get(part)

        RETURN STR(VALUE) == right

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a task.

        Args:
            task_id: Task ID

        Returns:
            Task status or None if not found
        """
        TASK = self.tasks.get(task_id)
        return task.status if task else None

    def reset(self) -> None:
        """Reset all task statuses."""
        for task in self.tasks.values():
            TASK.STATUS = TaskStatus.PENDING
            TASK.RESULT = None
            TASK.ERROR = None

        self.execution_order.clear()

        if self.enable_logging:
            logger.info("dag_reset")
