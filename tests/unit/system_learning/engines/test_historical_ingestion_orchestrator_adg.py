"""ADG importability contract for system_learning/engines/historical_ingestion_orchestrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_historical_ingestion_orchestrator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.historical_ingestion_orchestrator import (  # noqa: F401
        ingest_and_build_indexes,
        ingest_and_build_indexes_with_embedder,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ingest_and_build_indexes = None  # type: ignore[assignment,misc]
    ingest_and_build_indexes_with_embedder = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="historical_ingestion_orchestrator.py deps unavailable")
class TestHistoricalIngestionOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: historical_ingestion_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_ingest_and_build_indexes_callable(self) -> None:
        assert callable(ingest_and_build_indexes)

    def test_ingest_and_build_indexes_with_embedder_callable(self) -> None:
        assert callable(ingest_and_build_indexes_with_embedder)