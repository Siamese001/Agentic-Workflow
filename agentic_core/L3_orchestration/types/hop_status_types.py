from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "hop_status_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "hop_status_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "hop_status_types")

"Enum types for orchestrate_workflow_types."
import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class HopStatus(Enum):
    """Status of a workflow hop."""


class GateDecision(Enum):
    """Decision from a validation gate."""
