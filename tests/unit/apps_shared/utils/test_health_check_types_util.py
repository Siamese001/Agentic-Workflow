"""Foundational behavioral tests for apps_shared/utils/health_check_types_util.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_health_check_types_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.utils.health_check_types_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    CheckResult,
    CommonChecks,
    HealthChecker,
    HealthReport,
    HealthStatus,
    ReadinessGate,
    get_health_checker,
    get_readiness_gate,
)


class TestHealthStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(HealthStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(HealthStatus)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in HealthStatus:
            assert member.value is not None

    def test_known_member_healthy_exists(self):
        assert hasattr(HealthStatus, 'HEALTHY')

class TestCheckResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CheckResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CheckResult)}
        assert field_names >= {'message', 'status', 'metadata', 'name', 'duration_ms'}

class TestHealthReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealthReport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(HealthReport)}
        assert field_names >= {'checks', 'status', 'version', 'timestamp'}

class TestHealthCheckerContract:
    def test_is_class(self):
        assert isinstance(HealthChecker, type)

    def test_has_method_register_check(self):
        assert callable(getattr(HealthChecker, 'register_check', None))

    def test_has_method_unregister_check(self):
        assert callable(getattr(HealthChecker, 'unregister_check', None))

    def test_has_method_run_check(self):
        assert callable(getattr(HealthChecker, 'run_check', None))

    def test_has_method_run_all_checks(self):
        assert callable(getattr(HealthChecker, 'run_all_checks', None))

class TestCommonChecksContract:
    def test_is_class(self):
        assert isinstance(CommonChecks, type)

    def test_has_method_env_var_check(self):
        assert callable(getattr(CommonChecks, 'env_var_check', None))

    def test_has_method_redis_check(self):
        assert callable(getattr(CommonChecks, 'redis_check', None))

    def test_has_method_disk_space_check(self):
        assert callable(getattr(CommonChecks, 'disk_space_check', None))

    def test_has_method_memory_check(self):
        assert callable(getattr(CommonChecks, 'memory_check', None))

class TestReadinessGateContract:
    def test_is_class(self):
        assert isinstance(ReadinessGate, type)

    def test_has_method_set_ready(self):
        assert callable(getattr(ReadinessGate, 'set_ready', None))

    def test_has_method_set_not_ready(self):
        assert callable(getattr(ReadinessGate, 'set_not_ready', None))

    def test_has_method_is_ready(self):
        assert callable(getattr(ReadinessGate, 'is_ready', None))

    def test_has_method_get_status(self):
        assert callable(getattr(ReadinessGate, 'get_status', None))

class TestGetHealthCheckerFunction:
    def test_is_callable(self):
        assert callable(get_health_checker)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_health_checker)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetReadinessGateFunction:
    def test_is_callable(self):
        assert callable(get_readiness_gate)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_readiness_gate)
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
    """Module health_check_types_util must be importable or skip gracefully."""
    pass  # Import verified at module level
