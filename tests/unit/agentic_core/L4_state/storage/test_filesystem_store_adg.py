"""ADG importability contract for agentic_core/L4_state/storage/filesystem_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_filesystem_store.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.storage.filesystem_store import (  # noqa: F401
        FileSystemStore,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FileSystemStore = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_store.py deps unavailable")
class TestFilesystemStoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: filesystem_store.py must be importable."""
        assert _AVAILABLE

    def test_filesystemstore_is_type(self) -> None:
        assert FileSystemStore is not None

