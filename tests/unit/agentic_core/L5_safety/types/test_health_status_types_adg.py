"""ADG contract tests for L5_safety/types/health_status_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_health_status_types_adg")
_emit_applies_guardrail("p0", "test_health_status_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_health_status_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_health_status_types_adg", "state_snapshot")
emit_replay_key("p0", "test_health_status_types_adg")
emit_determinism_digest("p0", "test_health_status_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.health_status_types import AlertSeverity, HealthStatus, health_metrics


class TestHealthStatus:
    def test_is_enum(self):
        import enum; assert issubclass(HealthStatus, enum.Enum)
    def test_has_healthy(self): assert HealthStatus.HEALTHY.value == "healthy"
    def test_has_critical(self): assert HealthStatus.CRITICAL.value == "critical"

class TestAlertSeverity:
    def test_is_enum(self):
        import enum; assert issubclass(AlertSeverity, enum.Enum)
    def test_has_warning(self): assert AlertSeverity.WARNING.value == "warning"

class TestHealthMetrics:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(health_metrics)
    def test_creates(self):
        m = health_metrics(agent_id="a1", success_rate=0.99, avg_response_time_ms=50.0,
                           error_rate=0.01, circuit_breaker_trips=0, total_requests=100)
        assert m.agent_id == "a1"
    def test_to_dict(self):
        m = health_metrics(agent_id="a1", success_rate=1.0, avg_response_time_ms=10.0,
                           error_rate=0.0, circuit_breaker_trips=0, total_requests=10)
        d = m.to_dict()
        assert d["agent_id"] == "a1"
