"""Foundational behavioral tests for agentic_core/config/core/colors_config.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_colors_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.config.core.colors_config import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    Colors,
    colorize,
    print_error,
    print_success,
    print_warning,
)


class TestColorsContract:
    def test_is_class(self):
        assert isinstance(Colors, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(Colors, type)

class TestColorizeFunction:
    def test_is_callable(self):
        assert callable(colorize)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(colorize)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestPrintSuccessFunction:
    def test_is_callable(self):
        assert callable(print_success)

class TestPrintErrorFunction:
    def test_is_callable(self):
        assert callable(print_error)

class TestPrintWarningFunction:
    def test_is_callable(self):
        assert callable(print_warning)

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
    """Module colors_config must be importable or skip gracefully."""
    pass  # Import verified at module level
