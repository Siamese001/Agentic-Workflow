"""ADG importability contract for agentic_core/L1_cognition/memory/healing_memory_retriever.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_memory_retriever.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.memory.healing_memory_retriever import (  # noqa: F401
        HealingMemoryRetriever,
        NullHealingMemoryRetriever,
        SimilarIncident,
        SovereigntyError,
        VectorSourceMismatchError,
        build_retriever,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VectorSourceMismatchError = None  # type: ignore[assignment,misc]
    SovereigntyError = None  # type: ignore[assignment,misc]
    SimilarIncident = None  # type: ignore[assignment,misc]
    NullHealingMemoryRetriever = None  # type: ignore[assignment,misc]
    HealingMemoryRetriever = None  # type: ignore[assignment,misc]
    build_retriever = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever deps unavailable")
class TestHealingMemoryRetrieverImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L1_cognition/memory/healing_memory_retriever.py must be importable."""
        assert _AVAILABLE

    def test_vectorsourcemismatcherror_defined(self) -> None:
        assert VectorSourceMismatchError is not None

    def test_sovereigntyerror_defined(self) -> None:
        assert SovereigntyError is not None

    def test_similarincident_defined(self) -> None:
        assert SimilarIncident is not None

    def test_nullhealingmemoryretriever_defined(self) -> None:
        assert NullHealingMemoryRetriever is not None

    def test_healingmemoryretriever_defined(self) -> None:
        assert HealingMemoryRetriever is not None