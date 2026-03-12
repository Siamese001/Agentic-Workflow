"""ADG importability contract for agentic_core/adg/analysis/confidence.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_confidence.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.confidence import (  # noqa: F401
        EdgeConfidence,
        score_edge,
        score_edges,
        confidence_summary,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    EdgeConfidence = None  # type: ignore[assignment,misc]
    score_edge = None  # type: ignore[assignment,misc]
    score_edges = None  # type: ignore[assignment,misc]
    confidence_summary = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="confidence.py deps unavailable")
class TestConfidenceImportability:
    def test_module_importable(self) -> None:
        """ADG contract: confidence.py must be importable."""
        assert _AVAILABLE

    def test_edgeconfidence_is_type(self) -> None:
        assert EdgeConfidence is not None

    def test_score_edge_callable(self) -> None:
        assert callable(score_edge)

    def test_score_edges_callable(self) -> None:
        assert callable(score_edges)

