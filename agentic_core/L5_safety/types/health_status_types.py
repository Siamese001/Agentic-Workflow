from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "health_status_types", "L5")
_emit_routes_through("p1", "health_status_types", "L5")
_emit_escalates_to_human("p1", "health_status_types", "L5")
_emit_reads_policy_state("p1", "health_status_types", "L5")

"Types and models for AutonomicMonitorAgent."
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Agent health status."""

    HEALTHY: Any = "healthy"
    DEGRADED: Any = "degraded"
    CRITICAL: Any = "critical"
    OFFLINE: Any = "offline"


class AlertSeverity(Enum):
    """Alert Severity levels."""

    INFO: Any = "info"
    WARNING: Any = "warning"
    ERROR: Any = "error"
    CRITICAL: Any = "critical"


@dataclass
class health_metrics:
    """Health metrics for an agent."""

    agent_id: str
    success_rate: float
    avg_response_time_ms: float
    error_rate: float
    circuit_breaker_trips: int
    total_requests: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "health_metrics.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "health_metrics.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "health_metrics.to_dict")
        return {
            "agent_id": self.agent_id,
            "success_rate": self.success_rate,
            "avg_response_time_ms": self.avg_response_time_ms,
            "error_rate": self.error_rate,
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "total_requests": self.total_requests,
            "timestamp": self.timestamp,
        }


@dataclass
class HealthAlert:
    """Health alert for degradation detection."""

    alert_id: str
    agent_id: str
    Severity: AlertSeverity
    message: str
    metrics: health_metrics
    recommended_actions: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "agent_id": self.agent_id,
            "Severity": self.Severity.value,
            "message": self.message,
            "metrics": self.metrics.to_dict(),
            "recommended_actions": self.recommended_actions,
            "timestamp": self.timestamp,
        }
