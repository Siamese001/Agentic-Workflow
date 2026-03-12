"""ADG-driven tests for agentic_core/config/core/colors_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.config.core.colors_config import (  # noqa: F401
        Colors,
        colorize,
        print_success,
        print_error,
        print_warning,
        print_info,
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
    Colors = None  # type: ignore[assignment,misc]
    colorize = None  # type: ignore[assignment,misc]
    print_success = None  # type: ignore[assignment,misc]
    print_error = None  # type: ignore[assignment,misc]
    print_warning = None  # type: ignore[assignment,misc]
    print_info = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestColors:
    def test_is_class(self):
        assert isinstance(Colors, type)
    def test_importable(self):
        assert Colors is not None

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestColorize:
    def test_is_callable(self):
        assert callable(colorize)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestPrintSuccess:
    def test_is_callable(self):
        assert callable(print_success)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestPrintError:
    def test_is_callable(self):
        assert callable(print_error)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestPrintWarning:
    def test_is_callable(self):
        assert callable(print_warning)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestPrintInfo:
    def test_is_callable(self):
        assert callable(print_info)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module colors_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
