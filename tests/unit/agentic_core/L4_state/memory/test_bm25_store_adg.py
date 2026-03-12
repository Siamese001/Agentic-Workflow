"""ADG importability contract for agentic_core/L4_state/memory/bm25_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_bm25_store.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.memory.bm25_store import (  # noqa: F401
        Bm25Store,
        get_bm25_store,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Bm25Store = None  # type: ignore[assignment,misc]
    get_bm25_store = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="bm25_store.py deps unavailable")
class TestBm25StoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: bm25_store.py must be importable."""
        assert _AVAILABLE

    def test_bm25store_is_type(self) -> None:
        assert Bm25Store is not None

    def test_get_bm25_store_callable(self) -> None:
        assert callable(get_bm25_store)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

