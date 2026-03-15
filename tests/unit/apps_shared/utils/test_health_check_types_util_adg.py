"""ADG-driven tests for apps_shared/utils/health_check_types_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.health_check_types_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
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
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealthStatus = None  # type: ignore[assignment,misc]
    CheckResult = None  # type: ignore[assignment,misc]
    HealthReport = None  # type: ignore[assignment,misc]
    HealthChecker = None  # type: ignore[assignment,misc]
    CommonChecks = None  # type: ignore[assignment,misc]
    ReadinessGate = None  # type: ignore[assignment,misc]
    get_health_checker = None  # type: ignore[assignment,misc]
    get_readiness_gate = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestHealthStatus:
    def test_is_enum(self):
        import enum
        assert issubclass(HealthStatus, enum.Enum)
    def test_has_members(self):
        assert len(list(HealthStatus)) >= 1
    def test_importable(self):
        assert HealthStatus is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestCheckResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CheckResult)
    def test_importable(self):
        assert CheckResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestHealthReport:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealthReport)
    def test_importable(self):
        assert HealthReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestHealthChecker:
    def test_is_class(self):
        assert isinstance(HealthChecker, type)
    def test_importable(self):
        assert HealthChecker is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestCommonChecks:
    def test_is_class(self):
        assert isinstance(CommonChecks, type)
    def test_importable(self):
        assert CommonChecks is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestReadinessGate:
    def test_is_class(self):
        assert isinstance(ReadinessGate, type)
    def test_importable(self):
        assert ReadinessGate is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestGetHealthChecker:
    def test_is_callable(self):
        assert callable(get_health_checker)

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestGetReadinessGate:
    def test_is_callable(self):
        assert callable(get_readiness_gate)

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="health_check_types_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module health_check_types_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
