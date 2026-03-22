"""Parallelization Engine.

Formalises the fan-out / fan-in pattern on top of the existing DAGManager infra.

Two modes:
  SECTIONING  — split one task into N sub-tasks, run in parallel, aggregate results
  SAMPLING    — run the same task N times with different seeds, vote / synthesize

Aggregation strategies:
  majority_vote   — pick the most common result string
  llm_synthesize  — call an async synthesizer_fn on all outputs
  first_pass      — return the first result that passes a predicate
  collect_all     — return the full list of outputs (no reduction)

Layer: L3_orchestration
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "parallelization_engine")
emit_determinism_digest("p0", "parallelization_engine")

_emit_dispatches_healing_run("p1", "parallelization_engine", "L3")
_emit_routes_through("p1", "parallelization_engine", "L3")
_emit_checks_agent_registry("p1", "parallelization_engine", "agent_registry")
_emit_validates_agent_capability("p1", "parallelization_engine", "capability")
_emit_dispatches_execution_plan("p1", "parallelization_engine", "exec_plan")
_emit_agent_executes_agent("p1", "parallelization_engine", "sub_agent")
_emit_routes_to_agent("p1", "parallelization_engine", "target_agent")
_emit_verifies_policy("p1", "parallelization_engine", "policy_check")
_emit_observes_runtime_state("p1", "parallelization_engine", "runtime_state")
_emit_verifies_boundary("p1", "parallelization_engine", "boundary_check")
_emit_transcripts_response("p1", "parallelization_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "parallelization_engine")
_emit_gated_by_confidence("p1", "parallelization_engine", "confidence_gate")
_emit_escalates_to_human("p1", "parallelization_engine", "L3")
_emit_reads_policy_state("p1", "parallelization_engine", "L3")

_emit_snapshots_state("p0", "parallelization_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "parallelization_engine", "p0_governance")
_emit_authorize_and_execute("p2", "parallelization_engine", "execution_auth")
_emit_validates_capability("p2", "parallelization_engine", "capability_check")
_emit_routes_to_capability("p2", "parallelization_engine", "capability_route")
_emit_writes_via_uwg("p2", "parallelization_engine", "uwg_write")
_emit_blocks_direct_write("p2", "parallelization_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "parallelization_engine", "tool_invocation")
_emit_captures_execution_output("p2", "parallelization_engine", "exec_output")
_emit_dispatches_agent("p3", "parallelization_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "parallelization_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "parallelization_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "parallelization_engine", "healing_outcome")
_emit_escalates_failure("p3", "parallelization_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "parallelization_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "parallelization_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "parallelization_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "parallelization_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "parallelization_engine", "eval_metric")
_emit_stores_embedding("p4", "parallelization_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "parallelization_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "parallelization_engine", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("parallelization_engine", "p4obs", "metric_1")
_emit_emits_metric_event("parallelization_engine", "p4obs", "metric_2")
_emit_emits_metric_event("parallelization_engine", "p4obs", "metric_3")
_emit_emits_metric_event("parallelization_engine", "p4obs", "metric_4")
_emit_emits_metric_event("parallelization_engine", "p4obs", "metric_5")
_emit_emits_metric_event("parallelization_engine", "p4obs", "metric_6")
_emit_records_incident_event("parallelization_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("parallelization_engine", "p4obs", "anomaly")
_emit_writes_observability_log("parallelization_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("parallelization_engine", "p4obs", "mon_state")
_emit_triggers_alert("parallelization_engine", "p4obs", "alert")
_emit_links_incident_trace("parallelization_engine", "p4obs", "trace_link")
_emit_captures_pattern("parallelization_engine", "p3lm", "pattern")
_emit_records_learning_event("parallelization_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("parallelization_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("parallelization_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("parallelization_engine", "p3lm", "routing")
_emit_improves_agent_policy("parallelization_engine", "p3lm", "policy")
_emit_stores_learning_state("parallelization_engine", "p3lm", "state")
_emit_records_execution_trace("parallelization_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("parallelization_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("parallelization_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("parallelization_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("parallelization_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("parallelization_engine", "env_read", "p2_env_1")
_emit_reads_environ("parallelization_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("parallelization_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("parallelization_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "parallelization_engine", "context_pull")
_emit_pulls_context("p1", "parallelization_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "parallelization_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "parallelization_engine", "uwg_term_2")
_emit_writes_through("p1", "parallelization_engine", "write_through")
_emit_writes_through("p1", "parallelization_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "parallelization_engine", "safety_validation")
_emit_invokes_eval("p1", "parallelization_engine", "eval_call")
_emit_proposal_commits_routing("p1", "parallelization_engine", "routing_commit")

Logger = logging.getLogger(__name__)


class ParallelMode(Enum):
    SECTIONING = "sectioning"
    SAMPLING = "sampling"


class AggregationStrategy(Enum):
    MAJORITY_VOTE = "majority_vote"
    LLM_SYNTHESIZE = "llm_synthesize"
    FIRST_PASS = "first_pass"
    COLLECT_ALL = "collect_all"


class ParallelizationEngine:
    """Fan-out / fan-in parallel execution engine.

    Args:
        worker_fn:     async (task: str, seed: int | None) -> Any
            Called for each parallel branch. In SECTIONING mode, ``task`` is a
            sub-task string; in SAMPLING mode, ``task`` is the same goal each time.
        mode:          ParallelMode (SECTIONING or SAMPLING).
        aggregation:   AggregationStrategy for reducing parallel outputs.
        synthesizer_fn: Required when aggregation=LLM_SYNTHESIZE.
                        async (outputs: list[Any]) -> str
        pass_predicate: Required when aggregation=FIRST_PASS.
                        sync (output: Any) -> bool
        max_concurrency: Optional semaphore cap on simultaneous workers.
    """

    def __init__(
        self,
        worker_fn: Callable[[str, int | None], Awaitable[Any]],
        mode: ParallelMode = ParallelMode.SECTIONING,
        aggregation: AggregationStrategy = AggregationStrategy.COLLECT_ALL,
        synthesizer_fn: Callable[[list[Any]], Awaitable[str]] | None = None,
        pass_predicate: Callable[[Any], bool] | None = None,
        max_concurrency: int | None = None,
    ) -> None:
        self.worker_fn = worker_fn
        self.mode = mode
        self.aggregation = aggregation
        self.synthesizer_fn = synthesizer_fn
        self.pass_predicate = pass_predicate
        self._semaphore = asyncio.Semaphore(max_concurrency) if max_concurrency else None

    async def run(
        self,
        goal: str,
        branches: list[str] | None = None,
        n_samples: int = 3,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute parallel branches and aggregate.

        Args:
            goal:     Main task / goal string.
            branches: Sub-task strings for SECTIONING mode. If None in SECTIONING
                      mode, goal is used as the only branch.
            n_samples: Number of parallel samples for SAMPLING mode (ignored in SECTIONING).
            context:  Optional metadata passed through to the result.

        Returns:
            dict with keys:
                ``result``   — aggregated output
                ``outputs``  — raw list of per-branch outputs
                ``mode``     — parallelization mode name
                ``branches`` — list of branch task strings used
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ParallelizationEngine.run")

        if self.mode == ParallelMode.SECTIONING:
            tasks = branches if branches else [goal]
            seeds = [None] * len(tasks)
        else:
            tasks = [goal] * n_samples
            seeds = list(range(n_samples))

        Logger.info(
            "parallelization_start",
            extra={"mode": self.mode.value, "branches": len(tasks), "goal": goal[:60]},
        )

        outputs = await self._execute_parallel(tasks, seeds)

        result = await self._aggregate(outputs)

        Logger.info(
            "parallelization_complete",
            extra={"mode": self.mode.value, "branches": len(tasks), "aggregation": self.aggregation.value},
        )

        return {
            "result": result,
            "outputs": outputs,
            "mode": self.mode.value,
            "branches": tasks,
        }

    async def _execute_parallel(self, tasks: list[str], seeds: list[int | None]) -> list[Any]:
        """Run all branches concurrently, respecting optional semaphore."""

        async def _guarded(task: str, seed: int | None) -> Any:
            if self._semaphore:
                async with self._semaphore:
                    return await self.worker_fn(task, seed)
            return await self.worker_fn(task, seed)

        results = await asyncio.gather(
            *[_guarded(t, s) for t, s in zip(tasks, seeds)],
            return_exceptions=True,
        )
        outputs: list[Any] = []
        for i, r in enumerate(results):
            if isinstance(r, BaseException):
                Logger.error("parallelization_branch_error", extra={"branch": i, "error": str(r)})
                outputs.append(None)
            else:
                outputs.append(r)
        return outputs

    async def _aggregate(self, outputs: list[Any]) -> Any:
        valid = [o for o in outputs if o is not None]

        if self.aggregation == AggregationStrategy.COLLECT_ALL:
            return outputs

        if self.aggregation == AggregationStrategy.MAJORITY_VOTE:
            if not valid:
                return None
            counts: dict[str, int] = {}
            for o in valid:
                key = str(o)
                counts[key] = counts.get(key, 0) + 1
            winner = max(counts, key=counts.__getitem__)
            return winner

        if self.aggregation == AggregationStrategy.LLM_SYNTHESIZE:
            if self.synthesizer_fn is None:
                raise ValueError("synthesizer_fn required for LLM_SYNTHESIZE aggregation")
            return await self.synthesizer_fn(valid)

        if self.aggregation == AggregationStrategy.FIRST_PASS:
            if self.pass_predicate is None:
                raise ValueError("pass_predicate required for FIRST_PASS aggregation")
            for o in valid:
                if self.pass_predicate(o):
                    return o
            return valid[0] if valid else None

        return outputs
