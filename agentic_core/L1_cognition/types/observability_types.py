"""
agentic_core/L1_cognition/reasoning/types/observability_types.py

Passive data structures for MetaLearningObservability.
Extracted from engine/meta_observability.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "observability_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "observability_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "observability_types")


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Health status for a component."""

    component: str
    healthy: bool
    message: str
    last_check: str = field(default_factory=lambda: datetime.now().isoformat())
    details: dict[str, Any] = field(default_factory=dict)
