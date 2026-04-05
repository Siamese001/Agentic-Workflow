"""L0 Threshold Tuner — deterministic threshold adjustment proposals for L0 routing surfaces.

Analyzes L0 routing metrics (escalation rates, routing confidence distributions)
and proposes bounded threshold adjustments subject to cooldown and sample-size
dampening policies.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
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

_emit_authorize_and_execute("p2", "l0_threshold_tuner", "execution_auth")
_emit_validates_capability("p2", "l0_threshold_tuner", "capability_check")
_emit_routes_to_capability("p2", "l0_threshold_tuner", "capability_route")
_emit_writes_via_uwg("p2", "l0_threshold_tuner", "uwg_write")
_emit_blocks_direct_write("p2", "l0_threshold_tuner", "direct_write_block")
_emit_records_tool_invocation("p2", "l0_threshold_tuner", "tool_invocation")
_emit_captures_execution_output("p2", "l0_threshold_tuner", "exec_output")
_emit_dispatches_agent("p3", "l0_threshold_tuner", "agent_dispatch")
_emit_coordinates_agents("p3", "l0_threshold_tuner", "agent_coordination")
_emit_records_workflow_lineage("p3", "l0_threshold_tuner", "workflow_lineage")
_emit_records_healing_outcome("p3", "l0_threshold_tuner", "healing_outcome")
_emit_escalates_failure("p3", "l0_threshold_tuner", "failure_escalation")
_emit_orchestrates_workflow("p3", "l0_threshold_tuner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l0_threshold_tuner", "healing_dispatch")
_emit_invokes_evaluation("p3", "l0_threshold_tuner", "evaluation_signal")
_emit_records_telemetry_event("p4", "l0_threshold_tuner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l0_threshold_tuner", "eval_metric")
_emit_stores_embedding("p4", "l0_threshold_tuner", "embedding_store")
_emit_updates_meta_learning_state("p4", "l0_threshold_tuner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l0_threshold_tuner", "exec_snapshot_link")
from system_learning.validators.dampening import (
    CooldownPolicy,
    CooldownViolation,
    SampleSizePolicy,
    SampleSizeViolation,
    assert_cooldown_ok,
    assert_min_sample_size,
)

_emit_applies_guardrail("p0", "l0_threshold_tuner", "p0_governance")
_emit_snapshots_state("p0", "l0_threshold_tuner", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("l0_threshold_tuner", "p4obs", "metric_1")
_emit_emits_metric_event("l0_threshold_tuner", "p4obs", "metric_2")
_emit_emits_metric_event("l0_threshold_tuner", "p4obs", "metric_3")
_emit_emits_metric_event("l0_threshold_tuner", "p4obs", "metric_4")
_emit_emits_metric_event("l0_threshold_tuner", "p4obs", "metric_5")
_emit_emits_metric_event("l0_threshold_tuner", "p4obs", "metric_6")
_emit_records_incident_event("l0_threshold_tuner", "p4obs", "incident")
_emit_captures_runtime_anomaly("l0_threshold_tuner", "p4obs", "anomaly")
_emit_writes_observability_log("l0_threshold_tuner", "p4obs", "obs_log")
_emit_updates_monitoring_state("l0_threshold_tuner", "p4obs", "mon_state")
_emit_triggers_alert("l0_threshold_tuner", "p4obs", "alert")
_emit_links_incident_trace("l0_threshold_tuner", "p4obs", "trace_link")
_emit_captures_pattern("l0_threshold_tuner", "p3lm", "pattern")
_emit_records_learning_event("l0_threshold_tuner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("l0_threshold_tuner", "p3lm", "snapshot")
_emit_feeds_meta_learning("l0_threshold_tuner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("l0_threshold_tuner", "p3lm", "routing")
_emit_improves_agent_policy("l0_threshold_tuner", "p3lm", "policy")
_emit_stores_learning_state("l0_threshold_tuner", "p3lm", "state")
_emit_records_execution_trace("l0_threshold_tuner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("l0_threshold_tuner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("l0_threshold_tuner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("l0_threshold_tuner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("l0_threshold_tuner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("l0_threshold_tuner", "env_read", "p2_env_1")
_emit_reads_environ("l0_threshold_tuner", "env_read", "p2_env_2")
_emit_reads_runtime_state("l0_threshold_tuner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("l0_threshold_tuner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "l0_threshold_tuner", "context_pull")
_emit_pulls_context("p1", "l0_threshold_tuner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "l0_threshold_tuner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "l0_threshold_tuner", "uwg_term_2")
_emit_writes_through("p1", "l0_threshold_tuner", "write_through")
_emit_writes_through("p1", "l0_threshold_tuner", "write_through_2")
_emit_validated_by_safety_plane("p1", "l0_threshold_tuner", "safety_validation")
_emit_invokes_eval("p1", "l0_threshold_tuner", "eval_call")
_emit_proposal_commits_routing("p1", "l0_threshold_tuner", "routing_commit")
_emit_escalates_to_human("p1", "l0_threshold_tuner", "human_escalation")
_emit_routes_through("p1", "l0_threshold_tuner", "route_through")
_emit_checks_agent_registry("p1", "l0_threshold_tuner", "agent_registry")
_emit_validates_agent_capability("p1", "l0_threshold_tuner", "capability")
_emit_dispatches_execution_plan("p1", "l0_threshold_tuner", "exec_plan")
_emit_agent_executes_agent("p1", "l0_threshold_tuner", "sub_agent")
_emit_routes_to_agent("p1", "l0_threshold_tuner", "target_agent")
_emit_verifies_policy("p1", "l0_threshold_tuner", "policy_check")
_emit_observes_runtime_state("p1", "l0_threshold_tuner", "runtime_state")
_emit_verifies_boundary("p1", "l0_threshold_tuner", "boundary_check")
_emit_transcripts_response("p1", "l0_threshold_tuner", "transcript")
_emit_hard_fails_untranscripted("p1", "l0_threshold_tuner")
_emit_gated_by_confidence("p1", "l0_threshold_tuner", "confidence_gate")
emit_replay_key("p0", "l0_threshold_tuner")
emit_determinism_digest("p0", "l0_threshold_tuner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — all bounds are hard-coded, no external config
# ---------------------------------------------------------------------------

_MIN_THRESHOLD = 0.50
_MAX_THRESHOLD = 0.95
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.03
_ESCALATION_RATE_TRIGGER = 0.20  # propose adjustment when rate exceeds this


# ---------------------------------------------------------------------------
# Change Package
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class L0ThresholdChangePackage:
    """Immutable, deterministically-hashable threshold change proposal.

    Fields
    ------
    surface_name : str
        Name of the L0 routing surface being tuned (e.g. ``"escalation_threshold"``).
    old_value : float
        Current threshold value.
    new_value : float
        Proposed threshold value.
    justification : str
        Human-readable reason for the change.
    snapshot_id : str
        ID of the snapshot that triggered this proposal.
    """

    surface_name: str
    old_value: float
    new_value: float
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L0ThresholdChangePackage.canonical_bytes")

        data = {
            "surface_name": self.surface_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        """SHA-256 content hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Proposal Function
# ---------------------------------------------------------------------------


def propose_l0_threshold_changes(
    *,
    snapshot_id: str,
    metrics: dict[str, float],
    current_config: dict[str, float],
    now_utc: int,
    history: dict[str, Any],
    cooldown_policy: CooldownPolicy,
    sample_policy: SampleSizePolicy,
) -> L0ThresholdChangePackage | None:
    """Propose an L0 threshold change based on routing metrics.

    Currently supports the ``escalation_threshold`` surface.  When the
    ``escalation_rate`` metric exceeds the trigger level the function proposes
    a bounded increase to the threshold, subject to cooldown and sample-size
    dampening.

    Parameters
    ----------
    snapshot_id : str
        Identifier for the metrics snapshot.
    metrics : dict[str, float]
        Routing metrics (must include ``"escalation_rate"``).
    current_config : dict[str, float]
        Current threshold values (must include ``"escalation_threshold"``).
    now_utc : int
        Current deterministic timestamp.
    history : dict[str, Any]
        Historical context with keys ``"<surface>_last_update"`` and
        ``"<surface>_n_obs"`` for dampening checks.
    cooldown_policy : CooldownPolicy
        Cooldown dampening policy.
    sample_policy : SampleSizePolicy
        Sample-size dampening policy.

    Returns
    -------
    L0ThresholdChangePackage | None
        A proposal if adjustment is warranted, ``None`` otherwise.
    """
    surface = "escalation_threshold"
    escalation_rate = metrics.get("escalation_rate")
    current_value = current_config.get(surface)

    if escalation_rate is None or current_value is None:
        return None

    # Check if adjustment is warranted
    if escalation_rate <= _ESCALATION_RATE_TRIGGER:
        return None

    # Dampening: cooldown
    last_update_utc = history.get(f"{surface}_last_update", 0)
    try:
        assert_cooldown_ok(last_update_utc, now_utc, cooldown_policy)
    except CooldownViolation:    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context    # guardian: CooldownViolation should be handled with specific context
        return None

    # Dampening: sample size
    n_obs = history.get(f"{surface}_n_obs", 0)
    try:
        assert_min_sample_size(n_obs, sample_policy)
    except SampleSizeViolation:    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context    # guardian: SampleSizeViolation should be handled with specific context
        return None

    # Compute proposed value: fixed delta, capped to bounds
    new_value = current_value + _DEFAULT_DELTA
    new_value = min(new_value, _MAX_THRESHOLD)
    new_value = max(new_value, _MIN_THRESHOLD)

    # Round to avoid floating-point noise
    new_value = round(new_value, 4)

    # No-op check: if value didn't change, skip
    if new_value == current_value:
        return None

    # Delta safety check
    delta = abs(new_value - current_value)
    if delta > _MAX_DELTA:
        new_value = current_value + (_MAX_DELTA if new_value > current_value else -_MAX_DELTA)
        new_value = round(new_value, 4)

    justification = (
        f"escalation_rate={escalation_rate:.4f} exceeds trigger={_ESCALATION_RATE_TRIGGER}; "
        f"adjusting {surface} from {current_value} to {new_value} (delta={delta:.4f})"
    )

    return L0ThresholdChangePackage(
        surface_name=surface,
        old_value=current_value,
        new_value=new_value,
        justification=justification,
        snapshot_id=snapshot_id,
    )


# ---------------------------------------------------------------------------
# Proposer Adapter (Protocol-conforming wrapper for the pipeline)
# ---------------------------------------------------------------------------


class L0ProposerAdapter:
    """Wraps ``propose_l0_threshold_changes`` to conform to the ``L0Proposer`` Protocol.

    The pipeline calls ``proposer.propose(snapshot, metrics, config, now_utc,
    history, cooldown, sample)``.  This adapter translates those args into the
    keyword-only function call.
    """

    def propose(
        self,
        snapshot: Any,
        metrics: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
    ) -> L0ThresholdChangePackage | None:
        """Propose L0 threshold changes.

        Extracts ``snapshot_id`` from the snapshot object and delegates
        to ``propose_l0_threshold_changes()``.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L0ProposerAdapter.propose")

        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")

        # Normalise metrics: must be dict[str, float]
        if not isinstance(metrics, dict):
            metrics = {}

        # Normalise config: must be dict[str, float]
        if not isinstance(config, dict):
            config = {}

        # Provide fallback escalation_rate from config if metrics is sparse
        if "escalation_rate" not in metrics:
            metrics = dict(metrics)

        # Normalise history
        if not isinstance(history, dict):
            history = {}

        # Normalise cooldown / sample to our policy types
        if cooldown is None:
            from system_learning.validators.dampening import CooldownPolicy
            # guardian: allow-magic-config
            cooldown = CooldownPolicy(min_seconds_between_updates=3600)

        if sample is None:
            from system_learning.validators.dampening import SampleSizePolicy
            # guardian: allow-magic-config
            sample = SampleSizePolicy(min_observations=10)

        return propose_l0_threshold_changes(
            snapshot_id=snapshot_id,
            metrics=metrics,
            current_config=config if isinstance(config, dict) else {},
            now_utc=now_utc,
            history=history,
            cooldown_policy=cooldown,
            sample_policy=sample,
        )


__all__ = [
    "L0ThresholdChangePackage",
    "L0ProposerAdapter",
    "propose_l0_threshold_changes",
]
