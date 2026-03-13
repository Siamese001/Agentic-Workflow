"""SemanticMemoryRegistry — Central registry for all ADG embedding use-cases.

Provides a single access point for all six semantic memory embedders:
  1. IncidentBundleEmbedder     — composite execution incident retrieval
  2. MutationDiffEmbedder       — UWG diff nearest-neighbour search
  3. HealerOutcomeEmbedder      — healer playbook retrieval
  4. PathDPreferenceEmbedder    — HITL preference precedent retrieval
  5. GraphNeighborhoodEmbedder  — ADG architectural motif search
  6. PolicyGuardrailEmbedder    — guardrail drift and calibration

All embedders are lazily instantiated singletons scoped to the registry.
The registry is itself a singleton, protected by a module-level lock.

Usage:
    registry = SemanticMemoryRegistry.get()
    registry.incidents.ingest(bundle)
    registry.mutations.pre_commit_check(candidate)
    registry.healers.retrieve_for_failure("ImportError: missing module x")
    registry.preferences.retrieve_for_proposal(plan_text)
    registry.graph.retrieve_by_description("risky mutation broker")
    registry.guardrails.retrieve_for_policy_hash(policy_hash)

Export for seed-pack ingestion:
    all_records = registry.export_all_corpus_records()

Design constraints:
- Thread-safe singleton via module-level lock.
- Each embedder has its own independent max_buffer.
- No wall-clock reads.
- Kill-switch compliant: retrieval paths fall through to [] when disabled.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from system_learning.config.semantic_memory_config import (
    DEFAULT_EMBEDDER_BUFFER_SIZE,
    GRAPH_NEIGHBORHOOD_BUFFER_SIZE,
)
from system_learning.engines.embedding_corpus_extraction import CorpusRecord
from system_learning.engines.graph_neighborhood_embedder import GraphNeighborhoodEmbedder
from system_learning.engines.healer_outcome_embedder import HealerOutcomeEmbedder
from system_learning.engines.incident_bundle_embedder import IncidentBundleEmbedder
from system_learning.engines.mutation_diff_embedder import MutationDiffEmbedder
from system_learning.engines.path_d_preference_embedder import PathDPreferenceEmbedder
from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

logger = logging.getLogger(__name__)

_REGISTRY_LOCK = threading.Lock()
_REGISTRY_INSTANCE: SemanticMemoryRegistry | None = None


class SemanticMemoryRegistry:
    """Central registry providing access to all six ADG semantic memory embedders.

    All embedders are independent singletons; the registry coordinates their
    lifecycle and provides a unified export surface for seed-pack ingestion.
    """

    def __init__(
        self,
        *,
        incident_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        mutation_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        healer_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        preference_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        graph_max_buffer: int = GRAPH_NEIGHBORHOOD_BUFFER_SIZE,
        guardrail_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
    ) -> None:
        self.incidents = IncidentBundleEmbedder(max_buffer=incident_max_buffer)
        self.mutations = MutationDiffEmbedder(max_buffer=mutation_max_buffer)
        self.healers = HealerOutcomeEmbedder(max_buffer=healer_max_buffer)
        self.preferences = PathDPreferenceEmbedder(max_buffer=preference_max_buffer)
        self.graph = GraphNeighborhoodEmbedder(max_buffer=graph_max_buffer)
        self.guardrails = PolicyGuardrailEmbedder(max_buffer=guardrail_max_buffer)

    @classmethod
    def get(cls, **kwargs: Any) -> SemanticMemoryRegistry:
        """Get or create the singleton registry instance.

        Args:
            **kwargs: Passed to __init__ only on first construction.

        Returns:
            The singleton SemanticMemoryRegistry instance.
        """
        global _REGISTRY_INSTANCE
        with _REGISTRY_LOCK:
            if _REGISTRY_INSTANCE is None:
                _REGISTRY_INSTANCE = cls(**kwargs)
                logger.info("SemanticMemoryRegistry: singleton created")
            return _REGISTRY_INSTANCE

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset singleton — test use only."""
        global _REGISTRY_INSTANCE
        with _REGISTRY_LOCK:
            _REGISTRY_INSTANCE = None

    def export_all_corpus_records(self) -> dict[str, list[CorpusRecord]]:
        """Export all buffered corpus records keyed by namespace.

        Returns a deterministically sorted snapshot from each embedder,
        grouped by namespace for seed-pack ingestion.

        Returns:
            Dict mapping namespace string to sorted list of CorpusRecords.
        """
        return {
            "incident_bundles": self.incidents.export_corpus_records(),
            "mutation_diffs": self.mutations.export_corpus_records(),
            "healer_outcomes": self.healers.export_corpus_records(),
            "path_d_preferences": self.preferences.export_corpus_records(),
            "graph_neighborhoods": self.graph.export_corpus_records(),
            "policy_guardrail_cases": self.guardrails.export_corpus_records(),
        }

    def total_buffer_size(self) -> dict[str, int]:
        """Return current buffer sizes for all embedders.

        Returns:
            Dict mapping namespace to buffer count.
        """
        return {
            "incident_bundles": self.incidents.buffer_size(),
            "mutation_diffs": self.mutations.buffer_size(),
            "healer_outcomes": self.healers.buffer_size(),
            "path_d_preferences": self.preferences.buffer_size(),
            "graph_neighborhoods": self.graph.buffer_size(),
            "policy_guardrail_cases": self.guardrails.buffer_size(),
        }


__all__ = ["SemanticMemoryRegistry"]
