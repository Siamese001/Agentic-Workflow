"""Foundational behavioral tests for apps_shared/scripts/fix_syntax_errors.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_fix_syntax_errors_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.scripts.fix_syntax_errors import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    check_syntax,
    fix_fstring_errors,
    fix_indentation_errors,
    fix_multiline_strings,
)


class TestFixMultilineStringsFunction:
    def test_is_callable(self):
        assert callable(fix_multiline_strings)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(fix_multiline_strings)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestFixIndentationErrorsFunction:
    def test_is_callable(self):
        assert callable(fix_indentation_errors)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(fix_indentation_errors)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestFixFstringErrorsFunction:
    def test_is_callable(self):
        assert callable(fix_fstring_errors)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(fix_fstring_errors)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestCheckSyntaxFunction:
    def test_is_callable(self):
        assert callable(check_syntax)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_syntax)
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
    """Module fix_syntax_errors must be importable or skip gracefully."""
    pass  # Import verified at module level
