"""Smoke tests for batch embedding service exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestBatchEmbeddingServiceAdg:
    """Smoke tests for batch embedding service exports."""

    def test_create_batch_embedding_service(self) -> None:
        """Import create_batch_embedding_service export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "create_batch_embedding_service")
        assert callable(func)

    def test_shutdown(self) -> None:
        """Import shutdown export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "shutdown")
        assert callable(func)

    def test_BatchEmbeddingService_init(self) -> None:
        """Import BatchEmbeddingService class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "BatchEmbeddingService")
        assert klass is not None

    def test_BatchEmbeddingService_shutdown(self) -> None:
        """Validate BatchEmbeddingService.shutdown method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "BatchEmbeddingService")
        assert hasattr(klass, "shutdown")
