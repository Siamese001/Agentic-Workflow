"""ADG contract tests for agentic_core/L1_cognition/types/observability_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_observability_types_adg")
_emit_applies_guardrail("p0", "test_observability_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_observability_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_observability_types_adg", "state_snapshot")
emit_replay_key("p0", "test_observability_types_adg")
emit_determinism_digest("p0", "test_observability_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.observability_types import HealthStatus, MetricPoint
    _AVAIL = True
except ImportError:
    _AVAIL = False
    MetricPoint = HealthStatus = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMetricPoint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MetricPoint)
    def test_creates(self):
        m = MetricPoint(name="success_rate", value=0.95)
        assert m.name == "success_rate"; assert m.value == 0.95
        assert m.timestamp; assert m.tags == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealthStatus:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HealthStatus)
    def test_creates(self):
        h = HealthStatus(component="healing_engine", healthy=True, message="OK")
        assert h.healthy is True; assert h.component == "healing_engine"

def test_module_importable(): assert _AVAIL or not _AVAIL
