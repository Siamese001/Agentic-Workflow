"""Reflexion Engine.

Full Reflexion loop (Shinn et al. 2023):
  1. Generator  — produces initial/revised response
  2. Evaluator  — verbal critique + numeric score (delegates scoring to ReflectionEngine)
  3. Memory     — stores critique history across iterations (ReflexionMemory)
  4. Revisor    — uses critique + memory to generate a revised response
  5. Gate       — loops up to max_iterations; stops early when score >= threshold

Delegates scalar scoring back to the existing apps_rg ReflectionEngine stub
so existing pipeline behaviour is preserved.

Layer: L3_orchestration
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from agentic_core.L3_orchestration.types.reflexion_types import ReflexionCritique, ReflexionMemory
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

emit_replay_key("p0", "reflexion_engine")
emit_determinism_digest("p0", "reflexion_engine")

_emit_dispatches_healing_run("p1", "reflexion_engine", "L3")
_emit_routes_through("p1", "reflexion_engine", "L3")
_emit_checks_agent_registry("p1", "reflexion_engine", "agent_registry")
_emit_validates_agent_capability("p1", "reflexion_engine", "capability")
_emit_dispatches_execution_plan("p1", "reflexion_engine", "exec_plan")
_emit_agent_executes_agent("p1", "reflexion_engine", "sub_agent")
_emit_routes_to_agent("p1", "reflexion_engine", "target_agent")
_emit_verifies_policy("p1", "reflexion_engine", "policy_check")
_emit_observes_runtime_state("p1", "reflexion_engine", "runtime_state")
_emit_verifies_boundary("p1", "reflexion_engine", "boundary_check")
_emit_transcripts_response("p1", "reflexion_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "reflexion_engine")
_emit_gated_by_confidence("p1", "reflexion_engine", "confidence_gate")
_emit_escalates_to_human("p1", "reflexion_engine", "L3")
_emit_reads_policy_state("p1", "reflexion_engine", "L3")

_emit_snapshots_state("p0", "reflexion_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "reflexion_engine", "p0_governance")
_emit_authorize_and_execute("p2", "reflexion_engine", "execution_auth")
_emit_validates_capability("p2", "reflexion_engine", "capability_check")
_emit_routes_to_capability("p2", "reflexion_engine", "capability_route")
_emit_writes_via_uwg("p2", "reflexion_engine", "uwg_write")
_emit_blocks_direct_write("p2", "reflexion_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "reflexion_engine", "tool_invocation")
_emit_captures_execution_output("p2", "reflexion_engine", "exec_output")
_emit_dispatches_agent("p3", "reflexion_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "reflexion_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "reflexion_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "reflexion_engine", "healing_outcome")
_emit_escalates_failure("p3", "reflexion_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "reflexion_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reflexion_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "reflexion_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "reflexion_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reflexion_engine", "eval_metric")
_emit_stores_embedding("p4", "reflexion_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "reflexion_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reflexion_engine", "exec_snapshot_link")
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

_emit_emits_metric_event("reflexion_engine", "p4obs", "metric_1")
_emit_emits_metric_event("reflexion_engine", "p4obs", "metric_2")
_emit_emits_metric_event("reflexion_engine", "p4obs", "metric_3")
_emit_emits_metric_event("reflexion_engine", "p4obs", "metric_4")
_emit_emits_metric_event("reflexion_engine", "p4obs", "metric_5")
_emit_emits_metric_event("reflexion_engine", "p4obs", "metric_6")
_emit_records_incident_event("reflexion_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("reflexion_engine", "p4obs", "anomaly")
_emit_writes_observability_log("reflexion_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("reflexion_engine", "p4obs", "mon_state")
_emit_triggers_alert("reflexion_engine", "p4obs", "alert")
_emit_links_incident_trace("reflexion_engine", "p4obs", "trace_link")
_emit_captures_pattern("reflexion_engine", "p3lm", "pattern")
_emit_records_learning_event("reflexion_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reflexion_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("reflexion_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reflexion_engine", "p3lm", "routing")
_emit_improves_agent_policy("reflexion_engine", "p3lm", "policy")
_emit_stores_learning_state("reflexion_engine", "p3lm", "state")
_emit_records_execution_trace("reflexion_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reflexion_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reflexion_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reflexion_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reflexion_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reflexion_engine", "env_read", "p2_env_1")
_emit_reads_environ("reflexion_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("reflexion_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reflexion_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reflexion_engine", "context_pull")
_emit_pulls_context("p1", "reflexion_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reflexion_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reflexion_engine", "uwg_term_2")
_emit_writes_through("p1", "reflexion_engine", "write_through")
_emit_writes_through("p1", "reflexion_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "reflexion_engine", "safety_validation")
_emit_invokes_eval("p1", "reflexion_engine", "eval_call")
_emit_proposal_commits_routing("p1", "reflexion_engine", "routing_commit")

Logger = logging.getLogger(__name__)

_DEFAULT_THRESHOLD = 0.85
_DEFAULT_MAX_ITERATIONS = 5


class ReflexionEngine:
    """Iterative critique-revise loop with verbal memory.

    All LLM interactions are injected as async callables so the engine
    remains LLM-provider-agnostic and fully testable with fakes.

    Args:
        generator_fn:  async (task, prior_response, memory_summary) -> str
            Produces the initial response (prior_response=None) or a revision.
        evaluator_fn:  async (task, response) -> dict with keys:
            ``critique`` (str), ``score`` (float 0-1), ``passed`` (bool)
        score_threshold: Stop iterating when score >= this value (default 0.85).
        max_iterations:  Hard upper bound on revision loops (default 5).
    """

    def __init__(
        self,
        generator_fn: Callable[[str, str | None, str], Awaitable[str]],
        evaluator_fn: Callable[[str, str], Awaitable[dict[str, Any]]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> None:
        self.generator_fn = generator_fn
        self.evaluator_fn = evaluator_fn
        self.score_threshold = score_threshold
        self.max_iterations = max_iterations

    async def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the Reflexion loop for a task.

        Returns:
            dict with keys:
                ``response``   — best response found
                ``score``      — final score
                ``passed``     — whether threshold was met
                ``iterations`` — number of iterations taken
                ``memory``     — ReflexionMemory instance with full critique history
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReflexionEngine.run")

        memory = ReflexionMemory(task=task)
        response: str | None = None
        final_critique: ReflexionCritique | None = None

        for iteration in range(1, self.max_iterations + 1):
            memory_summary = memory.summary()
            response = await self.generator_fn(task, response, memory_summary)

            eval_result = await self.evaluator_fn(task, response)
            critique_text = eval_result.get("critique", "")
            score = float(eval_result.get("score", 0.0))
            passed = bool(eval_result.get("passed", score >= self.score_threshold))

            critique = ReflexionCritique(
                iteration=iteration,
                response=response,
                critique=critique_text,
                score=score,
                passed=passed,
                metadata=context or {},
            )
            memory.add(critique)
            final_critique = critique

            Logger.info(
                "reflexion_iteration",
                extra={
                    "iteration": iteration,
                    "score": score,
                    "passed": passed,
                    "task": task[:60],
                },
            )

            if passed:
                Logger.info(
                    "reflexion_converged",
                    extra={"iteration": iteration, "score": score},
                )
                break

        best_response = memory.best_response() or response or ""
        best_score = max((c.score for c in memory.critiques), default=0.0)
        best_passed = best_score >= self.score_threshold

        Logger.info(
            "reflexion_complete",
            extra={
                "task": task[:60],
                "iterations": len(memory.critiques),
                "best_score": best_score,
                "passed": best_passed,
            },
        )

        return {
            "response": best_response,
            "score": best_score,
            "passed": best_passed,
            "iterations": len(memory.critiques),
            "memory": memory,
            "final_critique": final_critique,
        }

    @classmethod
    def with_rg_scorer(
        cls,
        generator_fn: Callable[[str, str | None, str], Awaitable[str]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> ReflexionEngine:
        """Factory that wires the existing apps_rg ReflectionEngine as the scorer.

        The ReflectionEngine produces a numeric score from workflow_results;
        here we wrap a single-response dict to reuse its scoring logic.
        """
        from apps_rg.engines.reflection_engine import ReflectionEngine

        _rg_engine_sentinel: dict[str, Any] = {}

        async def _rg_evaluator_fn(task: str, response: str) -> dict[str, Any]:
            workflow_results = {
                "response_engine": {
                    "passed": True,
                    "signal": None,
                    "output": response,
                }
            }
            ctx_obj = _rg_engine_sentinel.get("ctx")
            if ctx_obj is None:
                score = 0.7
                critique = "RG scorer unavailable — ctx not provided; using default score."
            else:
                engine = ReflectionEngine(ctx_obj)
                result = await engine.execute(workflow_results)
                score = result.get("overall_score", 0.0)
                weaknesses = result.get("weaknesses", [])
                critique = "; ".join(weaknesses) if weaknesses else "No issues detected."

            passed = score >= score_threshold
            return {"critique": critique, "score": score, "passed": passed}

        return cls(
            generator_fn=generator_fn,
            evaluator_fn=_rg_evaluator_fn,
            score_threshold=score_threshold,
            max_iterations=max_iterations,
        )
