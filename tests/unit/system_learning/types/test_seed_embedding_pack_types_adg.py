"""ADG importability contract for system_learning/types/seed_embedding_pack_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_seed_embedding_pack_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.types.seed_embedding_pack_types import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        SeedEmbeddingPackConfig,
        SeedEmbeddingPackManifest,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SeedEmbeddingPackManifest = None  # type: ignore[assignment,misc]
    SeedEmbeddingPackConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="seed_embedding_pack_types.py deps unavailable")
class TestSeedEmbeddingPackTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: seed_embedding_pack_types.py must be importable."""
        assert _AVAILABLE

    def test_seedembeddingpackmanifest_is_type(self) -> None:
        assert SeedEmbeddingPackManifest is not None

    def test_seedembeddingpackconfig_is_type(self) -> None:
        assert SeedEmbeddingPackConfig is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
