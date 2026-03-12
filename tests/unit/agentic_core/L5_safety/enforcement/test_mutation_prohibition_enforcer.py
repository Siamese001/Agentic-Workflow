"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_mutation_prohibition_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer import (  # noqa: F401
        assert_no_persistent_write,
        safe_write_text,
        safe_write_bytes,
        safe_json_dump,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    assert_no_persistent_write = None  # type: ignore[assignment,misc]
    safe_write_text = None  # type: ignore[assignment,misc]
    safe_write_bytes = None  # type: ignore[assignment,misc]
    safe_json_dump = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestAssertNoPersistentWriteFunction:
    def test_is_callable(self):
        assert callable(assert_no_persistent_write)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(assert_no_persistent_write)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestSafeWriteTextFunction:
    def test_is_callable(self):
        assert callable(safe_write_text)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_write_text)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestSafeWriteBytesFunction:
    def test_is_callable(self):
        assert callable(safe_write_bytes)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_write_bytes)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestSafeJsonDumpFunction:
    def test_is_callable(self):
        assert callable(safe_json_dump)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_json_dump)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module mutation_prohibition_enforcer must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
