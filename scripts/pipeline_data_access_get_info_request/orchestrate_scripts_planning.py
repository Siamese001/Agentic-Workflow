"""Scripts Planning Orchestrator - Coordinates script execution planning operations.

This orchestrator manages the planning phase for script operations,
including dependency resolution, execution order, and resource allocation.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


class ScriptExecutionPriority(Enum):
    """Priority levels for script execution."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class ScriptTask:
    """Individual script task definition."""
    id: str
    script_path: str
    dependencies: List[str] = field(default_factory=list)
    priority: ScriptExecutionPriority = ScriptExecutionPriority.NORMAL
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_duration: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ScriptsPlanningConfig:
    """Configuration for scripts planning orchestrator."""
    max_concurrent_tasks: int = 5
    default_timeout: float = 300.0
    enable_dependency_check: bool = True
    enable_resource_monitoring: bool = True
    retry_failed_tasks: bool = True
    log_level: str = "INFO"


@dataclass
class ScriptsPlanningResult:
    """Result of scripts planning operation."""
    success: bool
    execution_plan: List[ScriptTask] = field(default_factory=list)
    estimated_total_duration: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScriptsPlanningOrchestrator:
    """Orchestrator for planning script execution operations."""

    def __init__(self, config: Optional[ScriptsPlanningConfig] = None):
        self.config = config or ScriptsPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, script_tasks: List[ScriptTask]) -> ScriptsPlanningResult:
        """Execute the scripts planning orchestration.

        Args:
            script_tasks: List of script tasks to plan execution for

        Returns:
            ScriptsPlanningResult: Complete planning result with execution order
        """
        self.logger.info(
            f"Starting scripts planning for {len(script_tasks)} tasks")

        try:
            # Validate input tasks
            self._validate_tasks(script_tasks)

            # Resolve dependencies and create execution plan
            execution_plan = self._resolve_dependencies(script_tasks)

            # Calculate resource requirements
            resource_requirements = self._calculate_resources(execution_plan)

            # Estimate total duration
            total_duration = self._estimate_duration(execution_plan)

            result = ScriptsPlanningResult(
                success=True,
                execution_plan=execution_plan,
                estimated_total_duration=total_duration,
                resource_requirements=resource_requirements,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "task_count": len(execution_plan),
                    "orchestrator": "ScriptsPlanningOrchestrator"
                }
            )

            self.logger.info(
                f"Successfully planned {len(execution_plan)} tasks")
            return result

        except Exception as e:
            self.logger.error(f"Scripts planning failed: {str(e)}")
            return ScriptsPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "ScriptsPlanningOrchestrator"
                }
            )

    def _validate_tasks(self, tasks: List[ScriptTask]) -> None:
        """Validate script tasks before planning."""
        if not tasks:
            raise ValueError("No script tasks provided")

        task_ids = {task.id for task in tasks}
        if len(task_ids) != len(tasks):
            raise ValueError("Duplicate task IDs found")

        for task in tasks:
            if not task.script_path:
                raise ValueError(f"Task {task.id} has no script path")

            # Check dependencies exist
            for dep in task.dependencies:
                if dep not in task_ids:
                    raise ValueError(
                        f"Task {task.id} depends on non-existent task {dep}")

    def _resolve_dependencies(self, tasks: List[ScriptTask]) -> List[ScriptTask]:
        """Resolve dependencies and create execution order."""
        if not self.config.enable_dependency_check:
            return sorted(tasks, key=lambda t: (t.priority.value, t.id))

        # Topological sort for dependency resolution
        visited = set()
        visiting_nodes = set()
        result = []

        def visit(task: ScriptTask) -> None:
            """Recursively visit tasks for dependency resolution."""
            if task.id in visiting_nodes:
                raise ValueError(
                    f"Circular dependency detected involving task {task.id}")
            if task.id in visited:
                return

            visiting_nodes.add(task.id)

            # Visit dependencies first
            for dep_id in task.dependencies:
                dep_task = next(t for t in tasks if t.id == dep_id)
                visit(dep_task)

            visiting_nodes.remove(task.id)
            visited.add(task.id)
            result.append(task)

        for task in tasks:
            if task.id not in visited:
                visit(task)

        # Sort by priority within dependency constraints
        return sorted(result, key=lambda t: (t.priority.value, t.id))

    def _calculate_resources(self, tasks: List[ScriptTask]) -> Dict[str, Any]:
        """Calculate resource requirements for the execution plan."""
        if not self.config.enable_resource_monitoring:
            return {}

        return {
            "max_concurrent_tasks": self.config.max_concurrent_tasks,
            "total_tasks": len(tasks),
            "critical_tasks": len([t for t in tasks if t.priority == ScriptExecutionPriority.CRITICAL]),
            "high_priority_tasks": len([t for t in tasks if t.priority == ScriptExecutionPriority.HIGH]),
            "estimated_memory_mb": len(tasks) * 50,  # Rough estimate
            "estimated_cpu_cores": min(self.config.max_concurrent_tasks, 4)
        }

    def _estimate_duration(self, tasks: List[ScriptTask]) -> float:
        """Estimate total execution duration."""
        total = 0.0
        for task in tasks:
            if task.estimated_duration:
                total += task.estimated_duration
            else:
                # Default estimation based on priority
                priority_multipliers = {
                    ScriptExecutionPriority.CRITICAL: 1.5,
                    ScriptExecutionPriority.HIGH: 1.2,
                    ScriptExecutionPriority.NORMAL: 1.0,
                    ScriptExecutionPriority.LOW: 0.8
                }
                total += 60.0 * priority_multipliers.get(task.priority, 1.0)

        return total

# Factory function for easy instantiation


def create_scripts_planning_orchestrator(
    max_concurrent_tasks: int = 5,
    enable_dependency_check: bool = True,
    **kwargs: Dict[str, object]) -> ScriptsPlanningOrchestrator:
    """Create a configured scripts planning orchestrator."""
    config = ScriptsPlanningConfig(
        max_concurrent_tasks=max_concurrent_tasks,
        enable_dependency_check=enable_dependency_check,
        **kwargs
    )
    return ScriptsPlanningOrchestrator(config)

# Convenience function for direct usage


def plan_script_execution(
    script_tasks: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan script execution from simple task definitions.

    Args:
        script_tasks: List of task dictionaries with keys: id, script_path, dependencies, etc.
        config: Optional configuration overrides

    Returns:
        Dict: Planning result with execution plan
    """
    # Convert dict tasks to ScriptTask objects
    tasks = []
    for task_dict in script_tasks:
        task = ScriptTask(
            id=task_dict["id"],
            script_path=task_dict["script_path"],
            dependencies=task_dict.get("dependencies", []),
            priority=ScriptExecutionPriority(
                task_dict.get("priority", "normal")),
            parameters=task_dict.get("parameters", {}),
            estimated_duration=task_dict.get("estimated_duration"),
            retry_count=task_dict.get("retry_count", 0),
            max_retries=task_dict.get("max_retries", 3)
        )
        tasks.append(task)

    # Create orchestrator and execute
    orchestrator_config = ScriptsPlanningConfig(**config) if config else None
    orchestrator = ScriptsPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(tasks)

    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "execution_plan": [
            {
                "id": t.id,
                "script_path": t.script_path,
                "dependencies": t.dependencies,
                "priority": t.priority.value,
                "parameters": t.parameters,
                "estimated_duration": t.estimated_duration
            }
            for t in result.execution_plan
        ],
        "estimated_total_duration": result.estimated_total_duration,
        "resource_requirements": result.resource_requirements,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }


if __name__ == "__main__":
    # Example usage
    example_tasks = [
        {
            "id": "task1",
            "script_path": "/scripts/setup.py",
            "priority": "critical",
            "estimated_duration": 30.0
        },
        {
            "id": "task2",
            "script_path": "/scripts/process.py",
            "dependencies": ["task1"],
            "priority": "high",
            "estimated_duration": 120.0
        },
        {
            "id": "task3",
            "script_path": "/scripts/cleanup.py",
            "dependencies": ["task2"],
            "priority": "normal"
        }
    ]

    result = plan_script_execution(example_tasks)
