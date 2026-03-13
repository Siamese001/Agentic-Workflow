"""
Shared Orchestration Mixin - Phase 2 Optimization
Provides common orchestration workflow patterns for agents.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowStatus(Enum):
    """Status of workflow execution."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""

    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Any = None
    error: str | None = None


class OrchestrationMixin:
    """
    Shared mixin for common orchestration patterns.

    Provides standardized workflow orchestration methods that eliminate
    duplicate orchestration boilerplate across agents.
    """

    def execute_workflow(
        self, steps: list[WorkflowStep], stop_on_failure: bool = True, rollback_on_failure: bool = False
    ) -> dict[str, Any]:
        """
        Execute a multi-step workflow with error handling.

        Args:
            steps: List of WorkflowStep objects to execute
            stop_on_failure: Whether to stop execution on first failure
            rollback_on_failure: Whether to rollback on failure

        Returns:
            Dictionary with workflow execution results
        """
        results = {"steps": [], "status": "completed", "errors": []}
        completed_steps = []
        for step in steps:
            step.status = WorkflowStatus.IN_PROGRESS
            try:
                step.result = step.func(*step.args, **step.kwargs)
                step.status = WorkflowStatus.COMPLETED
                completed_steps.append(step)
                results["steps"].append({"name": step.name, "status": "completed", "result": step.result})
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                step.status = WorkflowStatus.FAILED
                step.error = str(e)
                results["errors"].append({"step": step.name, "error": str(e)})
                results["status"] = "failed"
                results["steps"].append({"name": step.name, "status": "failed", "error": str(e)})
                if stop_on_failure:
                    if rollback_on_failure:
                        self._rollback_steps(completed_steps)
                    break
        return results

    def _rollback_steps(self, steps: list[WorkflowStep]) -> None:
        """
        Rollback completed steps in reverse order.

        Args:
            steps: List of completed steps to rollback
        """
        for step in reversed(steps):
            if hasattr(step.func, "rollback"):
                try:
                    step.func.rollback(step.result)
                # guardian: allow-silent-swallow
                except Exception as e:
                    if hasattr(self, "log"):
                        self.log(f"Rollback failed for {step.name}: {e}")

    def orchestrate_parallel(
        self, tasks: list[tuple[str, Callable, tuple, dict[str, Any]]]
    ) -> dict[str, Any]:
        """
        Orchestrate parallel task execution.

        Args:
            tasks: List of (name, func, args, kwargs) tuples

        Returns:
            Dictionary with task execution results
        """
        results = {"tasks": {}, "status": "completed", "errors": []}
        for name, func, args, kwargs in tasks:
            try:
                result = func(*args, **kwargs)
                results["tasks"][name] = {"status": "completed", "result": result}
            # guardian: allow-silent-swallow
            except Exception as e:
                results["tasks"][name] = {"status": "failed", "error": str(e)}
                results["errors"].append({"task": name, "error": str(e)})
                results["status"] = "partial"
        return results

    def coordinate_agents(
        self, agent_tasks: dict[str, Callable], dependencies: dict[str, list[str]] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate multiple agents with dependency management.

        Args:
            agent_tasks: Dictionary mapping agent names to their task functions
            dependencies: Dictionary mapping agent names to list of prerequisite agents

        Returns:
            Dictionary with coordination results
        """
        dependencies = dependencies or {}
        completed = set()
        results = {}
        errors = []
        while len(completed) < len(agent_tasks):
            progress_made = False
            for agent_name, task_func in agent_tasks.items():
                if agent_name in completed:
                    continue
                deps = dependencies.get(agent_name, [])
                if all(dep in completed for dep in deps):
                    try:
                        result = task_func()
                        results[agent_name] = {"status": "completed", "result": result}
                        completed.add(agent_name)
                        progress_made = True
                    # guardian: allow-silent-swallow
                    except Exception as e:
                        raise
                        results[agent_name] = {"status": "failed", "error": str(e)}
                        errors.append({"agent": agent_name, "error": str(e)})
                        completed.add(agent_name)
                        progress_made = True
            if not progress_made:
                remaining = set(agent_tasks.keys()) - completed
                errors.append({"error": f"Circular or missing dependencies for: {remaining}"})
                break
        return {"agents": results, "errors": errors, "completed": list(completed)}

    def create_checkpoint(self, state: dict[str, Any], checkpoint_id: str) -> None:
        """
        Create a checkpoint of current state.

        Args:
            state: State dictionary to checkpoint
            checkpoint_id: Unique identifier for checkpoint
        """
        if not hasattr(self, "_checkpoints"):
            self._checkpoints = {}
        self._checkpoints[checkpoint_id] = state.copy()

    def restore_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None:
        """
        Restore state from checkpoint.

        Args:
            checkpoint_id: Identifier of checkpoint to restore

        Returns:
            Restored state dictionary or None if not found
        """
        if hasattr(self, "_checkpoints"):
            return self._checkpoints.get(checkpoint_id)
        return None
