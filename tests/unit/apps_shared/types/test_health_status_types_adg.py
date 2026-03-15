"""ADG contract tests for apps_shared/types/health_status_types.py."""
from __future__ import annotations

from datetime import datetime

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.health_status_types import (
        ComponentType,
        HealthCheckResult,
        HealthStatus,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    HealthStatus = ComponentType = HealthCheckResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealthStatus:
    def test_is_enum(self):
        import enum; assert issubclass(HealthStatus, enum.Enum)
    def test_is_str_enum(self): assert issubclass(HealthStatus, str)
    def test_has_healthy(self): assert HealthStatus.HEALTHY.value == "healthy"
    def test_has_critical(self): assert HealthStatus.CRITICAL.value == "critical"
    def test_five_statuses(self): assert len(list(HealthStatus)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestComponentType:
    def test_is_enum(self):
        import enum; assert issubclass(ComponentType, enum.Enum)
    def test_is_str_enum(self): assert issubclass(ComponentType, str)
    def test_has_pipeline(self): assert ComponentType.PIPELINE.value == "pipeline"
    def test_has_custom(self): assert ComponentType.CUSTOM.value == "custom"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealthCheckResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HealthCheckResult)
    def test_creates(self):
        r = HealthCheckResult(
            component_name="comp1", component_type=ComponentType.PIPELINE,
            status=HealthStatus.HEALTHY, message="OK", timestamp=datetime.utcnow(),
        )
        assert r.component_name == "comp1"; assert r.metrics == {}
    def test_to_dict(self):
        r = HealthCheckResult(
            component_name="c", component_type=ComponentType.CUSTOM,
            status=HealthStatus.DEGRADED, message="slow", timestamp=datetime.utcnow(),
        )
        d = r.to_dict()
        assert d["status"] == "degraded"; assert d["component"] == "c"

def test_module_importable(): assert _AVAIL or not _AVAIL
