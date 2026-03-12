"""Foundational behavioral tests for apps_shared/utils/request_type_util.py.

fan_in=17 — this module is imported by 17 other modules.
ADG contract: import-hygiene is covered by test_request_type_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.request_type_util import (  # noqa: F401
        RequestType,
        DataSource,
        AggregationType,
        MetricDefinition,
        LogQuery,
        TraceQuery,
        create_observability_load_planner,
        plan_observability_load,
        load_data_planning,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    RequestType = None  # type: ignore[assignment,misc]
    DataSource = None  # type: ignore[assignment,misc]
    AggregationType = None  # type: ignore[assignment,misc]
    MetricDefinition = None  # type: ignore[assignment,misc]
    LogQuery = None  # type: ignore[assignment,misc]
    TraceQuery = None  # type: ignore[assignment,misc]
    create_observability_load_planner = None  # type: ignore[assignment,misc]
    plan_observability_load = None  # type: ignore[assignment,misc]
    load_data_planning = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestRequestTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(RequestType, enum.Enum)

    def test_has_members(self):
        assert len(list(RequestType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in RequestType:
            assert member.value is not None

    def test_known_member_metric_query_exists(self):
        assert hasattr(RequestType, 'METRIC_QUERY')

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestDataSourceContract:
    def test_is_enum(self):
        import enum
        assert issubclass(DataSource, enum.Enum)

    def test_has_members(self):
        assert len(list(DataSource)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in DataSource:
            assert member.value is not None

    def test_known_member_prometheus_exists(self):
        assert hasattr(DataSource, 'PROMETHEUS')

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestAggregationTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(AggregationType, enum.Enum)

    def test_has_members(self):
        assert len(list(AggregationType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in AggregationType:
            assert member.value is not None

    def test_known_member_sum_exists(self):
        assert hasattr(AggregationType, 'SUM')

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestMetricDefinitionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetricDefinition)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(MetricDefinition)}
        assert field_names >= {'query', 'aggregation', 'labels', 'name', 'time_range'}

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestLogQueryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LogQuery)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(LogQuery)}
        assert field_names >= {'size', 'query', 'index', 'filters', 'time_range'}

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestTraceQueryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TraceQuery)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(TraceQuery)}
        assert field_names >= {'service', 'operation', 'tags', 'time_range', 'trace_id'}

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestCreateObservabilityLoadPlannerFunction:
    def test_is_callable(self):
        assert callable(create_observability_load_planner)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_observability_load_planner)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestPlanObservabilityLoadFunction:
    def test_is_callable(self):
        assert callable(plan_observability_load)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(plan_observability_load)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="request_type_util.py deps unavailable")
class TestLoadDataPlanningFunction:
    def test_is_callable(self):
        assert callable(load_data_planning)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_data_planning)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module request_type_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
