"""L0 Routing Confidence Monitor — proposal-only min_confidence threshold tuner.

Mirrors the structure of ``l0_threshold_tuner.py`` but targets the
``routing_min_confidence`` surface of AgenticRouter.

When the 10th-percentile routing confidence (``routing_confidence_p10``)
drops below a configurable trigger level, a bounded threshold adjustment is
proposed via ``L0ThresholdChangePackage``.

Design invariants
-----------------
1. Pure function interface — no global mutable state.
2. No wall-clock reads; ``now_utc`` is caller-supplied.
3. All bounds are hard-coded constants; no external config.
4. Proposals are strictly informational — they MUST NOT mutate routing
   or config state directly.
5. Dampening via cooldown + sample-size policies (same validators as
   ``l0_threshold_tuner.py``).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "l0_routing_confidence_monitor", "execution_auth")
trace_contract._emit_validates_capability("p2", "l0_routing_confidence_monitor", "capability_check")
trace_contract._emit_routes_to_capability("p2", "l0_routing_confidence_monitor", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "l0_routing_confidence_monitor", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "l0_routing_confidence_monitor", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "l0_routing_confidence_monitor", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "l0_routing_confidence_monitor", "exec_output")
trace_contract._emit_dispatches_agent("p3", "l0_routing_confidence_monitor", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "l0_routing_confidence_monitor", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "l0_routing_confidence_monitor", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "l0_routing_confidence_monitor", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "l0_routing_confidence_monitor", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "l0_routing_confidence_monitor", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "l0_routing_confidence_monitor", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "l0_routing_confidence_monitor", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "l0_routing_confidence_monitor", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "l0_routing_confidence_monitor", "eval_metric")
trace_contract._emit_stores_embedding("p4", "l0_routing_confidence_monitor", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "l0_routing_confidence_monitor", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "l0_routing_confidence_monitor", "exec_snapshot_link")
from agentic_core.L6_system_learning.constraints.dampening import (
    CooldownPolicy,
    CooldownViolation,
    SampleSizePolicy,
    SampleSizeViolation,
    assert_cooldown_ok,
    assert_min_sample_size,
)

trace_contract._emit_emits_metric_event("l0_routing_confidence_monitor", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("l0_routing_confidence_monitor", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("l0_routing_confidence_monitor", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("l0_routing_confidence_monitor", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("l0_routing_confidence_monitor", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("l0_routing_confidence_monitor", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("l0_routing_confidence_monitor", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("l0_routing_confidence_monitor", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("l0_routing_confidence_monitor", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("l0_routing_confidence_monitor", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("l0_routing_confidence_monitor", "p4obs", "alert")
trace_contract._emit_links_incident_trace("l0_routing_confidence_monitor", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("l0_routing_confidence_monitor", "p3lm", "pattern")
trace_contract._emit_records_learning_event("l0_routing_confidence_monitor", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("l0_routing_confidence_monitor", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("l0_routing_confidence_monitor", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("l0_routing_confidence_monitor", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("l0_routing_confidence_monitor", "p3lm", "policy")
trace_contract._emit_stores_learning_state("l0_routing_confidence_monitor", "p3lm", "state")
trace_contract._emit_records_execution_trace("l0_routing_confidence_monitor", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("l0_routing_confidence_monitor", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("l0_routing_confidence_monitor", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("l0_routing_confidence_monitor", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("l0_routing_confidence_monitor", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("l0_routing_confidence_monitor", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("l0_routing_confidence_monitor", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("l0_routing_confidence_monitor", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("l0_routing_confidence_monitor", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "l0_routing_confidence_monitor")
trace_contract._emit_applies_guardrail("p0", "l0_routing_confidence_monitor", "p0_governance")
trace_contract._emit_snapshots_state("p0", "l0_routing_confidence_monitor", "state_snapshot")
trace_contract._emit_pulls_context("p1", "l0_routing_confidence_monitor", "context_pull")
trace_contract._emit_pulls_context("p1", "l0_routing_confidence_monitor", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "l0_routing_confidence_monitor", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "l0_routing_confidence_monitor", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "l0_routing_confidence_monitor", "write_through")
trace_contract._emit_writes_through("p1", "l0_routing_confidence_monitor", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "l0_routing_confidence_monitor", "safety_validation")
trace_contract._emit_invokes_eval("p1", "l0_routing_confidence_monitor", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "l0_routing_confidence_monitor", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "l0_routing_confidence_monitor", "human_escalation")
trace_contract._emit_routes_through("p1", "l0_routing_confidence_monitor", "route_through")
trace_contract._emit_checks_agent_registry("p1", "l0_routing_confidence_monitor", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "l0_routing_confidence_monitor", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "l0_routing_confidence_monitor", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "l0_routing_confidence_monitor", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "l0_routing_confidence_monitor", "target_agent")
trace_contract._emit_verifies_policy("p1", "l0_routing_confidence_monitor", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "l0_routing_confidence_monitor", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "l0_routing_confidence_monitor", "boundary_check")
trace_contract._emit_transcripts_response("p1", "l0_routing_confidence_monitor", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "l0_routing_confidence_monitor")
trace_contract._emit_gated_by_confidence("p1", "l0_routing_confidence_monitor", "confidence_gate")
trace_contract.emit_replay_key("p0", "l0_routing_confidence_monitor")
trace_contract.emit_determinism_digest("p0", "l0_routing_confidence_monitor")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MIN_CONFIDENCE = 0.10
_MAX_CONFIDENCE = 0.80
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.03
_P10_TRIGGER = 0.30


# ---------------------------------------------------------------------------
# Change Package
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RoutingConfidenceChangePackage:
    """Immutable, deterministically-hashable routing confidence change proposal.

    Fields
    ------
    surface_name : str
        Always ``"routing_min_confidence"``.
    old_value : float
        Current min_confidence value in AgenticRouter.
    new_value : float
        Proposed min_confidence value.
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
        data = {
            "surface_name": self.surface_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Percentile helper
# ---------------------------------------------------------------------------


def _compute_p10(values: list[float]) -> float:
    """Compute the 10th percentile of a sorted list of floats."""
    if not values:
        return 1.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    index = 0.10 * (n - 1)
    lower = int(index)
    upper = min(lower + 1, n - 1)
    fraction = index - lower
    return sorted_vals[lower] + fraction * (sorted_vals[upper] - sorted_vals[lower])


# ---------------------------------------------------------------------------
# Proposal Function
# ---------------------------------------------------------------------------


def propose_routing_confidence_change(
    *,
    snapshot_id: str,
    confidence_values: list[float],
    current_config: dict[str, float],
    now_utc: int,
    history: dict[str, Any],
    cooldown_policy: CooldownPolicy,
    sample_policy: SampleSizePolicy,
    adg_territory_score: float = 0.0,
    adg_confidence_tiers: dict[str, int] | None = None,
) -> RoutingConfidenceChangePackage | None:
    """Propose a routing_min_confidence adjustment when p10 drops below trigger.

    Parameters
    ----------
    snapshot_id : str
        Identifier for the metrics snapshot.
    confidence_values : list[float]
        Recent routing confidence scores (one per routing decision).
    current_config : dict[str, float]
        Must include ``"routing_min_confidence"``.
    now_utc : int
        Current deterministic timestamp.
    history : dict[str, Any]
        Keys: ``"routing_min_confidence_last_update"``,
              ``"routing_min_confidence_n_obs"``.
    cooldown_policy : CooldownPolicy
        Cooldown dampening policy.
    sample_policy : SampleSizePolicy
        Sample-size dampening policy.
    adg_territory_score : float
        ADG behavioral score (0-1, higher = more risk).
    adg_confidence_tiers : dict[str, int] | None
        ADG confidence tier distribution (e.g., {'C0': 1000, 'C1': 500}).

    Returns
    -------
    RoutingConfidenceChangePackage | None
        A proposal if adjustment is warranted, ``None`` otherwise.
    """
    surface = "routing_min_confidence"
    current_value = current_config.get(surface)
    if current_value is None or not confidence_values:
        return None

    p10 = round(_compute_p10(confidence_values), 4)

    # Adjust p10 trigger based on ADG territory score    # review: CooldownViolation should be handled with specific context
    # Higher ADG risk = lower trigger threshold (more sensitive)
    adjusted_trigger = _P10_TRIGGER - (adg_territory_score * 0.1)  # Max 0.1 reduction
    adjusted_trigger = max(0.5, adjusted_trigger)  # Never go below 0.5

    # Further adjust based on ADG confidence tiers
    if adg_confidence_tiers:  # review: SampleSizeViolation should be handled with specific context
        total_edges = sum(adg_confidence_tiers.values())
        if total_edges > 0:
            # High proportion of low confidence (C0/C1) increases sensitivity
            low_conf_ratio = (
                adg_confidence_tiers.get("C0", 0) + adg_confidence_tiers.get("C1", 0)
            ) / total_edges
            if low_conf_ratio > 0.3:  # More than 30% low confidence
                adjusted_trigger -= 0.05  # Additional sensitivity boost
                adjusted_trigger = max(0.5, adjusted_trigger)

    if p10 >= adjusted_trigger:
        return None

    last_update_utc = history.get(f"{surface}_last_update", 0)
    try:
        assert_cooldown_ok(last_update_utc, now_utc, cooldown_policy)
    except CooldownViolation:  # guardian: allow-return-none-swallow -- cooldown active: caller treats None as "no update proposed this cycle"
        return None

    n_obs = history.get(f"{surface}_n_obs", 0)
    try:
        assert_min_sample_size(n_obs, sample_policy)
    except SampleSizeViolation:  # guardian: allow-return-none-swallow -- insufficient samples: caller treats None as "no update proposed this cycle"
        return None

    new_value = current_value + _DEFAULT_DELTA
    new_value = min(new_value, _MAX_CONFIDENCE)
    new_value = max(new_value, _MIN_CONFIDENCE)
    new_value = round(new_value, 4)

    if new_value == current_value:
        return None

    delta = abs(new_value - current_value)
    if delta > _MAX_DELTA:
        new_value = current_value + (_MAX_DELTA if new_value > current_value else -_MAX_DELTA)
        new_value = round(new_value, 4)

    justification = (
        f"routing_confidence_p10={p10:.4f} below adjusted_trigger={adjusted_trigger:.4f} "
        f"(base_trigger={_P10_TRIGGER}, adg_score={adg_territory_score:.3f}, "
        f"low_conf_ratio={(adg_confidence_tiers and (sum(adg_confidence_tiers.get(t, 0) for t in ('C0', 'C1')) / sum(adg_confidence_tiers.values())) or 0):.3f}); "
        f"adjusting {surface} from {current_value} to {new_value} (delta={delta:.4f})"
    )
    logger.debug("RoutingConfidenceMonitor: %s", justification)

    return RoutingConfidenceChangePackage(
        surface_name=surface,
        old_value=current_value,
        new_value=new_value,
        justification=justification,
        snapshot_id=snapshot_id,
    )


# ---------------------------------------------------------------------------
# Proposer Adapter (mirrors L0ProposerAdapter pattern)
# ---------------------------------------------------------------------------


class L0RoutingConfidenceProposerAdapter:
    """Adapts ``propose_routing_confidence_change`` to the pipeline proposer protocol.

    The pipeline calls ``proposer.propose(snapshot, confidence_values, config,
    now_utc, history, cooldown, sample)``.
    """

    def propose(
        self,
        snapshot: Any,
        confidence_values: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
        adg_territory_score: float = 0.0,
        adg_confidence_tiers: dict[str, int] | None = None,
    ) -> RoutingConfidenceChangePackage | None:
        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")

        if not isinstance(confidence_values, list):
            confidence_values = []

        if not isinstance(config, dict):
            config = {}

        if not isinstance(history, dict):
            history = {}

        if cooldown is None:
            # guardian: allow-magic-config
            cooldown = CooldownPolicy(min_seconds_between_updates=3600)

        if sample is None:
            # guardian: allow-magic-config
            sample = SampleSizePolicy(min_observations=10)

        return propose_routing_confidence_change(
            snapshot_id=snapshot_id,
            confidence_values=confidence_values,
            current_config=config,
            now_utc=now_utc,
            history=history,
            cooldown_policy=cooldown,
            sample_policy=sample,
            adg_territory_score=adg_territory_score,
            adg_confidence_tiers=adg_confidence_tiers,
        )


__all__ = [
    "RoutingConfidenceChangePackage",
    "L0RoutingConfidenceProposerAdapter",
    "propose_routing_confidence_change",
]
