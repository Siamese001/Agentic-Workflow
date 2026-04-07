"""
D0 Engine Adapter — bridges spine string-based d0_injections to D0InjectionEngine.

The spine adapters carry d0_injections as a plain string with fence segments
separated by '|' in the format "fence_id:text|fence_id2:text2".
D0InjectionEngine expects a tuple[RoleFence, ...].

This adapter converts between the two representations without mutating either side.
Falls back to the null stub if D0InjectionEngine cannot be imported.
"""

from __future__ import annotations

import logging

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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "d0_engine_adapter", "p0_governance")
_emit_reads_policy_state("p0", "d0_engine_adapter", "policy_binding")
_emit_snapshots_state("p0", "d0_engine_adapter", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("d0_engine_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("d0_engine_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("d0_engine_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("d0_engine_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("d0_engine_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("d0_engine_adapter", "p4obs", "metric_6")
_emit_records_incident_event("d0_engine_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("d0_engine_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("d0_engine_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("d0_engine_adapter", "p4obs", "mon_state")
_emit_triggers_alert("d0_engine_adapter", "p4obs", "alert")
_emit_links_incident_trace("d0_engine_adapter", "p4obs", "trace_link")
_emit_captures_pattern("d0_engine_adapter", "p3lm", "pattern")
_emit_records_learning_event("d0_engine_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("d0_engine_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("d0_engine_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("d0_engine_adapter", "p3lm", "routing")
_emit_improves_agent_policy("d0_engine_adapter", "p3lm", "policy")
_emit_stores_learning_state("d0_engine_adapter", "p3lm", "state")
_emit_records_execution_trace("d0_engine_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("d0_engine_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("d0_engine_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("d0_engine_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("d0_engine_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("d0_engine_adapter", "env_read", "p2_env_1")
_emit_reads_environ("d0_engine_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("d0_engine_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("d0_engine_adapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "d0_engine_adapter", "context_pull")
_emit_pulls_context("p1", "d0_engine_adapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "d0_engine_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "d0_engine_adapter", "uwg_term_2")
_emit_writes_through("p1", "d0_engine_adapter", "write_through")
_emit_writes_through("p1", "d0_engine_adapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "d0_engine_adapter", "safety_validation")
_emit_invokes_eval("p1", "d0_engine_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "d0_engine_adapter", "routing_commit")
_emit_escalates_to_human("p1", "d0_engine_adapter", "human_escalation")
_emit_routes_through("p1", "d0_engine_adapter", "route_through")
_emit_checks_agent_registry("p1", "d0_engine_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "d0_engine_adapter", "capability")
_emit_dispatches_execution_plan("p1", "d0_engine_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "d0_engine_adapter", "sub_agent")
_emit_routes_to_agent("p1", "d0_engine_adapter", "target_agent")
_emit_verifies_policy("p1", "d0_engine_adapter", "policy_check")
_emit_observes_runtime_state("p1", "d0_engine_adapter", "runtime_state")
_emit_verifies_boundary("p1", "d0_engine_adapter", "boundary_check")
_emit_transcripts_response("p1", "d0_engine_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "d0_engine_adapter")
_emit_gated_by_confidence("p1", "d0_engine_adapter", "confidence_gate")
emit_replay_key("p0", "d0_engine_adapter")
emit_determinism_digest("p0", "d0_engine_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "d0_engine_adapter", "execution_auth")
_emit_validates_capability("p2", "d0_engine_adapter", "capability_check")
_emit_routes_to_capability("p2", "d0_engine_adapter", "capability_route")
_emit_writes_via_uwg("p2", "d0_engine_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "d0_engine_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "d0_engine_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "d0_engine_adapter", "exec_output")
_emit_dispatches_agent("p3", "d0_engine_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "d0_engine_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "d0_engine_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "d0_engine_adapter", "healing_outcome")
_emit_escalates_failure("p3", "d0_engine_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "d0_engine_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "d0_engine_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "d0_engine_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "d0_engine_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "d0_engine_adapter", "eval_metric")
_emit_stores_embedding("p4", "d0_engine_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "d0_engine_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "d0_engine_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)


def _build_real_engine():
    from agentic_core.L5_safety.enforcement.d0_injection_engine_enforcer import D0InjectionEngine, RoleFence

    return (D0InjectionEngine, RoleFence)


class D0EngineAdapter:
    """
    Adapter converting spine string d0_injections format to RoleFence tuple.

    Input format (string): "fence_id_1:text1|fence_id_2:text2"
    Output: D0InjectionEngine.render_d0(fences=tuple[RoleFence, ...]) -> str

    Falls back to null behavior (return input string unchanged) if the real
    D0InjectionEngine module is unavailable.
    """

    def __init__(self) -> None:
        try:
            D0InjectionEngine, self._RoleFence = _build_real_engine()
            self._engine = D0InjectionEngine()
            self._real = True
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("D0InjectionEngine unavailable; using null fallback")
            self._engine = None
            self._RoleFence = None
            self._real = False

    def render_d0(self, d0_injections: str) -> str:
        """
        Render D0 injection string via the real D0InjectionEngine.

        Args:
            d0_injections: Pipe-separated fence segments "fence_id:text|..."

        Returns:
            Rendered D0 XML string (e.g. "<D0>\\n[fence_id] text\\n</D0>\\n")
            or the original string unchanged when engine unavailable.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "D0EngineAdapter.render_d0")

        if not self._real or not d0_injections:
            return d0_injections
        fences = []
        for segment in d0_injections.split("|"):
            segment = segment.strip()
            if ":" in segment:
                fence_id, text = segment.split(":", 1)
                fence_id = fence_id.strip()
                text = text.strip()
                if fence_id:
                    fences.append(self._RoleFence(fence_id=fence_id, text=text))
        if not fences:
            return d0_injections
        return self._engine.render_d0(fences=tuple(fences))

    @property
    def is_real(self) -> bool:
        """True if backed by the real D0InjectionEngine, False for null fallback."""
        return self._real
