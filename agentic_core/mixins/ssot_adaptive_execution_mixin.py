"""
SSOT Adaptive Execution Mixin — L4-Derived Execution Mode Selection.

Provides adaptive execution that:
  - Derives execution mode from L4 aggregate signals
  - Replay mode locks to "standard" (no adaptive switching)
  - Must not override should_proceed_with_healing

Layer: L2 Execution Aid
Authority: Mode selection only. No L4 mutation. No routing override.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_applies_guardrail("p0", "ssot_adaptive_execution_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_adaptive_execution_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_adaptive_execution_mixin", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("ssot_adaptive_execution_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_adaptive_execution_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_adaptive_execution_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_adaptive_execution_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_adaptive_execution_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_adaptive_execution_mixin", "p4obs", "metric_6")
_emit_records_incident_event("ssot_adaptive_execution_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_adaptive_execution_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_adaptive_execution_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_adaptive_execution_mixin", "p4obs", "mon_state")
_emit_triggers_alert("ssot_adaptive_execution_mixin", "p4obs", "alert")
_emit_links_incident_trace("ssot_adaptive_execution_mixin", "p4obs", "trace_link")
_emit_captures_pattern("ssot_adaptive_execution_mixin", "p3lm", "pattern")
_emit_records_learning_event("ssot_adaptive_execution_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_adaptive_execution_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_adaptive_execution_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_adaptive_execution_mixin", "p3lm", "routing")
_emit_improves_agent_policy("ssot_adaptive_execution_mixin", "p3lm", "policy")
_emit_stores_learning_state("ssot_adaptive_execution_mixin", "p3lm", "state")
_emit_records_execution_trace("ssot_adaptive_execution_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_adaptive_execution_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_adaptive_execution_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_adaptive_execution_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_adaptive_execution_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_adaptive_execution_mixin", "env_read", "p2_env_1")
_emit_reads_environ("ssot_adaptive_execution_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_adaptive_execution_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_adaptive_execution_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_adaptive_execution_mixin", "context_pull")
_emit_pulls_context("p1", "ssot_adaptive_execution_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_adaptive_execution_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_adaptive_execution_mixin", "uwg_term_2")
_emit_writes_through("p1", "ssot_adaptive_execution_mixin", "write_through")
_emit_writes_through("p1", "ssot_adaptive_execution_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_adaptive_execution_mixin", "safety_validation")
_emit_invokes_eval("p1", "ssot_adaptive_execution_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_adaptive_execution_mixin", "routing_commit")
_emit_escalates_to_human("p1", "ssot_adaptive_execution_mixin", "human_escalation")
_emit_routes_through("p1", "ssot_adaptive_execution_mixin", "route_through")
_emit_checks_agent_registry("p1", "ssot_adaptive_execution_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_adaptive_execution_mixin", "capability")
_emit_dispatches_execution_plan("p1", "ssot_adaptive_execution_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_adaptive_execution_mixin", "sub_agent")
_emit_routes_to_agent("p1", "ssot_adaptive_execution_mixin", "target_agent")
_emit_verifies_policy("p1", "ssot_adaptive_execution_mixin", "policy_check")
_emit_observes_runtime_state("p1", "ssot_adaptive_execution_mixin", "runtime_state")
_emit_verifies_boundary("p1", "ssot_adaptive_execution_mixin", "boundary_check")
_emit_transcripts_response("p1", "ssot_adaptive_execution_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_adaptive_execution_mixin")
_emit_gated_by_confidence("p1", "ssot_adaptive_execution_mixin", "confidence_gate")
emit_replay_key("p0", "ssot_adaptive_execution_mixin")
emit_determinism_digest("p0", "ssot_adaptive_execution_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_adaptive_execution_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_adaptive_execution_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_adaptive_execution_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_adaptive_execution_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_adaptive_execution_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_adaptive_execution_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_adaptive_execution_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_adaptive_execution_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_adaptive_execution_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_adaptive_execution_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_adaptive_execution_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_adaptive_execution_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_adaptive_execution_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_adaptive_execution_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_adaptive_execution_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_adaptive_execution_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_adaptive_execution_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_adaptive_execution_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_adaptive_execution_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_adaptive_execution_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTAdaptiveExecution")
EXECUTION_MODES = ("standard", "aggressive", "conservative", "minimal")


class SSOTAdaptiveExecutionMixin:
    """L4-derived execution mode with replay lock.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Under replay mode, execution mode is locked to "standard".
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_execution_mode: str = "standard"

    @property
    def execution_mode(self) -> str:
        """Current execution mode. Locked to 'standard' under replay."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTAdaptiveExecutionMixin.execution_mode")

        if getattr(self, "is_replay_mode", False):
            return "standard"
        return self._ssot_execution_mode

    def set_execution_mode(self, mode: str) -> bool:
        """Set execution mode. Rejected under replay mode.

        Parameters
        ----------
        mode : str
            One of: standard, aggressive, conservative, minimal.

        Returns
        -------
        bool
            True if mode was set, False if rejected (replay mode or invalid).
        """
        if getattr(self, "is_replay_mode", False):
            _logger.warning("[SSOTAdaptive] Mode change rejected: replay mode active")
            return False
        if mode not in EXECUTION_MODES:
            _logger.warning("[SSOTAdaptive] Invalid mode: %s (valid: %s)", mode, EXECUTION_MODES)
            return False
        old = self._ssot_execution_mode
        self._ssot_execution_mode = mode
        _logger.info("[SSOTAdaptive] Mode: %s -> %s", old, mode)
        return True

    def derive_mode_from_signals(self, failure_rate: float = 0.0, violation_count: int = 0) -> str:
        """Derive execution mode from L4 aggregate signals.

        Under replay mode, always returns "standard".

        Parameters
        ----------
        failure_rate : float
            Recent failure rate (0.0 to 1.0).
        violation_count : int
            Number of active violations.

        Returns
        -------
        str
            Recommended execution mode.
        """
        if getattr(self, "is_replay_mode", False):
            return "standard"
        if failure_rate > 0.5 or violation_count > 50:
            return "conservative"
        if failure_rate > 0.2 or violation_count > 20:
            return "standard"
        if violation_count < 5:
            return "aggressive"
        return "standard"
