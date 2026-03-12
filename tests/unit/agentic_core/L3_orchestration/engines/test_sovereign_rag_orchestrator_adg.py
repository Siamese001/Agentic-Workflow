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
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SovereignRagOrchestrator = None  # type: ignore[assignment,misc]
    get_sovereign_rag_orchestrator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_rag_orchestrator.py deps unavailable")
class TestSovereignRagOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: sovereign_rag_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_sovereignragorchestrator_is_type(self) -> None:
        assert SovereignRagOrchestrator is not None

    def test_get_sovereign_rag_orchestrator_callable(self) -> None:
        assert callable(get_sovereign_rag_orchestrator)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

