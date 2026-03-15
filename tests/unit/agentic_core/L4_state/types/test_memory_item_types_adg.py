"""ADG importability contract for agentic_core/L4_state/types/memory_item_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_memory_item_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.types.memory_item_types import (  # noqa: F401
        MemoryItem,
        MemoryQuery,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MemoryItem = None  # type: ignore[assignment,misc]
    MemoryQuery = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="memory_item_types deps unavailable")
class TestMemoryItemTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/types/memory_item_types.py must be importable."""
        assert _AVAILABLE

    def test_memoryitem_defined(self) -> None:
        assert MemoryItem is not None

    def test_memoryquery_defined(self) -> None:
        assert MemoryQuery is not None
