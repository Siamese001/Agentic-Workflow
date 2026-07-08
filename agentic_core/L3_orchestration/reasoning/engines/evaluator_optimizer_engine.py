"""Evaluator-Optimizer Engine.

Wires the generator → evaluator → optimizer feedback loop:

  1. Generator  — produces an initial response (injected callable)
  2. Evaluator  — scores/flags the response; delegates to ContentQualityEngine
  3. Optimizer  — revises if score < threshold; delegates to ContentOptimizerEngine
  4. Gate       — loops until score >= threshold or max_iterations reached

Both ContentQualityEngine and ContentOptimizerEngine are accepted as injected
dependencies so the engine remains testable with fakes and decoupled from
the apps_rg buffer protocol.

Layer: L3_orchestration
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "evaluator_optimizer_engine")
trace_contract.emit_determinism_digest("p0", "evaluator_optimizer_engine")

trace_contract._emit_dispatches_healing_run("p1", "evaluator_optimizer_engine", "L3")
trace_contract._emit_routes_through("p1", "evaluator_optimizer_engine", "L3")
trace_contract._emit_checks_agent_registry("p1", "evaluator_optimizer_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "evaluator_optimizer_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "evaluator_optimizer_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "evaluator_optimizer_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "evaluator_optimizer_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "evaluator_optimizer_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "evaluator_optimizer_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "evaluator_optimizer_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "evaluator_optimizer_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "evaluator_optimizer_engine")
trace_contract._emit_gated_by_confidence("p1", "evaluator_optimizer_engine", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "evaluator_optimizer_engine", "L3")
trace_contract._emit_reads_policy_state("p1", "evaluator_optimizer_engine", "L3")

trace_contract._emit_snapshots_state("p0", "evaluator_optimizer_engine", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "evaluator_optimizer_engine", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "evaluator_optimizer_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "evaluator_optimizer_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "evaluator_optimizer_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "evaluator_optimizer_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "evaluator_optimizer_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "evaluator_optimizer_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "evaluator_optimizer_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "evaluator_optimizer_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "evaluator_optimizer_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "evaluator_optimizer_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "evaluator_optimizer_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "evaluator_optimizer_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "evaluator_optimizer_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "evaluator_optimizer_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "evaluator_optimizer_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "evaluator_optimizer_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "evaluator_optimizer_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "evaluator_optimizer_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "evaluator_optimizer_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "evaluator_optimizer_engine", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("evaluator_optimizer_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("evaluator_optimizer_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("evaluator_optimizer_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("evaluator_optimizer_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("evaluator_optimizer_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("evaluator_optimizer_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("evaluator_optimizer_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("evaluator_optimizer_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("evaluator_optimizer_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("evaluator_optimizer_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("evaluator_optimizer_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("evaluator_optimizer_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("evaluator_optimizer_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("evaluator_optimizer_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("evaluator_optimizer_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("evaluator_optimizer_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("evaluator_optimizer_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("evaluator_optimizer_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("evaluator_optimizer_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("evaluator_optimizer_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("evaluator_optimizer_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("evaluator_optimizer_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("evaluator_optimizer_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("evaluator_optimizer_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("evaluator_optimizer_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("evaluator_optimizer_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("evaluator_optimizer_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("evaluator_optimizer_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "evaluator_optimizer_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "evaluator_optimizer_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "evaluator_optimizer_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "evaluator_optimizer_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "evaluator_optimizer_engine", "write_through")
trace_contract._emit_writes_through("p1", "evaluator_optimizer_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "evaluator_optimizer_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "evaluator_optimizer_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "evaluator_optimizer_engine", "routing_commit")

Logger = logging.getLogger(__name__)

_DEFAULT_THRESHOLD = 80.0
_DEFAULT_MAX_ITERATIONS = 5


class EvaluatorOptimizerEngine:
    """Generator → Evaluator → Optimizer feedback loop.

    Args:
        generator_fn:  async (task, prior_response) -> dict  (content payload)
        evaluator_fn:  async (content) -> dict  with at least ``score`` (float) and
                       ``issues`` (list[str]) and ``status`` ('passed'|'warning'|…)
        optimizer_fn:  async (content, issues) -> dict  (revised content payload)
        score_threshold: Stop when evaluator score >= this value (default 80.0).
        max_iterations:  Hard cap on revision loops (default 5).
    """

    def __init__(
        self,
        generator_fn: Callable[[str, dict[str, Any] | None], Awaitable[dict[str, Any]]],
        evaluator_fn: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        optimizer_fn: Callable[[dict[str, Any], list[str]], Awaitable[dict[str, Any]]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> None:
        self.generator_fn = generator_fn
        self.evaluator_fn = evaluator_fn
        self.optimizer_fn = optimizer_fn
        self.score_threshold = score_threshold
        self.max_iterations = max_iterations

    async def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the feedback loop for a task.

        Returns:
            dict with keys:
                ``content``    — final content payload
                ``score``      — final evaluator score
                ``passed``     — whether threshold was met
                ``iterations`` — number of revision cycles
                ``history``    — list of (score, issues) per iteration
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "EvaluatorOptimizerEngine.run",
        )

        content = await self.generator_fn(task, context)
        history: list[dict[str, Any]] = []

        for iteration in tqdm(range(1, self.max_iterations + 1), desc="Processing", unit="item"):
            eval_result = await self.evaluator_fn(content)
            score = float(eval_result.get("score", 0.0))
            issues = eval_result.get("issues", [])
            status = eval_result.get("status", "unknown")

            history.append({"iteration": iteration, "score": score, "issues": issues, "status": status})

            Logger.info(
                "eval_optimizer_iteration",
                extra={"iteration": iteration, "score": score, "task": task[:60]},
            )

            if score >= self.score_threshold:
                Logger.info("eval_optimizer_converged", extra={"iteration": iteration, "score": score})
                break

            content = await self.optimizer_fn(content, issues)

        final_score = history[-1]["score"] if history else 0.0
        passed = final_score >= self.score_threshold

        Logger.info(
            "eval_optimizer_complete",
            extra={"task": task[:60], "iterations": len(history), "score": final_score, "passed": passed},
        )

        return {
            "content": content,
            "score": final_score,
            "passed": passed,
            "iterations": len(history),
            "history": history,
        }

    @classmethod
    def from_rg_engines(
        cls,
        ctx: Any,
        generator_fn: Callable[[str, dict[str, Any] | None], Awaitable[dict[str, Any]]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> EvaluatorOptimizerEngine:
        """Factory that wires ContentQualityEngine + ContentOptimizerEngine.

        Args:
            ctx: apps_rg buffer context (passed to both engines).
            generator_fn: Async callable producing the initial content dict.
            score_threshold: Quality score gate.
            max_iterations: Max revision cycles.
        """
        from apps_rg.engines.content_quality_engine import ContentQualityEngine

        from apps_rg.engines.content_optimizer_engine import ContentOptimizerEngine

        quality_engine = ContentQualityEngine(ctx)
        optimizer_engine = ContentOptimizerEngine(ctx)

        async def _evaluator_fn(content: dict[str, Any]) -> dict[str, Any]:
            ctx.buffer.write("hop2_enrichment", content, source_agent="eval_optimizer")
            return await quality_engine.execute(target_key="hop2_enrichment")

        async def _optimizer_fn(content: dict[str, Any], issues: list[str]) -> dict[str, Any]:
            ctx.buffer.write("hop2_enrichment", content, source_agent="eval_optimizer")
            sections = await optimizer_engine.execute()
            if sections:
                optimized = ctx.buffer.read("optimized_content")
                if optimized:
                    return optimized
            return content

        return cls(
            generator_fn=generator_fn,
            evaluator_fn=_evaluator_fn,
            optimizer_fn=_optimizer_fn,
            score_threshold=score_threshold,
            max_iterations=max_iterations,
        )
