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
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "vigilance_event_types")
emit_determinism_digest("p0", "vigilance_event_types")

_emit_dispatches_healing_run("p1", "vigilance_event_types", "L6")
_emit_routes_through("p1", "vigilance_event_types", "L6")
_emit_escalates_to_human("p1", "vigilance_event_types", "L6")
_emit_reads_policy_state("p1", "vigilance_event_types", "L6")

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
