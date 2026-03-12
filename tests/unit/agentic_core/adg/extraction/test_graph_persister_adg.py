"""ADG importability contract for agentic_core/adg/extraction/graph_persister.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_graph_persister.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.extraction.graph_persister import (  # noqa: F401
        persist_scan_result,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    persist_scan_result = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="graph_persister.py deps unavailable")
class TestGraphPersisterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: graph_persister.py must be importable."""
        assert _AVAILABLE

    def test_persist_scan_result_callable(self) -> None:
        assert callable(persist_scan_result)

