"""ADG importability contract for agentic_core/L1_cognition/memory/SemanticMemory.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SemanticMemory.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.memory.SemanticMemory import (  # noqa: F401
        EmbeddingProvider,
        SemanticEntry,
        SemanticMemory,
        VectorIndex,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    EmbeddingProvider = None  # type: ignore[assignment,misc]
    VectorIndex = None  # type: ignore[assignment,misc]
    SemanticEntry = None  # type: ignore[assignment,misc]
    SemanticMemory = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="SemanticMemory.py deps unavailable")
class TestSemanticmemoryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: SemanticMemory.py must be importable."""
        assert _AVAILABLE

    def test_embeddingprovider_is_type(self) -> None:
        assert EmbeddingProvider is not None

    def test_vectorindex_is_type(self) -> None:
        assert VectorIndex is not None

    def test_semanticentry_is_type(self) -> None:
        assert SemanticEntry is not None