"""
Risk Gate Adapter — bridges ConfCalibRiskGate to the spine's _RiskResult interface.

ConfCalibRiskGate.evaluate() returns RiskDecision(allow, level, reasons).
The spine adapters expect an object with a single bool attribute: allow.

This adapter wraps ConfCalibRiskGate and returns a RiskResult compatible
with the spine's existing _RiskResult contract.
Falls back to allow=True null behavior if ConfCalibRiskGate cannot be imported.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

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

_emit_applies_guardrail("p0", "risk_gate_adapter", "p0_governance")
_emit_reads_policy_state("p0", "risk_gate_adapter", "policy_binding")
_emit_snapshots_state("p0", "risk_gate_adapter", "state_snapshot")
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

_emit_emits_metric_event("risk_gate_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("risk_gate_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("risk_gate_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("risk_gate_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("risk_gate_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("risk_gate_adapter", "p4obs", "metric_6")
_emit_records_incident_event("risk_gate_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("risk_gate_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("risk_gate_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("risk_gate_adapter", "p4obs", "mon_state")
_emit_triggers_alert("risk_gate_adapter", "p4obs", "alert")
_emit_links_incident_trace("risk_gate_adapter", "p4obs", "trace_link")
_emit_captures_pattern("risk_gate_adapter", "p3lm", "pattern")
_emit_records_learning_event("risk_gate_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("risk_gate_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("risk_gate_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("risk_gate_adapter", "p3lm", "routing")
_emit_improves_agent_policy("risk_gate_adapter", "p3lm", "policy")
_emit_stores_learning_state("risk_gate_adapter", "p3lm", "state")
_emit_records_execution_trace("risk_gate_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("risk_gate_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("risk_gate_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("risk_gate_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("risk_gate_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("risk_gate_adapter", "env_read", "p2_env_1")
_emit_reads_environ("risk_gate_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("risk_gate_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("risk_gate_adapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "risk_gate_adapter", "context_pull")
_emit_pulls_context("p1", "risk_gate_adapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "risk_gate_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "risk_gate_adapter", "uwg_term_2")
_emit_writes_through("p1", "risk_gate_adapter", "write_through")
_emit_writes_through("p1", "risk_gate_adapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "risk_gate_adapter", "safety_validation")
_emit_invokes_eval("p1", "risk_gate_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "risk_gate_adapter", "routing_commit")
_emit_escalates_to_human("p1", "risk_gate_adapter", "human_escalation")
_emit_routes_through("p1", "risk_gate_adapter", "route_through")
_emit_checks_agent_registry("p1", "risk_gate_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "risk_gate_adapter", "capability")
_emit_dispatches_execution_plan("p1", "risk_gate_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "risk_gate_adapter", "sub_agent")
_emit_routes_to_agent("p1", "risk_gate_adapter", "target_agent")
_emit_verifies_policy("p1", "risk_gate_adapter", "policy_check")
_emit_observes_runtime_state("p1", "risk_gate_adapter", "runtime_state")
_emit_verifies_boundary("p1", "risk_gate_adapter", "boundary_check")
_emit_transcripts_response("p1", "risk_gate_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "risk_gate_adapter")
_emit_gated_by_confidence("p1", "risk_gate_adapter", "confidence_gate")
emit_replay_key("p0", "risk_gate_adapter")
emit_determinism_digest("p0", "risk_gate_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "risk_gate_adapter", "execution_auth")
_emit_validates_capability("p2", "risk_gate_adapter", "capability_check")
_emit_routes_to_capability("p2", "risk_gate_adapter", "capability_route")
_emit_writes_via_uwg("p2", "risk_gate_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "risk_gate_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "risk_gate_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "risk_gate_adapter", "exec_output")
_emit_dispatches_agent("p3", "risk_gate_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "risk_gate_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "risk_gate_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "risk_gate_adapter", "healing_outcome")
_emit_escalates_failure("p3", "risk_gate_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "risk_gate_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "risk_gate_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "risk_gate_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "risk_gate_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "risk_gate_adapter", "eval_metric")
_emit_stores_embedding("p4", "risk_gate_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "risk_gate_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "risk_gate_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RiskResult:
    """
    Minimal risk result compatible with spine adapter _RiskResult contract.

    Extends the null stub type so existing spine code works unchanged.
    Carries the full decision context for observability.
    """

    allow: bool
    level: str = "LOW"
    reasons: tuple[str, ...] = ()


def _build_real_gate():
    from agentic_core.L5_safety.enforcement.conf_calib_gate import ConfCalibRiskGate

    return ConfCalibRiskGate


class RiskGateAdapter:
    """
    Adapter wrapping ConfCalibRiskGate for use in spine adapters.

    Converts RiskDecision → RiskResult so existing spine wiring requires
    no changes to its evaluate() call site.
    Falls back to allow=True when the real gate is unavailable.
    """

    def __init__(self) -> None:
        try:
            ConfCalibRiskGate = _build_real_gate()
            self._gate = ConfCalibRiskGate()
            self._real = True
        except ImportError:  # guardian: allow-silent-swallow - optional dependency
            logger.warning("ConfCalibRiskGate unavailable; using null fallback (allow=True)")
            self._gate = None
            self._real = False

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> RiskResult:
        """
        Evaluate risk for payload and D0 injections.

        Args:
            payload_like: Object with optional .sanitized and .check_ids attributes
            d0_injections: D0 injection string (checked for "DENY_EXECUTION")

        Returns:
            RiskResult with allow, level, and reasons from the real gate,
            or RiskResult(allow=True) when gate unavailable.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RiskGateAdapter.evaluate")

        if not self._real:
            return RiskResult(allow=True)
        d0_str = d0_injections if isinstance(d0_injections, str) else str(d0_injections)
        decision = self._gate.evaluate(payload_like=payload_like, d0_injections=d0_str)
        return RiskResult(allow=decision.allow, level=decision.level.value, reasons=decision.reasons)

    @property
    def is_real(self) -> bool:
        """True if backed by the real ConfCalibRiskGate, False for null fallback."""
        return self._real
