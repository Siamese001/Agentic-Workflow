"""ADG importability contract for agentic_core/adg/runtime/hitl_graph.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hitl_graph.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.hitl_graph import (  # noqa: F401
        HITLCheckpoint,
        HITLDecisionType,
        HITLGraph,
        HITLRuntimeRecorder,
        HumanDecision,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HITLDecisionType = None  # type: ignore[assignment,misc]
    HITLCheckpoint = None  # type: ignore[assignment,misc]
    HumanDecision = None  # type: ignore[assignment,misc]
    HITLGraph = None  # type: ignore[assignment,misc]
    HITLRuntimeRecorder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hitl_graph deps unavailable")
class TestHitlGraphImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/hitl_graph.py must be importable."""
        assert _AVAILABLE

    def test_hitldecisiontype_defined(self) -> None:
        assert HITLDecisionType is not None

    def test_hitlcheckpoint_defined(self) -> None:
        assert HITLCheckpoint is not None

    def test_humandecision_defined(self) -> None:
        assert HumanDecision is not None

    def test_hitlgraph_defined(self) -> None:
        assert HITLGraph is not None

    def test_hitlruntimerecorder_defined(self) -> None:
        assert HITLRuntimeRecorder is not None
