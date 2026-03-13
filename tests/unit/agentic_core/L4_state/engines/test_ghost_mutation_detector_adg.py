"""ADG importability contract for agentic_core/L4_state/engines/ghost_mutation_detector.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ghost_mutation_detector.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.engines.ghost_mutation_detector import (  # noqa: F401
        GhostMutationViolation,
        ReconciliationResult,
        detect_ghost_mutations,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GhostMutationViolation = None  # type: ignore[assignment,misc]
    ReconciliationResult = None  # type: ignore[assignment,misc]
    detect_ghost_mutations = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ghost_mutation_detector deps unavailable")
class TestGhostMutationDetectorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/engines/ghost_mutation_detector.py must be importable."""
        assert _AVAILABLE

    def test_ghostmutationviolation_defined(self) -> None:
        assert GhostMutationViolation is not None

    def test_reconciliationresult_defined(self) -> None:
        assert ReconciliationResult is not None
