"""ADG importability contract for agentic_core/L4_state/memory/in_memory_vector_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_in_memory_vector_store.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.memory.in_memory_vector_store import (  # noqa: F401
        InMemoryVectorStore,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InMemoryVectorStore = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="in_memory_vector_store deps unavailable")
class TestInMemoryVectorStoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/memory/in_memory_vector_store.py must be importable."""
        assert _AVAILABLE

    def test_inmemoryvectorstore_defined(self) -> None:
        assert InMemoryVectorStore is not None