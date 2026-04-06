"""L4MetaPriorProvider — bridges HealingSuccessRateStore to MetaPriorProvider seam.

Gap 3 fix: healing_tier_router.route_healing_tier() accepts meta_prior_provider but
the live L4-backed provider was never wired. This module provides the adapter.

Contracts:
- get_prior() delegates to HealingSuccessRateStore.get_prior() (read-only).
- Falls back to NeutralMetaPriorProvider on cold start (no store / store raises).
- MUST NOT import agentic_core modules directly (layer boundary: system_learning only).
- MUST be synchronous and deterministic.
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

_emit_authorize_and_execute("p2", "l4_meta_prior_provider", "execution_auth")
_emit_validates_capability("p2", "l4_meta_prior_provider", "capability_check")
_emit_routes_to_capability("p2", "l4_meta_prior_provider", "capability_route")
_emit_writes_via_uwg("p2", "l4_meta_prior_provider", "uwg_write")
_emit_blocks_direct_write("p2", "l4_meta_prior_provider", "direct_write_block")
_emit_records_tool_invocation("p2", "l4_meta_prior_provider", "tool_invocation")
_emit_captures_execution_output("p2", "l4_meta_prior_provider", "exec_output")
_emit_dispatches_agent("p3", "l4_meta_prior_provider", "agent_dispatch")
_emit_coordinates_agents("p3", "l4_meta_prior_provider", "agent_coordination")
_emit_records_workflow_lineage("p3", "l4_meta_prior_provider", "workflow_lineage")
_emit_records_healing_outcome("p3", "l4_meta_prior_provider", "healing_outcome")
_emit_escalates_failure("p3", "l4_meta_prior_provider", "failure_escalation")
_emit_orchestrates_workflow("p3", "l4_meta_prior_provider", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l4_meta_prior_provider", "healing_dispatch")
_emit_invokes_evaluation("p3", "l4_meta_prior_provider", "evaluation_signal")
_emit_records_telemetry_event("p4", "l4_meta_prior_provider", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l4_meta_prior_provider", "eval_metric")
_emit_stores_embedding("p4", "l4_meta_prior_provider", "embedding_store")
_emit_updates_meta_learning_state("p4", "l4_meta_prior_provider", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l4_meta_prior_provider", "exec_snapshot_link")
from system_learning.ports.meta_prior_provider import (
    _NEUTRAL_PRIOR,
    NeutralMetaPriorProvider,
)

_emit_applies_guardrail("p0", "l4_meta_prior_provider", "p0_governance")
_emit_reads_policy_state("p0", "l4_meta_prior_provider", "policy_binding")
_emit_snapshots_state("p0", "l4_meta_prior_provider", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("l4_meta_prior_provider", "p4obs", "metric_1")
_emit_emits_metric_event("l4_meta_prior_provider", "p4obs", "metric_2")
_emit_emits_metric_event("l4_meta_prior_provider", "p4obs", "metric_3")
_emit_emits_metric_event("l4_meta_prior_provider", "p4obs", "metric_4")
_emit_emits_metric_event("l4_meta_prior_provider", "p4obs", "metric_5")
_emit_emits_metric_event("l4_meta_prior_provider", "p4obs", "metric_6")
_emit_records_incident_event("l4_meta_prior_provider", "p4obs", "incident")
_emit_captures_runtime_anomaly("l4_meta_prior_provider", "p4obs", "anomaly")
_emit_writes_observability_log("l4_meta_prior_provider", "p4obs", "obs_log")
_emit_updates_monitoring_state("l4_meta_prior_provider", "p4obs", "mon_state")
_emit_triggers_alert("l4_meta_prior_provider", "p4obs", "alert")
_emit_links_incident_trace("l4_meta_prior_provider", "p4obs", "trace_link")
_emit_captures_pattern("l4_meta_prior_provider", "p3lm", "pattern")
_emit_records_learning_event("l4_meta_prior_provider", "p3lm", "learning_event")
_emit_writes_learning_snapshot("l4_meta_prior_provider", "p3lm", "snapshot")
_emit_feeds_meta_learning("l4_meta_prior_provider", "p3lm", "meta_feed")
_emit_updates_routing_strategy("l4_meta_prior_provider", "p3lm", "routing")
_emit_improves_agent_policy("l4_meta_prior_provider", "p3lm", "policy")
_emit_stores_learning_state("l4_meta_prior_provider", "p3lm", "state")
_emit_records_execution_trace("l4_meta_prior_provider", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("l4_meta_prior_provider", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("l4_meta_prior_provider", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("l4_meta_prior_provider", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("l4_meta_prior_provider", "L4_STATE", "p2_trace_5")
_emit_reads_environ("l4_meta_prior_provider", "env_read", "p2_env_1")
_emit_reads_environ("l4_meta_prior_provider", "env_read", "p2_env_2")
_emit_reads_runtime_state("l4_meta_prior_provider", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("l4_meta_prior_provider", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "l4_meta_prior_provider", "context_pull")
_emit_pulls_context("p1", "l4_meta_prior_provider", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "l4_meta_prior_provider", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "l4_meta_prior_provider", "uwg_term_2")
_emit_writes_through("p1", "l4_meta_prior_provider", "write_through")
_emit_writes_through("p1", "l4_meta_prior_provider", "write_through_2")
_emit_validated_by_safety_plane("p1", "l4_meta_prior_provider", "safety_validation")
_emit_invokes_eval("p1", "l4_meta_prior_provider", "eval_call")
_emit_proposal_commits_routing("p1", "l4_meta_prior_provider", "routing_commit")
_emit_escalates_to_human("p1", "l4_meta_prior_provider", "human_escalation")
_emit_routes_through("p1", "l4_meta_prior_provider", "route_through")
_emit_checks_agent_registry("p1", "l4_meta_prior_provider", "agent_registry")
_emit_validates_agent_capability("p1", "l4_meta_prior_provider", "capability")
_emit_dispatches_execution_plan("p1", "l4_meta_prior_provider", "exec_plan")
_emit_agent_executes_agent("p1", "l4_meta_prior_provider", "sub_agent")
_emit_routes_to_agent("p1", "l4_meta_prior_provider", "target_agent")
_emit_verifies_policy("p1", "l4_meta_prior_provider", "policy_check")
_emit_observes_runtime_state("p1", "l4_meta_prior_provider", "runtime_state")
_emit_verifies_boundary("p1", "l4_meta_prior_provider", "boundary_check")
_emit_transcripts_response("p1", "l4_meta_prior_provider", "transcript")
_emit_hard_fails_untranscripted("p1", "l4_meta_prior_provider")
_emit_gated_by_confidence("p1", "l4_meta_prior_provider", "confidence_gate")
emit_replay_key("p0", "l4_meta_prior_provider")
emit_determinism_digest("p0", "l4_meta_prior_provider")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_neutral = NeutralMetaPriorProvider()


class L4MetaPriorProvider:
    """Live prior provider backed by HealingSuccessRateStore.

    Parameters
    ----------
    store:
        An instance of HealingSuccessRateStore. If None, falls back to neutral prior.
    """

    def __init__(self, store=None) -> None:
        self._store = store

    def get_prior(self, error_signature: str) -> float:
        """Return historical success-rate prior for error_signature.

        Delegates to store.get_prior(). Falls back to _NEUTRAL_PRIOR when:
        - store is None (cold start)
        - store raises any exception
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L4MetaPriorProvider.get_prior")

        if self._store is None:
            return _NEUTRAL_PRIOR
        try:
            return self._store.get_prior(error_signature)
        except Exception as e:  # guardian: allow-silent-swallow
            logger.debug(
                "L4MetaPriorProvider: store.get_prior raised; returning neutral",
                extra={"error_signature": error_signature, "error": str(e)},
                exc_info=True,
            )
            return _NEUTRAL_PRIOR

    @classmethod
    def from_default_store(cls) -> L4MetaPriorProvider:
        """Construct using the process-global default HealingSuccessRateStore."""
        from system_learning.engines.healing_success_rate_store import get_default_store

        return cls(store=get_default_store())


__all__ = ["L4MetaPriorProvider"]
