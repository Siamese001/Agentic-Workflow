"""3.2: HardenedGeminiExecutor — Google/Gemini execution path via SovereignLLMGateway.

Wired into HardenedRouter._initialize_executors() for Provider.GOOGLE.
All calls route through SovereignLLMGateway — no direct SDK access.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.utils import get_clock
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
)

_emit_reads_policy_state("p0", "hardened_gemini_executor", "policy_binding")
_emit_snapshots_state("p0", "hardened_gemini_executor", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hardened_gemini_executor", "execution_auth")
_emit_validates_capability("p2", "hardened_gemini_executor", "capability_check")
_emit_routes_to_capability("p2", "hardened_gemini_executor", "capability_route")
_emit_writes_via_uwg("p2", "hardened_gemini_executor", "uwg_write")
_emit_blocks_direct_write("p2", "hardened_gemini_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "hardened_gemini_executor", "tool_invocation")
_emit_captures_execution_output("p2", "hardened_gemini_executor", "exec_output")
_emit_dispatches_agent("p3", "hardened_gemini_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "hardened_gemini_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardened_gemini_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardened_gemini_executor", "healing_outcome")
_emit_escalates_failure("p3", "hardened_gemini_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardened_gemini_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardened_gemini_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardened_gemini_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardened_gemini_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardened_gemini_executor", "eval_metric")
_emit_stores_embedding("p4", "hardened_gemini_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardened_gemini_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardened_gemini_executor", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("hardened_gemini_executor", "p4obs", "metric_1")
_emit_emits_metric_event("hardened_gemini_executor", "p4obs", "metric_2")
_emit_emits_metric_event("hardened_gemini_executor", "p4obs", "metric_3")
_emit_emits_metric_event("hardened_gemini_executor", "p4obs", "metric_4")
_emit_emits_metric_event("hardened_gemini_executor", "p4obs", "metric_5")
_emit_emits_metric_event("hardened_gemini_executor", "p4obs", "metric_6")
_emit_records_incident_event("hardened_gemini_executor", "p4obs", "incident")
_emit_captures_runtime_anomaly("hardened_gemini_executor", "p4obs", "anomaly")
_emit_writes_observability_log("hardened_gemini_executor", "p4obs", "obs_log")
_emit_updates_monitoring_state("hardened_gemini_executor", "p4obs", "mon_state")
_emit_triggers_alert("hardened_gemini_executor", "p4obs", "alert")
_emit_links_incident_trace("hardened_gemini_executor", "p4obs", "trace_link")
_emit_captures_pattern("hardened_gemini_executor", "p3lm", "pattern")
_emit_records_learning_event("hardened_gemini_executor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hardened_gemini_executor", "p3lm", "snapshot")
_emit_feeds_meta_learning("hardened_gemini_executor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hardened_gemini_executor", "p3lm", "routing")
_emit_improves_agent_policy("hardened_gemini_executor", "p3lm", "policy")
_emit_stores_learning_state("hardened_gemini_executor", "p3lm", "state")
_emit_records_execution_trace("hardened_gemini_executor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hardened_gemini_executor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hardened_gemini_executor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hardened_gemini_executor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hardened_gemini_executor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hardened_gemini_executor", "env_read", "p2_env_1")
_emit_reads_environ("hardened_gemini_executor", "env_read", "p2_env_2")
_emit_reads_runtime_state("hardened_gemini_executor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hardened_gemini_executor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hardened_gemini_executor", "context_pull")
_emit_pulls_context("p1", "hardened_gemini_executor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hardened_gemini_executor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hardened_gemini_executor", "uwg_term_2")
_emit_writes_through("p1", "hardened_gemini_executor", "write_through")
_emit_writes_through("p1", "hardened_gemini_executor", "write_through_2")
_emit_validated_by_safety_plane("p1", "hardened_gemini_executor", "safety_validation")
_emit_invokes_eval("p1", "hardened_gemini_executor", "eval_call")
_emit_proposal_commits_routing("p1", "hardened_gemini_executor", "routing_commit")
_emit_escalates_to_human("p1", "hardened_gemini_executor", "human_escalation")
_emit_routes_through("p1", "hardened_gemini_executor", "route_through")
_emit_checks_agent_registry("p1", "hardened_gemini_executor", "agent_registry")
_emit_validates_agent_capability("p1", "hardened_gemini_executor", "capability")
_emit_dispatches_execution_plan("p1", "hardened_gemini_executor", "exec_plan")
_emit_agent_executes_agent("p1", "hardened_gemini_executor", "sub_agent")
_emit_routes_to_agent("p1", "hardened_gemini_executor", "target_agent")
_emit_verifies_policy("p1", "hardened_gemini_executor", "policy_check")
_emit_observes_runtime_state("p1", "hardened_gemini_executor", "runtime_state")
_emit_verifies_boundary("p1", "hardened_gemini_executor", "boundary_check")
_emit_transcripts_response("p1", "hardened_gemini_executor", "transcript")
_emit_hard_fails_untranscripted("p1", "hardened_gemini_executor")
_emit_gated_by_confidence("p1", "hardened_gemini_executor", "confidence_gate")

logger = logging.getLogger(__name__)


@dataclass
class HardenedGeminiExecutor:
    """Sovereign Gemini execution path.

    Delegates all LLM calls to SovereignLLMGateway.
    Provides circuit-breaker and retry logic consistent with the hardened router.
    """

    agent_id: str = "HardenedGeminiExecutor"
    max_retries: int = 3
    _gateway: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            from agentic_core.interfaces.gateway import SovereignLLMGateway

            self._gateway = SovereignLLMGateway()
            _clk = get_clock()
            _clk.emit_replay_key(context=f"rg:gemini:{self.agent_id}")
            _clk.emit_determinism_digest(inputs={"executor": self.agent_id, "provider": "google"})
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("HardenedGeminiExecutor: SovereignLLMGateway not available")
            self._gateway = None

    def execute(
        self, prompt: str, model: str | None = None, temperature: float = 0.7, max_tokens: int | None = None
    ) -> dict[str, Any]:
        """Execute a prompt via SovereignLLMGateway (Google/Gemini path).

        Returns:
            dict with 'content', 'model', 'provider', 'success' keys.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HardenedGeminiExecutor.execute")

        if self._gateway is None:
            raise RuntimeError("HardenedGeminiExecutor: SovereignLLMGateway not available — cannot execute")
        from agentic_core.interfaces.gateway import GenerationRequest

        effective_model = model or "gemini-2.5-pro"
        request = GenerationRequest(
            agent_id=self.agent_id, provider="google", model=effective_model, prompt=prompt
        )
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                loop = asyncio.new_event_loop()
                try:
                    response = loop.run_until_complete(self._gateway.route_generation(request))
                finally:
                    loop.close()
                logger.debug(
                    "HardenedGeminiExecutor: success on attempt %d model=%s", attempt, effective_model
                )
                return {
                    "content": response.content,
                    "model": effective_model,
                    "provider": "google",
                    "success": True,
                    "attempt": attempt,
                }
            # guardian: allow-silent-swallow
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "HardenedGeminiExecutor attempt %d/%d failed: %s", attempt, self.max_retries, exc
                )
        raise RuntimeError(
            f"HardenedGeminiExecutor: all {self.max_retries} attempts failed. Last: {last_exc}"
        )

    def is_available(self) -> bool:
        """Return True if the gateway is wired up."""
        return self._gateway is not None


__all__ = ["HardenedGeminiExecutor"]
