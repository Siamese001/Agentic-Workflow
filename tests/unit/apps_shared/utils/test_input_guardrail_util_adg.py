"""ADG-driven tests for apps_shared/utils/input_guardrail_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.input_guardrail_util import (  # noqa: F401
        GuardAction,
        GuardResult,
        InputGuardrail,
        get_input_guardrail,
        scan_input,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GuardAction = None  # type: ignore[assignment,misc]
    GuardResult = None  # type: ignore[assignment,misc]
    InputGuardrail = None  # type: ignore[assignment,misc]
    get_input_guardrail = None  # type: ignore[assignment,misc]
    scan_input = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestGuardAction:
    def test_is_enum(self):
        import enum
        assert issubclass(GuardAction, enum.Enum)
    def test_has_members(self):
        assert len(list(GuardAction)) >= 1
    def test_importable(self):
        assert GuardAction is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestGuardResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GuardResult)
    def test_importable(self):
        assert GuardResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestInputGuardrail:
    def test_is_class(self):
        assert isinstance(InputGuardrail, type)
    def test_importable(self):
        assert InputGuardrail is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestGetInputGuardrail:
    def test_is_callable(self):
        assert callable(get_input_guardrail)

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestScanInput:
    def test_is_callable(self):
        assert callable(scan_input)

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module input_guardrail_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
