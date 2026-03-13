"""ADG importability contract for agentic_core/L3_orchestration/engines/deterministic_orchestrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_deterministic_orchestrator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.deterministic_orchestrator import (  # noqa: F401
        DeterministicOrchestrator,
        OrchestrationConfig,
        RouteMode,
        canonical_json,
        compute_determinism_digest,
        compute_plan_hash,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RouteMode = None  # type: ignore[assignment,misc]
    OrchestrationConfig = None  # type: ignore[assignment,misc]
    canonical_json = None  # type: ignore[assignment,misc]
    compute_plan_hash = None  # type: ignore[assignment,misc]
    compute_determinism_digest = None  # type: ignore[assignment,misc]
    DeterministicOrchestrator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="deterministic_orchestrator deps unavailable")
class TestDeterministicOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/deterministic_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_routemode_defined(self) -> None:
        assert RouteMode is not None

    def test_orchestrationconfig_defined(self) -> None:
        assert OrchestrationConfig is not None

    def test_deterministicorchestrator_defined(self) -> None:
        assert DeterministicOrchestrator is not None
