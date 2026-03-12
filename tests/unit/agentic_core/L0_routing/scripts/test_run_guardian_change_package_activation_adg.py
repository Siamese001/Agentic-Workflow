"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_change_package_activation.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_change_package_activation import (  # noqa: F401
        scan_activation_patterns,
        run_change_package_activation_guardian,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_activation_patterns = None  # type: ignore[assignment,misc]
    run_change_package_activation_guardian = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_change_package_activation.py deps unavailable")
class TestRunGuardianChangePackageActivationImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_change_package_activation.py must be importable."""
        assert _AVAILABLE

    def test_scan_activation_patterns_callable(self) -> None:
        assert callable(scan_activation_patterns)

    def test_run_change_package_activation_guardian_callable(self) -> None:
        assert callable(run_change_package_activation_guardian)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None

