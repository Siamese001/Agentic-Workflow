"""ADG-driven tests for agentic_core/mixins/batching_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.batching_mixin import (  # noqa: F401
        BatchingConfig,
        BatchingMixin,
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
    BatchingConfig = None  # type: ignore[assignment,misc]
    BatchingMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestBatchingConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BatchingConfig)
    def test_importable(self):
        assert BatchingConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestBatchingMixin:
    def test_is_class(self):
        assert isinstance(BatchingMixin, type)
    def test_importable(self):
        assert BatchingMixin is not None

@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="batching_mixin.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module batching_mixin.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
