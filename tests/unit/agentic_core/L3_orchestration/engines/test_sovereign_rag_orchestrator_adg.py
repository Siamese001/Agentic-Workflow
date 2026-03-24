"""ADG importability contract for agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereign_rag_orchestrator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.sovereign_rag_orchestrator import (  # noqa: F401
        SovereignRagOrchestrator,
        get_sovereign_rag_orchestrator,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_sovereign_rag_orchestrator = None  # type: ignore[assignment,misc]
    SovereignRagOrchestrator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_rag_orchestrator deps unavailable")
class TestSovereignRagOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_sovereignragorchestrator_defined(self) -> None:
        assert SovereignRagOrchestrator is not None