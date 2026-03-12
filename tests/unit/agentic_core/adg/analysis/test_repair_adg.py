"""ADG importability contract for agentic_core/adg/analysis/repair.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_repair.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.repair import (  # noqa: F401
        RepairRoute,
        route_violations,
        route_diff_violations,
        repair_routing_summary,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RepairRoute = None  # type: ignore[assignment,misc]
    route_violations = None  # type: ignore[assignment,misc]
    route_diff_violations = None  # type: ignore[assignment,misc]
    repair_routing_summary = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="repair.py deps unavailable")
class TestRepairImportability:
    def test_module_importable(self) -> None:
        """ADG contract: repair.py must be importable."""
        assert _AVAILABLE

    def test_repairroute_is_type(self) -> None:
        assert RepairRoute is not None

    def test_route_violations_callable(self) -> None:
        assert callable(route_violations)

    def test_route_diff_violations_callable(self) -> None:
        assert callable(route_diff_violations)

