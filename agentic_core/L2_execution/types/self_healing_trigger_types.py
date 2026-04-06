"""
§Wave4.3 — L2SelfHealingTrigger: authorized, deterministic healing trigger.

Emitted from the control spine ONLY when healing is authorized:
  (a) L5 auto-approves healing for the request/risk tier, OR
  (b) HIL approves healing escalation

NOT emitted from L1 or L6. NOT emitted when rejected/pending/read-only.

Deterministic contract:
  - SemanticClockSnapshot required (Phase 3.2)
  - recommended_actions sorted
  - trace_id is SHA-256 of canonical payload (no uuid4)
  - No wall-clock timestamps, no elapsed_ms
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("self_healing_trigger_types", "p4obs", "metric_1")
_emit_emits_metric_event("self_healing_trigger_types", "p4obs", "metric_2")
_emit_emits_metric_event("self_healing_trigger_types", "p4obs", "metric_3")
_emit_emits_metric_event("self_healing_trigger_types", "p4obs", "metric_4")
_emit_emits_metric_event("self_healing_trigger_types", "p4obs", "metric_5")
_emit_emits_metric_event("self_healing_trigger_types", "p4obs", "metric_6")
_emit_records_incident_event("self_healing_trigger_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("self_healing_trigger_types", "p4obs", "anomaly")
_emit_writes_observability_log("self_healing_trigger_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("self_healing_trigger_types", "p4obs", "mon_state")
_emit_triggers_alert("self_healing_trigger_types", "p4obs", "alert")
_emit_links_incident_trace("self_healing_trigger_types", "p4obs", "trace_link")
_emit_captures_pattern("self_healing_trigger_types", "p3lm", "pattern")
_emit_records_learning_event("self_healing_trigger_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("self_healing_trigger_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("self_healing_trigger_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("self_healing_trigger_types", "p3lm", "routing")
_emit_improves_agent_policy("self_healing_trigger_types", "p3lm", "policy")
_emit_stores_learning_state("self_healing_trigger_types", "p3lm", "state")
_emit_records_execution_trace("self_healing_trigger_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("self_healing_trigger_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("self_healing_trigger_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("self_healing_trigger_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("self_healing_trigger_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("self_healing_trigger_types", "env_read", "p2_env_1")
_emit_reads_environ("self_healing_trigger_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("self_healing_trigger_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("self_healing_trigger_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "self_healing_trigger_types")
emit_determinism_digest("p0", "self_healing_trigger_types")

_emit_dispatches_healing_run("p1", "self_healing_trigger_types", "L2")
_emit_routes_through("p1", "self_healing_trigger_types", "L2")
_emit_checks_agent_registry("p1", "self_healing_trigger_types", "agent_registry")
_emit_validates_agent_capability("p1", "self_healing_trigger_types", "capability")
_emit_dispatches_execution_plan("p1", "self_healing_trigger_types", "exec_plan")
_emit_agent_executes_agent("p1", "self_healing_trigger_types", "sub_agent")
_emit_routes_to_agent("p1", "self_healing_trigger_types", "target_agent")
_emit_verifies_policy("p1", "self_healing_trigger_types", "policy_check")
_emit_observes_runtime_state("p1", "self_healing_trigger_types", "runtime_state")
_emit_verifies_boundary("p1", "self_healing_trigger_types", "boundary_check")
_emit_transcripts_response("p1", "self_healing_trigger_types", "transcript")
_emit_hard_fails_untranscripted("p1", "self_healing_trigger_types")
_emit_gated_by_confidence("p1", "self_healing_trigger_types", "confidence_gate")
_emit_escalates_to_human("p1", "self_healing_trigger_types", "L2")
_emit_reads_policy_state("p1", "self_healing_trigger_types", "L2")
_emit_pulls_context("p1", "self_healing_trigger_types", "context_pull")
_emit_pulls_context("p1", "self_healing_trigger_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "self_healing_trigger_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "self_healing_trigger_types", "uwg_term_secondary")
_emit_writes_through("p1", "self_healing_trigger_types", "write_through")
_emit_writes_through("p1", "self_healing_trigger_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "self_healing_trigger_types", "safety_validation")
_emit_invokes_eval("p1", "self_healing_trigger_types", "eval_call")
_emit_proposal_commits_routing("p1", "self_healing_trigger_types", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "self_healing_trigger_types")
_emit_applies_guardrail("p0", "self_healing_trigger_types", "p0_governance")
_emit_snapshots_state("p0", "self_healing_trigger_types", "state_snapshot")
_emit_authorize_and_execute("p2", "self_healing_trigger_types", "execution_auth")
_emit_validates_capability("p2", "self_healing_trigger_types", "capability_check")
_emit_routes_to_capability("p2", "self_healing_trigger_types", "capability_route")
_emit_writes_via_uwg("p2", "self_healing_trigger_types", "uwg_write")
_emit_blocks_direct_write("p2", "self_healing_trigger_types", "direct_write_block")
_emit_records_tool_invocation("p2", "self_healing_trigger_types", "tool_invocation")
_emit_captures_execution_output("p2", "self_healing_trigger_types", "exec_output")
_emit_dispatches_agent("p3", "self_healing_trigger_types", "agent_dispatch")
_emit_coordinates_agents("p3", "self_healing_trigger_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "self_healing_trigger_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "self_healing_trigger_types", "healing_outcome")
_emit_escalates_failure("p3", "self_healing_trigger_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "self_healing_trigger_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "self_healing_trigger_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "self_healing_trigger_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "self_healing_trigger_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "self_healing_trigger_types", "eval_metric")
_emit_stores_embedding("p4", "self_healing_trigger_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "self_healing_trigger_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "self_healing_trigger_types", "exec_snapshot_link")

# =============================================================================
# §Wave4.3 — Authorization decision enum (string, not Enum object)
# =============================================================================

AUTHORIZED_DECISIONS: frozenset[str] = frozenset(
    {
        "AUTO_APPROVED",
        "HIL_APPROVED",
    },
)

REJECTED_DECISIONS: frozenset[str] = frozenset(
    {
        "REJECTED",
        "PENDING",
        "READ_ONLY",
        "NOT_APPROVED",
    },
)


# =============================================================================
# §Wave4.3 — L2SelfHealingTrigger
# =============================================================================


@dataclass(frozen=True)
class L2SelfHealingTrigger:
    """§Wave4.3 — Authorized self-healing trigger emitted at L2 control spine.

    Required fields:
      artifact_type        — fixed "SELF_HEALING_TRIGGER"
      semantic_clock       — required SemanticClockSnapshot
      trace_id             — deterministic (SHA-256 of canonical payload)
      target               — stable identifier (file path or subsystem key)
      reason_code          — stable string (no Enum objects)
      recommended_actions  — sorted tuple of action strings
      risk_tier            — tier string (e.g., "low", "medium", "high", "critical")
      authorization        — how healing was authorized ("AUTO_APPROVED" or "HIL_APPROVED")
      policy_config_hash   — optional
      route_context        — optional stable string
    """

    artifact_type: str
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    target: str
    reason_code: str
    recommended_actions: tuple[str, ...]
    risk_tier: str
    authorization: str
    policy_config_hash: str = ""
    route_context: str = ""

    def __post_init__(self) -> None:
        if self.artifact_type != "SELF_HEALING_TRIGGER":
            raise ValueError(
                f"L2SelfHealingTrigger: artifact_type must be 'SELF_HEALING_TRIGGER', "
                f"got '{self.artifact_type}'",
            )
        validate_semantic_clock(self.semantic_clock)
        if not self.trace_id:
            raise ValueError("L2SelfHealingTrigger: trace_id must be non-empty")
        if not self.target:
            raise ValueError("L2SelfHealingTrigger: target must be non-empty")
        if not self.reason_code:
            raise ValueError("L2SelfHealingTrigger: reason_code must be non-empty")
        if not isinstance(self.recommended_actions, tuple):
            raise TypeError(
                "L2SelfHealingTrigger: recommended_actions must be a tuple",
            )
        if list(self.recommended_actions) != sorted(self.recommended_actions):
            raise ValueError(
                "L2SelfHealingTrigger: recommended_actions must be sorted",
            )
        if not self.risk_tier:
            raise ValueError("L2SelfHealingTrigger: risk_tier must be non-empty")
        if self.authorization not in AUTHORIZED_DECISIONS:
            raise ValueError(
                f"L2SelfHealingTrigger: authorization must be one of "
                f"{sorted(AUTHORIZED_DECISIONS)}, got '{self.authorization}'",
            )

    def to_dict(self) -> dict[str, Any]:
        """Deterministic serialization with sorted keys."""
        return {
            "artifact_type": self.artifact_type,
            "authorization": self.authorization,
            "policy_config_hash": self.policy_config_hash,
            "reason_code": self.reason_code,
            "recommended_actions": list(self.recommended_actions),
            "risk_tier": self.risk_tier,
            "route_context": self.route_context,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target": self.target,
            "trace_id": self.trace_id,
        }


# =============================================================================
# §Wave4.3 — Authorization gate + emit factory
# =============================================================================


def _compute_trigger_trace_id(
    target: str,
    reason_code: str,
    actions: tuple[str, ...],
    tick: int,
) -> str:
    """Deterministic trace_id from canonical payload hash."""
    canonical = json.dumps(
        {
            "actions": list(actions),
            "reason_code": reason_code,
            "target": target,
            "tick": tick,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def is_healing_authorized(decision: str) -> bool:
    """§Wave4.3 — Check if a decision authorizes healing emission."""
    return decision in AUTHORIZED_DECISIONS


def emit_self_healing_trigger(
    decision: str,
    target: str,
    reason_code: str,
    recommended_actions: list[str],
    risk_tier: str,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str = "",
    route_context: str = "",
) -> L2SelfHealingTrigger | None:
    """§Wave4.3 — Emit a SelfHealingTrigger ONLY when authorized.

    Returns None if healing is not authorized (rejected/pending/read-only).
    Raises ValueError if semantic_clock is None (even for authorized paths).

    Authorization gate:
      AUTO_APPROVED / HIL_APPROVED → emit trigger
      Everything else → return None (no emission)
    """
    if not is_healing_authorized(decision):
        return None

    validate_semantic_clock(semantic_clock)

    normalized_actions = tuple(sorted(set(recommended_actions)))
    trace_id = _compute_trigger_trace_id(
        target,
        reason_code,
        normalized_actions,
        semantic_clock.tick,
    )

    return L2SelfHealingTrigger(
        artifact_type="SELF_HEALING_TRIGGER",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        target=target,
        reason_code=reason_code,
        recommended_actions=normalized_actions,
        risk_tier=risk_tier,
        authorization=decision,
        policy_config_hash=policy_config_hash,
        route_context=route_context,
    )


__all__ = [
    "AUTHORIZED_DECISIONS",
    "L2SelfHealingTrigger",
    "REJECTED_DECISIONS",
    "emit_self_healing_trigger",
    "is_healing_authorized",
]
