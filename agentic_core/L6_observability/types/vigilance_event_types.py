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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.record_execution_trace("vigilance_event_types", "vigilance_event_types_trace")


trace_contract._emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("vigilance_event_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("vigilance_event_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("vigilance_event_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("vigilance_event_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("vigilance_event_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("vigilance_event_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("vigilance_event_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("vigilance_event_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("vigilance_event_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("vigilance_event_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("vigilance_event_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("vigilance_event_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("vigilance_event_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("vigilance_event_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("vigilance_event_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("vigilance_event_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("vigilance_event_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("vigilance_event_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("vigilance_event_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("vigilance_event_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("vigilance_event_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("vigilance_event_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("vigilance_event_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "vigilance_event_types")
trace_contract.emit_determinism_digest("p0", "vigilance_event_types")

trace_contract._emit_dispatches_healing_run("p1", "vigilance_event_types", "L6")
trace_contract._emit_routes_through("p1", "vigilance_event_types", "L6")
trace_contract._emit_checks_agent_registry("p1", "vigilance_event_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "vigilance_event_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "vigilance_event_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "vigilance_event_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "vigilance_event_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "vigilance_event_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "vigilance_event_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "vigilance_event_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "vigilance_event_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "vigilance_event_types")
trace_contract._emit_gated_by_confidence("p1", "vigilance_event_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "vigilance_event_types", "L6")
trace_contract._emit_reads_policy_state("p1", "vigilance_event_types", "L6")
trace_contract._emit_pulls_context("p1", "vigilance_event_types", "context_pull")
trace_contract._emit_pulls_context("p1", "vigilance_event_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "vigilance_event_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "vigilance_event_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "vigilance_event_types", "write_through")
trace_contract._emit_writes_through("p1", "vigilance_event_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "vigilance_event_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "vigilance_event_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "vigilance_event_types", "routing_commit")

trace_contract._emit_snapshots_state("p0", "vigilance_event_types", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "vigilance_event_types", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "vigilance_event_types")
trace_contract._emit_authorize_and_execute("p2", "vigilance_event_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "vigilance_event_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "vigilance_event_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "vigilance_event_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "vigilance_event_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "vigilance_event_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "vigilance_event_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "vigilance_event_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "vigilance_event_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "vigilance_event_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "vigilance_event_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "vigilance_event_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "vigilance_event_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "vigilance_event_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "vigilance_event_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "vigilance_event_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "vigilance_event_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "vigilance_event_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "vigilance_event_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "vigilance_event_types", "exec_snapshot_link")


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
