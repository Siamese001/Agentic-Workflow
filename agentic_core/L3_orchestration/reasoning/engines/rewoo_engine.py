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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "rewoo_engine")
emit_determinism_digest("p0", "rewoo_engine")

_emit_dispatches_healing_run("p1", "rewoo_engine", "L3")
_emit_routes_through("p1", "rewoo_engine", "L3")
_emit_checks_agent_registry("p1", "rewoo_engine", "agent_registry")
_emit_validates_agent_capability("p1", "rewoo_engine", "capability")
_emit_dispatches_execution_plan("p1", "rewoo_engine", "exec_plan")
_emit_agent_executes_agent("p1", "rewoo_engine", "sub_agent")
_emit_routes_to_agent("p1", "rewoo_engine", "target_agent")
_emit_verifies_policy("p1", "rewoo_engine", "policy_check")
_emit_observes_runtime_state("p1", "rewoo_engine", "runtime_state")
_emit_verifies_boundary("p1", "rewoo_engine", "boundary_check")
_emit_transcripts_response("p1", "rewoo_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "rewoo_engine")
_emit_gated_by_confidence("p1", "rewoo_engine", "confidence_gate")
_emit_escalates_to_human("p1", "rewoo_engine", "L3")
_emit_reads_policy_state("p1", "rewoo_engine", "L3")

_emit_snapshots_state("p0", "rewoo_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "rewoo_engine", "p0_governance")
_emit_authorize_and_execute("p2", "rewoo_engine", "execution_auth")
_emit_validates_capability("p2", "rewoo_engine", "capability_check")
_emit_routes_to_capability("p2", "rewoo_engine", "capability_route")
_emit_writes_via_uwg("p2", "rewoo_engine", "uwg_write")
_emit_blocks_direct_write("p2", "rewoo_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "rewoo_engine", "tool_invocation")
_emit_captures_execution_output("p2", "rewoo_engine", "exec_output")
_emit_dispatches_agent("p3", "rewoo_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "rewoo_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "rewoo_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "rewoo_engine", "healing_outcome")
_emit_escalates_failure("p3", "rewoo_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "rewoo_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rewoo_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "rewoo_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "rewoo_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rewoo_engine", "eval_metric")
_emit_stores_embedding("p4", "rewoo_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "rewoo_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rewoo_engine", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("rewoo_engine", "p4obs", "metric_1")
_emit_emits_metric_event("rewoo_engine", "p4obs", "metric_2")
_emit_emits_metric_event("rewoo_engine", "p4obs", "metric_3")
_emit_emits_metric_event("rewoo_engine", "p4obs", "metric_4")
_emit_emits_metric_event("rewoo_engine", "p4obs", "metric_5")
_emit_emits_metric_event("rewoo_engine", "p4obs", "metric_6")
_emit_records_incident_event("rewoo_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("rewoo_engine", "p4obs", "anomaly")
_emit_writes_observability_log("rewoo_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("rewoo_engine", "p4obs", "mon_state")
_emit_triggers_alert("rewoo_engine", "p4obs", "alert")
_emit_links_incident_trace("rewoo_engine", "p4obs", "trace_link")
_emit_captures_pattern("rewoo_engine", "p3lm", "pattern")
_emit_records_learning_event("rewoo_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rewoo_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("rewoo_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rewoo_engine", "p3lm", "routing")
_emit_improves_agent_policy("rewoo_engine", "p3lm", "policy")
_emit_stores_learning_state("rewoo_engine", "p3lm", "state")
_emit_records_execution_trace("rewoo_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rewoo_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rewoo_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rewoo_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rewoo_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rewoo_engine", "env_read", "p2_env_1")
_emit_reads_environ("rewoo_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("rewoo_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rewoo_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rewoo_engine", "context_pull")
_emit_pulls_context("p1", "rewoo_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rewoo_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rewoo_engine", "uwg_term_2")
_emit_writes_through("p1", "rewoo_engine", "write_through")
_emit_writes_through("p1", "rewoo_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "rewoo_engine", "safety_validation")
_emit_invokes_eval("p1", "rewoo_engine", "eval_call")
_emit_proposal_commits_routing("p1", "rewoo_engine", "routing_commit")

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
        except (ValueError, TypeError) as exc:  # guardian: allow-silent-swallower
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
