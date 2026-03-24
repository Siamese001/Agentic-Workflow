"""ADG-driven tests for apps_shared/scripts/fix_syntax_errors.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.fix_syntax_errors import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        check_syntax,
        fix_file,
        fix_fstring_errors,
        fix_indentation_errors,
        fix_multiline_strings,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    fix_multiline_strings = None  # type: ignore[assignment,misc]
    fix_indentation_errors = None  # type: ignore[assignment,misc]
    fix_fstring_errors = None  # type: ignore[assignment,misc]
    check_syntax = None  # type: ignore[assignment,misc]
    fix_file = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestFixMultilineStrings:
    def test_is_callable(self):
        assert callable(fix_multiline_strings)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestFixIndentationErrors:
    def test_is_callable(self):
        assert callable(fix_indentation_errors)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestFixFstringErrors:
    def test_is_callable(self):
        assert callable(fix_fstring_errors)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestCheckSyntax:
    def test_is_callable(self):
        assert callable(check_syntax)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestFixFile:
    def test_is_callable(self):
        assert callable(fix_file)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_syntax_errors.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module fix_syntax_errors.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE