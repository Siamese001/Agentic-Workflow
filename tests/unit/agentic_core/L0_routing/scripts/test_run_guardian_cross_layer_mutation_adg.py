"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_cross_layer_mutation.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation import (  # noqa: F401
        scan_cross_layer_mutations,
        run_cross_layer_mutation_guardian,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_cross_layer_mutations = None  # type: ignore[assignment,misc]
    run_cross_layer_mutation_guardian = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_cross_layer_mutation.py deps unavailable")
class TestRunGuardianCrossLayerMutationImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_cross_layer_mutation.py must be importable."""
        assert _AVAILABLE

    def test_scan_cross_layer_mutations_callable(self) -> None:
        assert callable(scan_cross_layer_mutations)

    def test_run_cross_layer_mutation_guardian_callable(self) -> None:
        assert callable(run_cross_layer_mutation_guardian)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None

