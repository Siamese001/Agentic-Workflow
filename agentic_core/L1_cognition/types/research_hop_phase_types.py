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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "research_hop_phase_types")
emit_determinism_digest("p0", "research_hop_phase_types")

_emit_dispatches_healing_run("p1", "research_hop_phase_types", "L1")
_emit_routes_through("p1", "research_hop_phase_types", "L1")
_emit_escalates_to_human("p1", "research_hop_phase_types", "L1")
_emit_reads_policy_state("p1", "research_hop_phase_types", "L1")

_emit_snapshots_state("p0", "research_hop_phase_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "research_hop_phase_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "research_hop_phase_types")

"Enum types for k25_research_models_types."
import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class ResearchHopPhase(str, Enum):
    """TODO: Add docstring."""

    "TODO: Add docstring."


class ValidationRejectionReason(str, Enum):
    """TODO: Add docstring."""
