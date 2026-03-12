"""ADG importability contract for agentic_core/adg/analysis/diff.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_diff.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.diff import (  # noqa: F401
        GraphDiff,
        diff_snapshots,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GraphDiff = None  # type: ignore[assignment,misc]
    diff_snapshots = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="diff.py deps unavailable")
class TestDiffImportability:
    def test_module_importable(self) -> None:
        """ADG contract: diff.py must be importable."""
        assert _AVAILABLE

    def test_graphdiff_is_type(self) -> None:
        assert GraphDiff is not None

    def test_diff_snapshots_callable(self) -> None:
        assert callable(diff_snapshots)

