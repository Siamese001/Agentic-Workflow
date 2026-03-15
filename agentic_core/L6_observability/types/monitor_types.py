"""
Monitor Types - Data models for agent execution monitoring.

Extracted from schemas/UnifiedAgent_monitor_types.py during Schema Dissolution.
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

_emit_snapshots_state("p0", "monitor_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "monitor_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "monitor_types")


@dataclass
class ExecutionMetrics:
    """Metrics for a single execution."""

    agent_name: str
    category: str
    strategy_type: str
    execution_time_ms: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for monitoring."""

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time_ms: float = 0.0
    avg_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float("inf")
    max_execution_time_ms: float = 0.0
    executions_by_category: dict[str, int] = field(default_factory=dict)
    executions_by_strategy: dict[str, int] = field(default_factory=dict)
    facade_executions: int = 0
    facade_agents: dict[str, int] = field(default_factory=dict)


__all__ = ["ExecutionMetrics", "AggregatedMetrics"]
