from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

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
