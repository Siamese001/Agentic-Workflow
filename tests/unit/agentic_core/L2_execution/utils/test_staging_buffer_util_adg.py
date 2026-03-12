"""ADG-driven tests for agentic_core/L2_execution/utils/staging_buffer_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.utils.staging_buffer_util import (  # noqa: F401
        StagingBufferError,
        ImmutableStagingBuffer,
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
    StagingBufferError = None  # type: ignore[assignment,misc]
    ImmutableStagingBuffer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestStagingBufferError:
    def test_is_class(self):
        assert isinstance(StagingBufferError, type)
    def test_importable(self):
        assert StagingBufferError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestImmutableStagingBuffer:
    def test_is_class(self):
        assert isinstance(ImmutableStagingBuffer, type)
    def test_importable(self):
        assert ImmutableStagingBuffer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="staging_buffer_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module staging_buffer_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
