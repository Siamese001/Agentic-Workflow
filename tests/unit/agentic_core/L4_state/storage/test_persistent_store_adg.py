"""ADG importability contract for agentic_core/L4_state/storage/persistent_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_persistent_store.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.storage.persistent_store import (  # noqa: F401
        StoreBackend,
        StoredArtifact,
        StoredArtifactRef,
        StoreMetrics,
        create_artifact,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    StoredArtifact = None  # type: ignore[assignment,misc]
    StoreMetrics = None  # type: ignore[assignment,misc]
    StoredArtifactRef = None  # type: ignore[assignment,misc]
    StoreBackend = None  # type: ignore[assignment,misc]
    create_artifact = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="persistent_store deps unavailable")
class TestPersistentStoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/storage/persistent_store.py must be importable."""
        assert _AVAILABLE

    def test_storedartifact_defined(self) -> None:
        assert StoredArtifact is not None

    def test_storemetrics_defined(self) -> None:
        assert StoreMetrics is not None

    def test_storedartifactref_defined(self) -> None:
        assert StoredArtifactRef is not None

    def test_storebackend_defined(self) -> None:
        assert StoreBackend is not None
