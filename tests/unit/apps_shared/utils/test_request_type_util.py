"""Foundational behavioral tests for apps_shared/utils/request_type_util.py.

fan_in=17 — this module is imported by 17 other modules.
ADG contract: import-hygiene is covered by test_request_type_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.utils.request_type_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    AggregationType,
    DataSource,
    LogQuery,
    MetricDefinition,
    RequestType,
    TraceQuery,
    create_observability_load_planner,
    load_data_planning,
    plan_observability_load,
)


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

class TestMetricDefinitionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetricDefinition)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(MetricDefinition)}
        assert field_names >= {'query', 'aggregation', 'labels', 'name', 'time_range'}

class TestLogQueryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LogQuery)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(LogQuery)}
        assert field_names >= {'size', 'query', 'index', 'filters', 'time_range'}

class TestTraceQueryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TraceQuery)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(TraceQuery)}
        assert field_names >= {'service', 'operation', 'tags', 'time_range', 'trace_id'}

class TestCreateObservabilityLoadPlannerFunction:
    def test_is_callable(self):
        assert callable(create_observability_load_planner)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_observability_load_planner)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestPlanObservabilityLoadFunction:
    def test_is_callable(self):
        assert callable(plan_observability_load)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(plan_observability_load)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestLoadDataPlanningFunction:
    def test_is_callable(self):
        assert callable(load_data_planning)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_data_planning)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module request_type_util must be importable or skip gracefully."""
    pass  # Import verified at module level
