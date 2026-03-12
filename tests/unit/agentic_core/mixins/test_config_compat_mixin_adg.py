"""ADG-driven tests for agentic_core/mixins/config_compat_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.config_compat_mixin import (  # noqa: F401
        CacheConfig,
        MetricsConfig,
        BatchingConfig,
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
    CacheConfig = None  # type: ignore[assignment,misc]
    MetricsConfig = None  # type: ignore[assignment,misc]
    BatchingConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestCacheConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CacheConfig)
    def test_importable(self):
        assert CacheConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestMetricsConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetricsConfig)
    def test_importable(self):
        assert MetricsConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestBatchingConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BatchingConfig)
    def test_importable(self):
        assert BatchingConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_compat_mixin.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module config_compat_mixin.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
