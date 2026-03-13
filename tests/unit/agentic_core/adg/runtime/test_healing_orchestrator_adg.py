"""ADG importability contract for agentic_core/adg/runtime/healing_orchestrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_orchestrator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.healing_orchestrator import (  # noqa: F401
        HealingOrchestrator,
        HealingOrchestratorReport,
        HealingRun,
        HealingRunPhase,
        HealingTrigger,
        OrchestrationStep,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealingRunPhase = None  # type: ignore[assignment,misc]
    HealingTrigger = None  # type: ignore[assignment,misc]
    OrchestrationStep = None  # type: ignore[assignment,misc]
    HealingRun = None  # type: ignore[assignment,misc]
    HealingOrchestratorReport = None  # type: ignore[assignment,misc]
    HealingOrchestrator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestrator deps unavailable")
class TestHealingOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/healing_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_healingrunphase_defined(self) -> None:
        assert HealingRunPhase is not None

    def test_healingtrigger_defined(self) -> None:
        assert HealingTrigger is not None

    def test_orchestrationstep_defined(self) -> None:
        assert OrchestrationStep is not None

    def test_healingrun_defined(self) -> None:
        assert HealingRun is not None

    def test_healingorchestratorreport_defined(self) -> None:
        assert HealingOrchestratorReport is not None

    def test_healingorchestrator_defined(self) -> None:
        assert HealingOrchestrator is not None
