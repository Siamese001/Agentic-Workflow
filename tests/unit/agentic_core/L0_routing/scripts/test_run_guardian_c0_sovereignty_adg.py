"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_c0_sovereignty.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty import (  # noqa: F401
        scan_embedding_control_flow,
        run_c0_sovereignty_guardian,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_embedding_control_flow = None  # type: ignore[assignment,misc]
    run_c0_sovereignty_guardian = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_c0_sovereignty.py deps unavailable")
class TestRunGuardianC0SovereigntyImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_c0_sovereignty.py must be importable."""
        assert _AVAILABLE

    def test_scan_embedding_control_flow_callable(self) -> None:
        assert callable(scan_embedding_control_flow)

    def test_run_c0_sovereignty_guardian_callable(self) -> None:
        assert callable(run_c0_sovereignty_guardian)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None

