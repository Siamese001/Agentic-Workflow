"""Rewoo (Reasoning Without Observation) Engine.

Pattern: Planner → task-list → Solver → Worker → update context
The key insight: planning happens *before* any tool execution, so the
Planner can reason about the full dependency graph upfront.

  1. RewooPlanner  — generates ordered RewooTaskList with reasoning annotations
  2. RewooSolver   — executes each ready task via tool access; stores results
  3. RewooWorker   — updates RewooContext so downstream tasks see prior results

Layer: L3_orchestration
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from agentic_core.L3_orchestration.types.rewoo_types import (
    RewooContext,
    RewooTask,
    RewooTaskList,
    RewooTaskStatus,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)


class RewooPlanner:
    """Generates a full task list with reasoning annotations before any execution.

    The planner_fn receives the goal and returns a list of dicts, each with:
      - task_id: str
      - description: str
      - reasoning: str   (why this task is needed)
      - tool_name: str
      - tool_input: dict
      - depends_on: list[str]  (task_ids that must complete first)
    """

    def __init__(
        self,
        planner_fn: Callable[[str, dict[str, Any]], Awaitable[list[dict[str, Any]]]],
    ) -> None:
        self._planner_fn = planner_fn

    async def plan(self, goal: str, context: dict[str, Any] | None = None) -> RewooTaskList:
        """Generate ordered task list for the goal."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RewooPlanner.plan")

        raw_tasks = await self._planner_fn(goal, context or {})
        task_list = RewooTaskList(goal=goal)
        for raw in raw_tasks:
            task_list.tasks.append(
                RewooTask(
                    task_id=raw.get("task_id", f"task_{uuid.uuid4().hex[:6]}"),
                    description=raw.get("description", ""),
                    reasoning=raw.get("reasoning", ""),
                    tool_name=raw.get("tool_name", "noop"),
                    tool_input=raw.get("tool_input", {}),
                    depends_on=raw.get("depends_on", []),
                )
            )
        Logger.info("rewoo_plan_generated", extra={"goal": goal[:80], "num_tasks": len(task_list.tasks)})
        return task_list


class RewooSolver:
    """Executes tasks from the task list using registered tools.

    Tools are registered as callables: async fn(tool_input: dict) -> Any
    """

    def __init__(self) -> None:
        self._tools: dict[str, Callable[[dict[str, Any]], Awaitable[Any]]] = {}

    def register_tool(self, name: str, fn: Callable[[dict[str, Any]], Awaitable[Any]]) -> None:
        self._tools[name] = fn

    async def execute_task(self, task: RewooTask, context: RewooContext) -> Any:
        """Execute a single task, substituting #task_id references in tool_input."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RewooSolver.execute_task")

        task.status = RewooTaskStatus.RUNNING
        resolved_input = self._resolve_references(task.tool_input, context.results)
        tool_fn = self._tools.get(task.tool_name)
        if tool_fn is None:
            task.status = RewooTaskStatus.FAILED
            task.error = f"Tool '{task.tool_name}' not registered"
            Logger.warning("rewoo_tool_missing", extra={"tool": task.tool_name, "task_id": task.task_id})
            return None
        try:
            result = await tool_fn(resolved_input)
            task.result = result
            task.status = RewooTaskStatus.COMPLETED
            Logger.info("rewoo_task_done", extra={"task_id": task.task_id, "tool": task.tool_name})
            return result
        except Exception as exc:  # guardian: allow-silent-swallower
            task.status = RewooTaskStatus.FAILED
            task.error = str(exc)
            Logger.error("rewoo_task_error", extra={"task_id": task.task_id, "error": str(exc)})
            return None

    def _resolve_references(self, tool_input: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
        """Replace '#task_id' placeholders in string values with prior results."""
        resolved: dict[str, Any] = {}
        for k, v in tool_input.items():
            if isinstance(v, str) and v.startswith("#"):
                ref_id = v[1:]
                resolved[k] = results.get(ref_id, v)
            else:
                resolved[k] = v
        return resolved


class RewooWorker:
    """Updates RewooContext with task results after each Solver execution."""

    def update(self, context: RewooContext, task: RewooTask) -> None:
        """Persist task result into context for downstream tasks."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RewooWorker.update")

        if task.result is not None:
            context.results[task.task_id] = task.result
        context.iteration += 1
        Logger.debug("rewoo_worker_update", extra={"task_id": task.task_id, "iteration": context.iteration})


class RewooEngine:
    """Orchestrates the full Rewoo pattern: Planner → Solver → Worker loop.

    Usage::

        engine = RewooEngine(planner, solver, worker, max_iterations=20)
        context = await engine.run(goal="Summarise and cite 3 sources", context={})
        print(context.final_answer)
    """

    def __init__(
        self,
        planner: RewooPlanner,
        solver: RewooSolver,
        worker: RewooWorker | None = None,
        max_iterations: int = 50,
        stop_on_first_failure: bool = False,
    ) -> None:
        self.planner = planner
        self.solver = solver
        self.worker = worker or RewooWorker()
        self.max_iterations = max_iterations
        self.stop_on_first_failure = stop_on_first_failure

    async def run(
        self,
        goal: str,
        context: dict[str, Any] | None = None,
        synthesizer_fn: Callable[[RewooContext], Awaitable[str]] | None = None,
    ) -> RewooContext:
        """Run the full Rewoo pipeline.

        Args:
            goal: High-level objective.
            context: Optional seed context passed to Planner.
            synthesizer_fn: Optional async fn that produces a final_answer from RewooContext.

        Returns:
            RewooContext with all task results and optional final_answer.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RewooEngine.run")

        task_list = await self.planner.plan(goal, context)
        rewoo_ctx = RewooContext(goal=goal, task_list=task_list)

        iterations = 0
        while iterations < self.max_iterations:
            ready = task_list.ready_tasks()
            if not ready:
                break
            for task in ready:
                await self.solver.execute_task(task, rewoo_ctx)
                self.worker.update(rewoo_ctx, task)
                if self.stop_on_first_failure and task.status == RewooTaskStatus.FAILED:
                    rewoo_ctx.error = f"Task {task.task_id} failed: {task.error}"
                    Logger.warning("rewoo_early_stop", extra={"task_id": task.task_id})
                    rewoo_ctx.success = False
                    return rewoo_ctx
            iterations += 1

        all_done = all(
            t.status in (RewooTaskStatus.COMPLETED, RewooTaskStatus.SKIPPED, RewooTaskStatus.FAILED)
            for t in task_list.tasks
        )
        rewoo_ctx.success = all_done and not any(t.status == RewooTaskStatus.FAILED for t in task_list.tasks)

        if synthesizer_fn is not None:
            rewoo_ctx.final_answer = await synthesizer_fn(rewoo_ctx)

        Logger.info(
            "rewoo_complete",
            extra={
                "goal": goal[:80],
                "success": rewoo_ctx.success,
                "iterations": iterations,
                "tasks": len(task_list.tasks),
            },
        )
        return rewoo_ctx
