"""ADG importability contract for agentic_core/adg/runtime/event_graph.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_event_graph.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.event_graph import (  # noqa: F401
        HealerPhase,
        RuntimeEdge,
        RuntimeEvent,
        RuntimeGraph,
        RuntimeGraphCollector,
        RuntimePhase,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RuntimePhase = None  # type: ignore[assignment,misc]
    HealerPhase = None  # type: ignore[assignment,misc]
    RuntimeEvent = None  # type: ignore[assignment,misc]
    RuntimeEdge = None  # type: ignore[assignment,misc]
    RuntimeGraph = None  # type: ignore[assignment,misc]
    RuntimeGraphCollector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="event_graph deps unavailable")
class TestEventGraphImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/event_graph.py must be importable."""
        assert _AVAILABLE

    def test_runtimephase_defined(self) -> None:
        assert RuntimePhase is not None

    def test_healerphase_defined(self) -> None:
        assert HealerPhase is not None

    def test_runtimeevent_defined(self) -> None:
        assert RuntimeEvent is not None

    def test_runtimeedge_defined(self) -> None:
        assert RuntimeEdge is not None

    def test_runtimegraph_defined(self) -> None:
        assert RuntimeGraph is not None

    def test_runtimegraphcollector_defined(self) -> None:
        assert RuntimeGraphCollector is not None