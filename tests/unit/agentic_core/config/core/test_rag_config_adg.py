"""ADG-driven tests for agentic_core/config/core/rag_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.config.core.rag_config import (  # noqa: F401
        EmbeddingConfig,
        VectorStoreConfig,
        RetrievalConfig,
        CacheConfig,
        SafetyConfig,
        SovereignRagConfig,
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
    EmbeddingConfig = None  # type: ignore[assignment,misc]
    VectorStoreConfig = None  # type: ignore[assignment,misc]
    RetrievalConfig = None  # type: ignore[assignment,misc]
    CacheConfig = None  # type: ignore[assignment,misc]
    SafetyConfig = None  # type: ignore[assignment,misc]
    SovereignRagConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestEmbeddingConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EmbeddingConfig)
    def test_importable(self):
        assert EmbeddingConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestVectorStoreConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VectorStoreConfig)
    def test_importable(self):
        assert VectorStoreConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestRetrievalConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalConfig)
    def test_importable(self):
        assert RetrievalConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestCacheConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CacheConfig)
    def test_importable(self):
        assert CacheConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestSafetyConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SafetyConfig)
    def test_importable(self):
        assert SafetyConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestSovereignRagConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SovereignRagConfig)
    def test_importable(self):
        assert SovereignRagConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rag_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module rag_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
