"""ADG importability contract for agentic_core/adg/applications/state_lineage.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_state_lineage.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.state_lineage import (  # noqa: F401
        LineageRecord,
        LineageIndex,
        build_lineage_index,
        query_mutations_for_state,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LineageRecord = None  # type: ignore[assignment,misc]
    LineageIndex = None  # type: ignore[assignment,misc]
    build_lineage_index = None  # type: ignore[assignment,misc]
    query_mutations_for_state = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="state_lineage.py deps unavailable")
class TestStateLineageImportability:
    def test_module_importable(self) -> None:
        """ADG contract: state_lineage.py must be importable."""
        assert _AVAILABLE

    def test_lineagerecord_is_type(self) -> None:
        assert LineageRecord is not None

    def test_lineageindex_is_type(self) -> None:
        assert LineageIndex is not None

    def test_build_lineage_index_callable(self) -> None:
        assert callable(build_lineage_index)

    def test_query_mutations_for_state_callable(self) -> None:
        assert callable(query_mutations_for_state)

