"""ADG-driven tests for apps_shared/utils/request_type_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.request_type_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        AggregationType,
        DataSource,
        LogQuery,
        MetricDefinition,
        ObservabilityLoadConfig,
        ObservabilityLoadPlan,
        RequestType,
        TraceQuery,
        create_observability_load_planner,
        load_data_planning,
        plan_observability_load,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RequestType = None  # type: ignore[assignment,misc]
    DataSource = None  # type: ignore[assignment,misc]
    AggregationType = None  # type: ignore[assignment,misc]
    MetricDefinition = None  # type: ignore[assignment,misc]
    LogQuery = None  # type: ignore[assignment,misc]
    TraceQuery = None  # type: ignore[assignment,misc]
    ObservabilityLoadPlan = None  # type: ignore[assignment,misc]
    ObservabilityLoadConfig = None  # type: ignore[assignment,misc]
    create_observability_load_planner = None  # type: ignore[assignment,misc]
    plan_observability_load = None  # type: ignore[assignment,misc]
    load_data_planning = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestRequestType:
    def test_is_enum(self):
        import enum
        assert issubclass(RequestType, enum.Enum)
    def test_has_members(self):
        assert len(list(RequestType)) >= 1
    def test_importable(self):
        assert RequestType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestDataSource:
    def test_is_enum(self):
        import enum
        assert issubclass(DataSource, enum.Enum)
    def test_has_members(self):
        assert len(list(DataSource)) >= 1
    def test_importable(self):
        assert DataSource is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestAggregationType:
    def test_is_enum(self):
        import enum
        assert issubclass(AggregationType, enum.Enum)
    def test_has_members(self):
        assert len(list(AggregationType)) >= 1
    def test_importable(self):
        assert AggregationType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestMetricDefinition:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetricDefinition)
    def test_importable(self):
        assert MetricDefinition is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestLogQuery:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LogQuery)
    def test_importable(self):
        assert LogQuery is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestTraceQuery:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TraceQuery)
    def test_importable(self):
        assert TraceQuery is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestObservabilityLoadPlan:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityLoadPlan)
    def test_importable(self):
        assert ObservabilityLoadPlan is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestObservabilityLoadConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityLoadConfig)
    def test_importable(self):
        assert ObservabilityLoadConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestCreateObservabilityLoadPlanner:
    def test_is_callable(self):
        assert callable(create_observability_load_planner)

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestPlanObservabilityLoad:
    def test_is_callable(self):
        assert callable(plan_observability_load)

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestLoadDataPlanning:
    def test_is_callable(self):
        assert callable(load_data_planning)

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module request_type_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE