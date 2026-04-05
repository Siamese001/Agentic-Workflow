"""
L3 Orchestration — Retrieval Bridge Module

Provides ContextRetrievalOrchestrator for wiring L3 context assembly
and GraphRAG routing to the retrieval pipeline.
"""

from __future__ import annotations

from typing import Any

# L3 Orchestration components for retrieval
from agentic_core.L3_orchestration.reasoning.engines.orchestrator_engine import Orchestrator
from agentic_core.L3_orchestration.reasoning.engines.sovereign_rag_orchestrator import SovereignRagOrchestrator

__all__ = [
    "ContextRetrievalOrchestrator",
]


class ContextRetrievalOrchestrator:
    """Bridge L3 orchestration to retrieval pipeline.

    This class is imported by apps_* to establish ADG edges
    from apps to L3_orchestration retrieval components.

    Minimal implementation: re-exports L3 retrieval functionality.
    """

    # Re-export core L3 classes for retrieval wiring
    Orchestrator = Orchestrator
    SovereignRagOrchestrator = SovereignRagOrchestrator

    @staticmethod
    def get_orchestrator() -> type[Orchestrator]:
        """Return the Orchestrator class."""
        return Orchestrator

    @staticmethod
    def get_rag_orchestrator() -> type[SovereignRagOrchestrator]:
        """Return the SovereignRagOrchestrator class."""
        return SovereignRagOrchestrator
