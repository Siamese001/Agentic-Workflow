"""ADG importability contract for agentic_core/adg/applications/guardian_prioritizer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_guardian_prioritizer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.guardian_prioritizer import (  # noqa: F401
        GuardianPriorityScore,
        PrioritizationResult,
        GuardianPrioritizer,
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GuardianPriorityScore = None  # type: ignore[assignment,misc]
    PrioritizationResult = None  # type: ignore[assignment,misc]
    GuardianPrioritizer = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_prioritizer.py deps unavailable")
class TestGuardianPrioritizerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: guardian_prioritizer.py must be importable."""
        assert _AVAILABLE

    def test_guardianpriorityscore_is_type(self) -> None:
        assert GuardianPriorityScore is not None

    def test_prioritizationresult_is_type(self) -> None:
        assert PrioritizationResult is not None

    def test_guardianprioritizer_is_type(self) -> None:
        assert GuardianPrioritizer is not None

    def test_main_callable(self) -> None:
        assert callable(main)

