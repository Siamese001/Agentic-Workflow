from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "budget_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "budget_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "budget_types")

"Dataclass models for lic_routing_rules."
import logging
from dataclasses import dataclass, field

_logger = logging.getLogger(__name__)


@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""

    _minimum: int = 0
    _maximum: int = 20
    _guidance: dict[str, str] = field(default_factory=dict)
