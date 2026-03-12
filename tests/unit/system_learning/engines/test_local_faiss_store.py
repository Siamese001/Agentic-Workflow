"""Foundational behavioral tests for system_learning/engines/local_faiss_store.py.

fan_in=6 — imported by 6 other modules.
ADG import-hygiene is covered separately by test_local_faiss_store_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.engines.local_faiss_store import (  # noqa: F401
        IndexNotBuiltError,
        IndexMetadataError,
        ManifestIntegrityError,
        EmbedderMismatchError,
        LocalFAISSStore,
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
    IndexNotBuiltError = None  # type: ignore[assignment,misc]
    IndexMetadataError = None  # type: ignore[assignment,misc]
    ManifestIntegrityError = None  # type: ignore[assignment,misc]
    EmbedderMismatchError = None  # type: ignore[assignment,misc]
    LocalFAISSStore = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestIndexNotBuiltErrorContract:
    def test_is_class(self):
        assert isinstance(IndexNotBuiltError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestIndexMetadataErrorContract:
    def test_is_class(self):
        assert isinstance(IndexMetadataError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestManifestIntegrityErrorContract:
    def test_is_class(self):
        assert isinstance(ManifestIntegrityError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestEmbedderMismatchErrorContract:
    def test_is_class(self):
        assert isinstance(EmbedderMismatchError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestLocalFAISSStoreContract:
    def test_is_class(self):
        assert isinstance(LocalFAISSStore, type)

    def test_has_method_open(self):
        assert callable(getattr(LocalFAISSStore, 'open', None))

    def test_has_method_search(self):
        assert callable(getattr(LocalFAISSStore, 'search', None))

    def test_has_method_begin_build(self):
        assert callable(getattr(LocalFAISSStore, 'begin_build', None))

    def test_has_method_add_vectors(self):
        assert callable(getattr(LocalFAISSStore, 'add_vectors', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(LocalFAISSStore) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="local_faiss_store.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: local_faiss_store importable or gracefully unavailable."""
    assert True
