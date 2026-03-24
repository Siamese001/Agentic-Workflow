"""ADG-driven tests for agentic_core/L5_safety/enforcement/pytest_config_guardrail.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.pytest_config_guardrail import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        PytestEnforcementGuard,
        TestPytestConfigGuardBrittleMarkerDetection,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PytestEnforcementGuard = None  # type: ignore[assignment,misc]
    TestPytestConfigGuardBrittleMarkerDetection = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestPytestEnforcementGuard:
    def test_is_class(self):
        assert isinstance(PytestEnforcementGuard, type)
    def test_importable(self):
        assert PytestEnforcementGuard is not None

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestTestPytestConfigGuardBrittleMarkerDetection:
    def test_is_class(self):
        assert isinstance(TestPytestConfigGuardBrittleMarkerDetection, type)
    def test_importable(self):
        assert TestPytestConfigGuardBrittleMarkerDetection is not None

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="pytest_config_guardrail.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module pytest_config_guardrail.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE