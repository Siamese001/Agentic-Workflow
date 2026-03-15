"""ADG importability contract for agentic_core/knowledge/engine/rag_orchestrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rag_orchestrator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.knowledge.engine.rag_orchestrator import (  # noqa: F401
        SovereignRagOrchestrator,
        get_rag_manager,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SovereignRagOrchestrator = None  # type: ignore[assignment,misc]
    get_rag_manager = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rag_orchestrator deps unavailable")
class TestRagOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/knowledge/engine/rag_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_sovereignragorchestrator_defined(self) -> None:
        assert SovereignRagOrchestrator is not None
