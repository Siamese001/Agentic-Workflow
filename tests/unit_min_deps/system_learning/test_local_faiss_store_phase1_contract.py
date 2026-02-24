"""Phase 1 contract tests for LocalFAISSStore and IndexBuildMetadata.

Tests imports succeed without optional dependencies, deterministic canonical JSON,
and that faiss is not imported at module level.
"""

import sys

import pytest

from system_learning.engines.local_faiss_store import LocalFAISSStore
from system_learning.types.index_build_metadata_types import IndexBuildMetadata

pytestmark = pytest.mark.unit_min_deps


def test_imports_succeed_without_faiss():
    """Test that modules import successfully without faiss installed."""
    # This test passes if the import statements above succeed
    # faiss should not be imported at module level
    assert "faiss" not in sys.modules, "faiss should not be imported at module import time"


def test_index_build_metadata_canonical_json_bytes():
    """Test IndexBuildMetadata.to_canonical_json_bytes() is deterministic and ASCII-only."""
    # Create metadata instance
    metadata = IndexBuildMetadata(
        index_id="test_index_v1",
        faiss_version="1.7.4",
        build_seed=42,
        canonicalization_version="canon-v1",
        embedding_model_version="text-embedding-004-v1",
        embedding_model_checksum="0" * 64,  # 64 zeros for test
        built_at_utc=1700000000,
        index_version_hash="1" * 64,  # 64 ones for test
        vector_count=1000,
        dimension=768,
    )

    # Get canonical bytes twice
    bytes1 = metadata.to_canonical_json_bytes()
    bytes2 = metadata.to_canonical_json_bytes()

    # Test ASCII-only
    assert all(c < 128 for c in bytes1), "Canonical JSON bytes must be ASCII-only"

    # Test deterministic (same bytes on 2 calls)
    assert bytes1 == bytes2, "Canonical JSON bytes must be deterministic"

    # Test it's valid JSON
    import json

    parsed = json.loads(bytes1.decode("ascii"))
    assert parsed["index_id"] == "test_index_v1"
    assert parsed["build_seed"] == 42


def test_local_faiss_store_exposes_contract_methods():
    """Test LocalFAISSStore exposes required open/search methods."""
    store = LocalFAISSStore(base_path="/tmp/test")

    # Test required attributes exist
    assert hasattr(store, "open"), "LocalFAISSStore must have open() method"
    assert hasattr(store, "search"), "LocalFAISSStore must have search() method"

    # Test they are callable
    assert callable(store.open), "open() must be callable"
    assert callable(store.search), "search() must be callable"

    # Test Phase 1: RuntimeError when faiss not available (lazy import)
    with pytest.raises(RuntimeError, match="FAISS is required"):
        store.open("test_index")

    with pytest.raises(RuntimeError, match="FAISS is required"):
        store.search("test_index", [0.1] * 768, 5, 0.5)
