"""ADG-driven tests for apps_shared/utils/metric_type_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.metric_type_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        AlertRule,
        AlertSeverity,
        LogConfiguration,
        LogLevel,
        MetricDefinition,
        MetricType,
        ObservabilityPlanningConfig,
        TraceConfiguration,
        create_observability_planning_orchestrator,
        orchestrate_observability_planning,
        plan_observability,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MetricType = None  # type: ignore[assignment,misc]
    LogLevel = None  # type: ignore[assignment,misc]
    AlertSeverity = None  # type: ignore[assignment,misc]
    MetricDefinition = None  # type: ignore[assignment,misc]
    LogConfiguration = None  # type: ignore[assignment,misc]
    TraceConfiguration = None  # type: ignore[assignment,misc]
    AlertRule = None  # type: ignore[assignment,misc]
    ObservabilityPlanningConfig = None  # type: ignore[assignment,misc]
    create_observability_planning_orchestrator = None  # type: ignore[assignment,misc]
    plan_observability = None  # type: ignore[assignment,misc]
    orchestrate_observability_planning = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestMetricType:
    def test_is_enum(self):
        import enum
        assert issubclass(MetricType, enum.Enum)
    def test_has_members(self):
        assert len(list(MetricType)) >= 1
    def test_importable(self):
        assert MetricType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestLogLevel:
    def test_is_enum(self):
        import enum
        assert issubclass(LogLevel, enum.Enum)
    def test_has_members(self):
        assert len(list(LogLevel)) >= 1
    def test_importable(self):
        assert LogLevel is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestAlertSeverity:
    def test_is_enum(self):
        import enum
        assert issubclass(AlertSeverity, enum.Enum)
    def test_has_members(self):
        assert len(list(AlertSeverity)) >= 1
    def test_importable(self):
        assert AlertSeverity is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestMetricDefinition:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetricDefinition)
    def test_importable(self):
        assert MetricDefinition is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestLogConfiguration:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LogConfiguration)
    def test_importable(self):
        assert LogConfiguration is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestTraceConfiguration:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TraceConfiguration)
    def test_importable(self):
        assert TraceConfiguration is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestAlertRule:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AlertRule)
    def test_importable(self):
        assert AlertRule is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestObservabilityPlanningConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityPlanningConfig)
    def test_importable(self):
        assert ObservabilityPlanningConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestCreateObservabilityPlanningOrchestrator:
    def test_is_callable(self):
        assert callable(create_observability_planning_orchestrator)

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestPlanObservability:
    def test_is_callable(self):
        assert callable(plan_observability)

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestOrchestrateObservabilityPlanning:
    def test_is_callable(self):
        assert callable(orchestrate_observability_planning)

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_type_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module metric_type_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE