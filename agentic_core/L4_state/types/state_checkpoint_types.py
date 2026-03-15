from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "state_checkpoint_types", "L4")
_emit_routes_through("p1", "state_checkpoint_types", "L4")
_emit_escalates_to_human("p1", "state_checkpoint_types", "L4")
_emit_reads_policy_state("p1", "state_checkpoint_types", "L4")

_emit_snapshots_state("p0", "state_checkpoint_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "state_checkpoint_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "state_checkpoint_types")

"Types and models for track_lic_state."
import logging
from dataclasses import dataclass, field

_logger = logging.getLogger(__name__)


@dataclass
class StateCheckpoint:
    """Checkpoint for a HOP state."""

    _hop_id: str
    _mission_id: str
    _timestamp: str
    _checksum: str
    _filepath: str


@dataclass
class StateValidationResult:
    """Result of state validation."""

    _is_valid: bool
    _errors: list[str] = field(default_factory=list)
    _warnings: list[str] = field(default_factory=list)
