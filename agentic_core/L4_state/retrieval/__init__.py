"""
L2 Execution — Retrieval Bridge Module

Provides SemanticEnrichmentBridge for wiring L2 execution components
to the retrieval pipeline across all apps_* packages.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.reasoning.batch_embedding_service import BatchEmbeddingService

# L2 Execution components for retrieval wiring
from agentic_core.L2_execution.reasoning.execution_gateway import ExecutionGateway

__all__ = [
    "SemanticEnrichmentBridge",
]


class SemanticEnrichmentBridge:
    """Bridge L2 execution to retrieval pipeline.

    This class is imported by apps_* to establish ADG edges
    from apps to L2_execution retrieval components.

    Minimal implementation: re-exports L2 retrieval functionality.
    """

    # Re-export core L2 classes for retrieval wiring
    ExecutionGateway = ExecutionGateway
    BatchEmbeddingService = BatchEmbeddingService

    @staticmethod
    def get_execution_gateway() -> type[ExecutionGateway]:
        """Return the ExecutionGateway class."""
        return ExecutionGateway

    @staticmethod
    def get_embedding_service() -> type[BatchEmbeddingService]:
        """Return the BatchEmbeddingService class."""
        return BatchEmbeddingService
