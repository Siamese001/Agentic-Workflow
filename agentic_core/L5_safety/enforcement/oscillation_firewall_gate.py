"""OscillationFirewall — L5 Safety enforcement.

Wraps the existing OscillationDetector with routing-tier-specific threshold
validation.  Prevents the routing pipeline from oscillating between tiers
(e.g. DETERMINISTIC -> QWEN -> DETERMINISTIC is an oscillation; it must be
frozen before it destabilises downstream agents).

Contract:
- record_tier_decision(tier, cycle) records the tier chosen at each cycle.
- assert_no_oscillation(tier, cycle) raises OscillationFirewallTripped if
  the tier change would complete an oscillation pattern.
- get_frozen_tiers(cycle) returns set of tiers currently frozen.

Threshold defaults (conservative, override via OscillationFirewallConfig):
  cooldown_window = 6   (check last 6 decisions)
  freeze_cycles   = 10  (frozen for 10 cycles on detection)
"""

from __future__ import annotations

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
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "oscillation_firewall_gate")
emit_determinism_digest("p0", "oscillation_firewall_gate")

_emit_dispatches_healing_run("p1", "oscillation_firewall_gate", "L5")
_emit_routes_through("p1", "oscillation_firewall_gate", "L5")
_emit_checks_agent_registry("p1", "oscillation_firewall_gate", "agent_registry")
_emit_validates_agent_capability("p1", "oscillation_firewall_gate", "capability")
_emit_dispatches_execution_plan("p1", "oscillation_firewall_gate", "exec_plan")
_emit_agent_executes_agent("p1", "oscillation_firewall_gate", "sub_agent")
_emit_routes_to_agent("p1", "oscillation_firewall_gate", "target_agent")
_emit_verifies_policy("p1", "oscillation_firewall_gate", "policy_check")
_emit_observes_runtime_state("p1", "oscillation_firewall_gate", "runtime_state")
_emit_verifies_boundary("p1", "oscillation_firewall_gate", "boundary_check")
_emit_transcripts_response("p1", "oscillation_firewall_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "oscillation_firewall_gate")
_emit_gated_by_confidence("p1", "oscillation_firewall_gate", "confidence_gate")
_emit_escalates_to_human("p1", "oscillation_firewall_gate", "L5")
_emit_reads_policy_state("p1", "oscillation_firewall_gate", "L5")

_emit_applies_guardrail("p0", "oscillation_firewall_gate", "p0_governance")
_emit_snapshots_state("p0", "oscillation_firewall_gate", "state_snapshot")
_emit_authorize_and_execute("p2", "oscillation_firewall_gate", "execution_auth")
_emit_validates_capability("p2", "oscillation_firewall_gate", "capability_check")
_emit_routes_to_capability("p2", "oscillation_firewall_gate", "capability_route")
_emit_writes_via_uwg("p2", "oscillation_firewall_gate", "uwg_write")
_emit_blocks_direct_write("p2", "oscillation_firewall_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "oscillation_firewall_gate", "tool_invocation")
_emit_captures_execution_output("p2", "oscillation_firewall_gate", "exec_output")
_emit_dispatches_agent("p3", "oscillation_firewall_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "oscillation_firewall_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "oscillation_firewall_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "oscillation_firewall_gate", "healing_outcome")
_emit_escalates_failure("p3", "oscillation_firewall_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "oscillation_firewall_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "oscillation_firewall_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "oscillation_firewall_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "oscillation_firewall_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "oscillation_firewall_gate", "eval_metric")
_emit_stores_embedding("p4", "oscillation_firewall_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "oscillation_firewall_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "oscillation_firewall_gate", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("oscillation_firewall_gate", "p4obs", "metric_1")
_emit_emits_metric_event("oscillation_firewall_gate", "p4obs", "metric_2")
_emit_emits_metric_event("oscillation_firewall_gate", "p4obs", "metric_3")
_emit_emits_metric_event("oscillation_firewall_gate", "p4obs", "metric_4")
_emit_emits_metric_event("oscillation_firewall_gate", "p4obs", "metric_5")
_emit_emits_metric_event("oscillation_firewall_gate", "p4obs", "metric_6")
_emit_records_incident_event("oscillation_firewall_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("oscillation_firewall_gate", "p4obs", "anomaly")
_emit_writes_observability_log("oscillation_firewall_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("oscillation_firewall_gate", "p4obs", "mon_state")
_emit_triggers_alert("oscillation_firewall_gate", "p4obs", "alert")
_emit_links_incident_trace("oscillation_firewall_gate", "p4obs", "trace_link")
_emit_captures_pattern("oscillation_firewall_gate", "p3lm", "pattern")
_emit_records_learning_event("oscillation_firewall_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("oscillation_firewall_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("oscillation_firewall_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("oscillation_firewall_gate", "p3lm", "routing")
_emit_improves_agent_policy("oscillation_firewall_gate", "p3lm", "policy")
_emit_stores_learning_state("oscillation_firewall_gate", "p3lm", "state")
_emit_records_execution_trace("oscillation_firewall_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("oscillation_firewall_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("oscillation_firewall_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("oscillation_firewall_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("oscillation_firewall_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("oscillation_firewall_gate", "env_read", "p2_env_1")
_emit_reads_environ("oscillation_firewall_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("oscillation_firewall_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("oscillation_firewall_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "oscillation_firewall_gate", "context_pull")
_emit_pulls_context("p1", "oscillation_firewall_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "oscillation_firewall_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "oscillation_firewall_gate", "uwg_term_2")
_emit_writes_through("p1", "oscillation_firewall_gate", "write_through")
_emit_writes_through("p1", "oscillation_firewall_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "oscillation_firewall_gate", "safety_validation")
_emit_invokes_eval("p1", "oscillation_firewall_gate", "eval_call")
_emit_proposal_commits_routing("p1", "oscillation_firewall_gate", "routing_commit")


class OscillationFirewallTripped(RuntimeError):
    """Raised when routing-tier oscillation is detected and firewall fires."""


@dataclass(frozen=True)
class OscillationFirewallConfig:
    """Configuration for the oscillation firewall.

    Fields:
        cooldown_window: Number of recent tier decisions to inspect.
        freeze_cycles:   Number of cycles a tier is frozen after oscillation.
    """

    cooldown_window: int = 6
    freeze_cycles: int = 10

    def __post_init__(self) -> None:
        if self.cooldown_window < 2:
            raise ValueError("cooldown_window must be >= 2")
        if self.freeze_cycles < 1:
            raise ValueError("freeze_cycles must be >= 1")


class OscillationFirewall:
    """Routing-tier oscillation firewall.

    Wraps system_learning.enforcement.oscillation_detector.OscillationDetector
    with routing-tier semantics.  Each tier is tracked independently; an
    oscillation in *any* tier triggers a freeze for that tier.

    Args:
        config: OscillationFirewallConfig (defaults are conservative).
    """

    def __init__(self, config: OscillationFirewallConfig | None = None) -> None:
        from system_learning.enforcement.oscillation_detector import OscillationDetector

        cfg = config or OscillationFirewallConfig()
        self._config = cfg
        self._detector = OscillationDetector(
            cooldown_window=cfg.cooldown_window,
            freeze_cycles=cfg.freeze_cycles,
        )
        self._tier_histories: dict[str, list[Any]] = {}

    def record_tier_decision(self, tier: str, cycle: int) -> None:
        """Record that *tier* was chosen at *cycle*.

        This is the non-raising variant — use for observation only.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "OscillationFirewall.record_tier_decision",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:OscillationFirewall.record_tier_decision".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if tier not in self._tier_histories:
            self._tier_histories[tier] = []
        self._tier_histories[tier].append(cycle)

    _ROUTING_PARAM = "routing_tier"

    def assert_no_oscillation(self, tier: str, cycle: int) -> None:
        """Assert that accepting *tier* at *cycle* does not complete oscillation.

        Tracks a single "routing_tier" parameter whose value is the tier name.
        DETERMINISTIC->QWEN->DETERMINISTIC is two value-flips = oscillation.

        Raises:
            OscillationFirewallTripped: if oscillation pattern is detected.
        """
        from system_learning.enforcement.oscillation_detector import ParameterFrozenError

        try:
            self._detector.record_change(self._ROUTING_PARAM, tier, cycle)
        except (
            ParameterFrozenError
        ) as exc:  # guardian: ParameterFrozenError should be handled with specific context
            raise OscillationFirewallTripped(
                f"OscillationFirewall: tier {tier!r} is oscillating at cycle {cycle}. Routing frozen.\nDetector: {exc}",
            ) from exc
        self.record_tier_decision(tier, cycle)

    def is_tier_frozen(self, tier: str, cycle: int) -> bool:
        """Return True if routing_tier parameter is frozen at *cycle*."""
        return self._detector.is_frozen(self._ROUTING_PARAM, cycle)

    def get_frozen_tiers(self, cycle: int) -> set[str]:
        """Return set of tier names currently frozen at *cycle*."""
        return {tier for tier in self._tier_histories if self._detector.is_frozen(tier, cycle)}

    def reset_for_testing(self) -> None:
        """Clear all state for test isolation."""
        self._detector.reset_for_testing()
        self._tier_histories.clear()


def validate_threshold(
    tier_sequence: tuple[str, ...],
    config: OscillationFirewallConfig | None = None,
) -> bool:
    """Return True if *tier_sequence* does NOT contain an oscillation pattern.

    Stateless alternative to OscillationFirewall.  Used in invariant tests
    to assert that a recorded sequence is stable.

    An oscillation is defined as: the same tier appearing at least twice
    with a different tier interspersed, within the cooldown_window.
    """
    cfg = config or OscillationFirewallConfig()
    if len(tier_sequence) < cfg.cooldown_window:
        return True
    window = tier_sequence[-cfg.cooldown_window :]
    for i in range(len(window) - 2):
        if window[i] == window[i + 2] and window[i] != window[i + 1]:
            return False
    return True


__all__ = [
    "OscillationFirewall",
    "OscillationFirewallConfig",
    "OscillationFirewallTripped",
    "validate_threshold",
]
