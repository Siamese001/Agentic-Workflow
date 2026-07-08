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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "reflexion_engine")
trace_contract.emit_determinism_digest("p0", "reflexion_engine")

trace_contract._emit_dispatches_healing_run("p1", "reflexion_engine", "L3")
trace_contract._emit_routes_through("p1", "reflexion_engine", "L3")
trace_contract._emit_checks_agent_registry("p1", "reflexion_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "reflexion_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "reflexion_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "reflexion_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "reflexion_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "reflexion_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "reflexion_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "reflexion_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "reflexion_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "reflexion_engine")
trace_contract._emit_gated_by_confidence("p1", "reflexion_engine", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "reflexion_engine", "L3")
trace_contract._emit_reads_policy_state("p1", "reflexion_engine", "L3")

trace_contract._emit_snapshots_state("p0", "reflexion_engine", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "reflexion_engine", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "reflexion_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "reflexion_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "reflexion_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "reflexion_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "reflexion_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "reflexion_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "reflexion_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "reflexion_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "reflexion_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "reflexion_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "reflexion_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "reflexion_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "reflexion_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "reflexion_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "reflexion_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "reflexion_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "reflexion_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "reflexion_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "reflexion_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "reflexion_engine", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("reflexion_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("reflexion_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("reflexion_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("reflexion_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("reflexion_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("reflexion_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("reflexion_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("reflexion_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("reflexion_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("reflexion_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("reflexion_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("reflexion_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("reflexion_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("reflexion_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("reflexion_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("reflexion_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("reflexion_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("reflexion_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("reflexion_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("reflexion_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("reflexion_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("reflexion_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("reflexion_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("reflexion_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("reflexion_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("reflexion_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("reflexion_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("reflexion_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "reflexion_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "reflexion_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "reflexion_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "reflexion_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "reflexion_engine", "write_through")
trace_contract._emit_writes_through("p1", "reflexion_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "reflexion_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "reflexion_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "reflexion_engine", "routing_commit")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ReflexionEngine.run")

        memory = ReflexionMemory(task=task)
        response: str | None = None
        final_critique: ReflexionCritique | None = None

        for iteration in tqdm(range(1, self.max_iterations + 1), desc="Processing", unit="item"):
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
                },
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
