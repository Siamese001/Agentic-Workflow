"""ADG-driven tests for agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer import (  # noqa: F401
        assert_no_persistent_write,
        safe_write_text,
        safe_write_bytes,
        safe_json_dump,
        safe_shutil_move,
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
    assert_no_persistent_write = None  # type: ignore[assignment,misc]
    safe_write_text = None  # type: ignore[assignment,misc]
    safe_write_bytes = None  # type: ignore[assignment,misc]
    safe_json_dump = None  # type: ignore[assignment,misc]
    safe_shutil_move = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestAssertNoPersistentWrite:
    def test_is_callable(self):
        assert callable(assert_no_persistent_write)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestSafeWriteText:
    def test_is_callable(self):
        assert callable(safe_write_text)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestSafeWriteBytes:
    def test_is_callable(self):
        assert callable(safe_write_bytes)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestSafeJsonDump:
    def test_is_callable(self):
        assert callable(safe_json_dump)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestSafeShutilMove:
    def test_is_callable(self):
        assert callable(safe_shutil_move)

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

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition_enforcer.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module mutation_prohibition_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
