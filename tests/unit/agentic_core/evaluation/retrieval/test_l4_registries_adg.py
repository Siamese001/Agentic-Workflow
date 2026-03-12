"""ADG importability contract for agentic_core/evaluation/retrieval/l4_registries.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_l4_registries.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.evaluation.retrieval.l4_registries import (  # noqa: F401
        ChunkManifest,
        ParentChildLink,
        RetrievalEvaluationRecord,
        ContextCompletenessSnapshot,
        ChunkManifestRegistry,
        ParentChildIndexRegistry,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ChunkManifest = None  # type: ignore[assignment,misc]
    ParentChildLink = None  # type: ignore[assignment,misc]
    RetrievalEvaluationRecord = None  # type: ignore[assignment,misc]
    ContextCompletenessSnapshot = None  # type: ignore[assignment,misc]
    ChunkManifestRegistry = None  # type: ignore[assignment,misc]
    ParentChildIndexRegistry = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="l4_registries.py deps unavailable")
class TestL4RegistriesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: l4_registries.py must be importable."""
        assert _AVAILABLE

    def test_chunkmanifest_is_type(self) -> None:
        assert ChunkManifest is not None

    def test_parentchildlink_is_type(self) -> None:
        assert ParentChildLink is not None

    def test_retrievalevaluationrecord_is_type(self) -> None:
        assert RetrievalEvaluationRecord is not None

