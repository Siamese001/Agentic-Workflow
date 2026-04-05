"""
§Wave4.1 — VigilanceEventArtifact: L6 → L0 routing signal.

Deterministic event artifact emitted by TieredVigilanceMonitor (L6)
and consumed by L0 routing intake. Carries semantic_clock from Phase 3.2,
a deterministic vigilance tier, and sorted normalized signal codes.

Forbidden: elapsed_ms, wall-clock timestamps, uuid4.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    record_execution_trace,
)

record_execution_trace("vigilance_event_types", "vigilance_event_types_trace")


_emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_1")
_emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_2")
_emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_3")
_emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_4")
_emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_5")
_emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_6")
_emit_records_incident_event("vigilance_event_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("vigilance_event_types", "p4obs", "anomaly")
_emit_writes_observability_log("vigilance_event_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("vigilance_event_types", "p4obs", "mon_state")
_emit_triggers_alert("vigilance_event_types", "p4obs", "alert")
_emit_links_incident_trace("vigilance_event_types", "p4obs", "trace_link")
_emit_captures_pattern("vigilance_event_types", "p3lm", "pattern")
_emit_records_learning_event("vigilance_event_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vigilance_event_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("vigilance_event_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vigilance_event_types", "p3lm", "routing")
_emit_improves_agent_policy("vigilance_event_types", "p3lm", "policy")
_emit_stores_learning_state("vigilance_event_types", "p3lm", "state")
_emit_records_execution_trace("vigilance_event_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vigilance_event_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vigilance_event_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vigilance_event_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vigilance_event_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vigilance_event_types", "env_read", "p2_env_1")
_emit_reads_environ("vigilance_event_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("vigilance_event_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vigilance_event_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "vigilance_event_types")
emit_determinism_digest("p0", "vigilance_event_types")

_emit_dispatches_healing_run("p1", "vigilance_event_types", "L6")
_emit_routes_through("p1", "vigilance_event_types", "L6")
_emit_checks_agent_registry("p1", "vigilance_event_types", "agent_registry")
_emit_validates_agent_capability("p1", "vigilance_event_types", "capability")
_emit_dispatches_execution_plan("p1", "vigilance_event_types", "exec_plan")
_emit_agent_executes_agent("p1", "vigilance_event_types", "sub_agent")
_emit_routes_to_agent("p1", "vigilance_event_types", "target_agent")
_emit_verifies_policy("p1", "vigilance_event_types", "policy_check")
_emit_observes_runtime_state("p1", "vigilance_event_types", "runtime_state")
_emit_verifies_boundary("p1", "vigilance_event_types", "boundary_check")
_emit_transcripts_response("p1", "vigilance_event_types", "transcript")
_emit_hard_fails_untranscripted("p1", "vigilance_event_types")
_emit_gated_by_confidence("p1", "vigilance_event_types", "confidence_gate")
_emit_escalates_to_human("p1", "vigilance_event_types", "L6")
_emit_reads_policy_state("p1", "vigilance_event_types", "L6")
_emit_pulls_context("p1", "vigilance_event_types", "context_pull")
_emit_pulls_context("p1", "vigilance_event_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "vigilance_event_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vigilance_event_types", "uwg_term_secondary")
_emit_writes_through("p1", "vigilance_event_types", "write_through")
_emit_writes_through("p1", "vigilance_event_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "vigilance_event_types", "safety_validation")
_emit_invokes_eval("p1", "vigilance_event_types", "eval_call")
_emit_proposal_commits_routing("p1", "vigilance_event_types", "routing_commit")

_emit_snapshots_state("p0", "vigilance_event_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "vigilance_event_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "vigilance_event_types")
_emit_authorize_and_execute("p2", "vigilance_event_types", "execution_auth")
_emit_validates_capability("p2", "vigilance_event_types", "capability_check")
_emit_routes_to_capability("p2", "vigilance_event_types", "capability_route")
_emit_writes_via_uwg("p2", "vigilance_event_types", "uwg_write")
_emit_blocks_direct_write("p2", "vigilance_event_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vigilance_event_types", "tool_invocation")
_emit_captures_execution_output("p2", "vigilance_event_types", "exec_output")
_emit_dispatches_agent("p3", "vigilance_event_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vigilance_event_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vigilance_event_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vigilance_event_types", "healing_outcome")
_emit_escalates_failure("p3", "vigilance_event_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vigilance_event_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vigilance_event_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vigilance_event_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vigilance_event_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vigilance_event_types", "eval_metric")
_emit_stores_embedding("p4", "vigilance_event_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vigilance_event_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vigilance_event_types", "exec_snapshot_link")


class VigilanceSeverity(str, Enum):
    """§Wave4.1 — Routing-oriented vigilance severity.

    Maps to L0 routing decisions:
      LOW/MEDIUM  → L5 rules-first (STANDARD_VALIDATION)
      HIGH/CRITICAL → HIL (HUMAN_ESCALATION)
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Fixed precedence: CRITICAL > HIGH > MEDIUM > LOW
_SEVERITY_PRECEDENCE: dict[VigilanceSeverity, int] = {
    VigilanceSeverity.LOW: 0,
    VigilanceSeverity.MEDIUM: 1,
    VigilanceSeverity.HIGH: 2,
    VigilanceSeverity.CRITICAL: 3,
}


@dataclass(frozen=True)
class VigilanceEventArtifact:
    """§Wave4.1 — Normalized L6 detection event for L0 routing.

    Required fields:
      event_type       — fixed string identifying the event class
      semantic_clock   — required; reuse Phase 3.2 contract
      vigilance_tier   — VigilanceSeverity enum
      signals          — sorted tuple of normalized signal codes
      trace_id         — deterministic (no uuid4)
      policy_config_hash — policy hash if available (empty string default)
    """

    event_type: str
    semantic_clock: SemanticClockSnapshot
    vigilance_tier: VigilanceSeverity
    signals: tuple[str, ...]
    trace_id: str
    policy_config_hash: str = ""

    def __post_init__(self) -> None:
        if not self.event_type:
            raise ValueError("VigilanceEventArtifact: event_type must be non-empty")
        validate_semantic_clock(self.semantic_clock)
        if not isinstance(self.vigilance_tier, VigilanceSeverity):
            raise TypeError(
                f"VigilanceEventArtifact: vigilance_tier must be VigilanceSeverity, "
                f"got {type(self.vigilance_tier).__name__}",
            )
        if not isinstance(self.signals, tuple):
            raise TypeError("VigilanceEventArtifact: signals must be a tuple")
        if list(self.signals) != sorted(self.signals):
            raise ValueError(
                "VigilanceEventArtifact: signals must be sorted",
            )
        if not self.trace_id:
            raise ValueError("VigilanceEventArtifact: trace_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic serialization with sorted keys."""
        return {
            "event_type": self.event_type,
            "policy_config_hash": self.policy_config_hash,
            "semantic_clock": self.semantic_clock.to_dict(),
            "signals": list(self.signals),
            "trace_id": self.trace_id,
            "vigilance_tier": self.vigilance_tier.value,
        }


def build_deterministic_trace_id(signals: tuple[str, ...], tick: int) -> str:
    """§Wave4.1 — Deterministic trace_id from signal content + clock tick.

    No uuid4. SHA-256 prefix of canonical input.
    """
    canonical = f"{tick}:{','.join(signals)}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


__all__ = [
    "VigilanceEventArtifact",
    "VigilanceSeverity",
    "build_deterministic_trace_id",
]
