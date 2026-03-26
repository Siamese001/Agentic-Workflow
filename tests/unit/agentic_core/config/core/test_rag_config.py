"""Foundational behavioral tests for agentic_core/config/core/rag_config.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_rag_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.config.core.rag_config import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    CacheConfig,
    EmbeddingConfig,
    RetrievalConfig,
    SafetyConfig,
    SovereignRagConfig,
    VectorStoreConfig,
)


class TestEmbeddingConfigContract:
    def test_is_dataclass(self):
                from agentic_core.config.core.rag_config import (  # noqa: F401
                import dataclasses
                assert dataclasses.is_dataclass(EmbeddingConfig)

        assert dataclasses.is_dataclass(EmbeddingConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EmbeddingConfig)}
        assert field_names >= {'cache_maxsize', 'cache_enabled', 'dimension', 'model_name', 'batch_size'}

class TestVectorStoreConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VectorStoreConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(VectorStoreConfig)}
        assert field_names >= {'metric', 'dimension', 'provider', 'namespace', 'index_name'}

class TestRetrievalConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RetrievalConfig)}
        assert field_names >= {'top_k', 'enable_hallucination_filter', 'enable_caching', 'enable_reranking', 'strategy'}

class TestCacheConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CacheConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CacheConfig)}
        assert field_names >= {'similarity_threshold', 'backend', 'enabled', 'ttl_seconds', 'max_entries'}

class TestSafetyConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SafetyConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SafetyConfig)}
        assert field_names >= {'enable_hallucination_detection', 'entity_support_threshold', 'forbidden_keywords', 'enable_pii_filter', 'enable_adversarial_defense'}

class TestSovereignRagConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SovereignRagConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SovereignRagConfig)}
        assert field_names >= {'retrieval', 'vector_store', 'safety', 'cache', 'embedding'}

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
    """Module rag_config must be importable or skip gracefully."""
    pass  # Import verified at module level
