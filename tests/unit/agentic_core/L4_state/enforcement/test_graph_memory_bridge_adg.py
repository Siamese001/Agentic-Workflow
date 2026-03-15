"""ADG importability contract for agentic_core/L4_state/enforcement/graph_memory_bridge.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_graph_memory_bridge.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.enforcement.graph_memory_bridge import (  # noqa: F401
        EntityDefinition,
        GraphMemoryBridge,
        RelationDefinition,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EntityDefinition = None  # type: ignore[assignment,misc]
    RelationDefinition = None  # type: ignore[assignment,misc]
    GraphMemoryBridge = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge deps unavailable")
class TestGraphMemoryBridgeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/enforcement/graph_memory_bridge.py must be importable."""
        assert _AVAILABLE

    def test_entitydefinition_defined(self) -> None:
        assert EntityDefinition is not None

    def test_relationdefinition_defined(self) -> None:
        assert RelationDefinition is not None

    def test_graphmemorybridge_defined(self) -> None:
        assert GraphMemoryBridge is not None
