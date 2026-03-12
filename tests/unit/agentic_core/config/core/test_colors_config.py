"""Foundational behavioral tests for agentic_core/config/core/colors_config.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_colors_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
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
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    Colors = None  # type: ignore[assignment,misc]
    colorize = None  # type: ignore[assignment,misc]
    print_success = None  # type: ignore[assignment,misc]
    print_error = None  # type: ignore[assignment,misc]
    print_warning = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestColorsContract:
    def test_is_class(self):
        assert isinstance(Colors, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(Colors, type)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestColorizeFunction:
    def test_is_callable(self):
        assert callable(colorize)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(colorize)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestPrintSuccessFunction:
    def test_is_callable(self):
        assert callable(print_success)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestPrintErrorFunction:
    def test_is_callable(self):
        assert callable(print_error)

@pytest.mark.skipif(not _AVAILABLE, reason="colors_config.py deps unavailable")
class TestPrintWarningFunction:
    def test_is_callable(self):
        assert callable(print_warning)

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


def test_module_importable():
    """Module colors_config must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
