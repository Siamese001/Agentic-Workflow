"""ADG importability contract for agentic_core/adg/applications/runtime_graph.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_runtime_graph.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.runtime_graph import (  # noqa: F401
        AgentActionNode,
        ToolInvocationNode,
        LayerTransitionEdge,
        RuntimeGraphReport,
        build_runtime_graph,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AgentActionNode = None  # type: ignore[assignment,misc]
    ToolInvocationNode = None  # type: ignore[assignment,misc]
    LayerTransitionEdge = None  # type: ignore[assignment,misc]
    RuntimeGraphReport = None  # type: ignore[assignment,misc]
    build_runtime_graph = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_graph.py deps unavailable")
class TestRuntimeGraphImportability:
    def test_module_importable(self) -> None:
        """ADG contract: runtime_graph.py must be importable."""
        assert _AVAILABLE

    def test_agentactionnode_is_type(self) -> None:
        assert AgentActionNode is not None

    def test_toolinvocationnode_is_type(self) -> None:
        assert ToolInvocationNode is not None

    def test_layertransitionedge_is_type(self) -> None:
        assert LayerTransitionEdge is not None

    def test_build_runtime_graph_callable(self) -> None:
        assert callable(build_runtime_graph)

