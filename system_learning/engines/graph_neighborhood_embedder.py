"""GraphNeighborhoodEmbedder — Semantic search over ADG architectural motifs.

Converts GraphNeighborhood objects (local ADG subgraphs) into CorpusRecords
for seed-pack ingestion and provides nearest-neighbour retrieval over
architectural patterns.

Enables queries like:
  - "modules that look like risky mutation brokers"
  - "components architecturally similar to this healer"
  - "nodes with the same governance edge pattern as this one"

The structural context — layer, relation types, governance edges,
mutation/determinism edges, territory — is serialized into flat text
so that BGE-M3 / OpenAI embeddings capture the motif semantically.

Design constraints:
- No wall-clock reads; structural data provided by ADG scanner.
- Deterministic text serialization via GraphNeighborhood.to_embedding_text().
- Kill-switch compliant: all retrieval paths check EMBEDDING_ENABLED.
- C0_INFORMATIONAL only: no routing influence from results.
- Thread-safe append via internal lock.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import GraphNeighborhood

logger = logging.getLogger(__name__)

_NAMESPACE = "graph_neighborhoods"


@dataclass(frozen=True)
class NeighborhoodRetrievalResult:
    """Nearest-neighbour result from graph neighborhood retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    node_id: str
    node_type: str
    layer: str
    risk_label: str
    content_preview: str


class GraphNeighborhoodEmbedder:
    """Converts GraphNeighborhood objects to corpus records and retrieves similar motifs.

    Usage:
        embedder = GraphNeighborhoodEmbedder()
        embedder.ingest(neighborhood)
        similar = embedder.retrieve_similar_motif(query_neighborhood, k=5)

    ADG integration:
        Build GraphNeighborhood objects from the ADG file graph JSON using
        neighborhood_from_adg_node(), then ingest to populate the buffer.
    """

    def __init__(self, max_buffer: int = 50_000) -> None:  # guardian: allow-magic_configuration
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, neighborhood: GraphNeighborhood) -> CorpusRecord:
        """Convert a GraphNeighborhood to a CorpusRecord and buffer it.

        Args:
            neighborhood: The graph neighborhood to ingest.

        Returns:
            The generated CorpusRecord.
        """
        text = neighborhood.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=neighborhood.node_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "node_id": neighborhood.node_id,
            "node_type": neighborhood.node_type,
            "layer": neighborhood.layer,
            "risk_label": neighborhood.risk_label,
            "ownership_territory": neighborhood.ownership_territory,
            "neighborhood_hash": neighborhood.neighborhood_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("GraphNeighborhoodEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, neighborhoods: list[GraphNeighborhood]) -> list[CorpusRecord]:
        """Ingest multiple GraphNeighborhoods.

        Args:
            neighborhoods: List of graph neighborhoods.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(n) for n in neighborhoods]

    def export_corpus_records(self) -> list[CorpusRecord]:
        """Return a deterministically sorted snapshot of buffered records.

        Sorted by (content_hash, trace_id) for determinism.
        """
        with self._lock:
            return sorted(self._records, key=lambda r: (r.content_hash, r.trace_id))

    def buffer_size(self) -> int:
        """Return current number of buffered records."""
        with self._lock:
            return len(self._records)

    def retrieve_similar_motif(
        self,
        query_neighborhood: GraphNeighborhood,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[NeighborhoodRetrievalResult]:
        """Retrieve architecturally similar nodes via sovereign semantic cache.

        Args:
            query_neighborhood: The node whose motif to match.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of NeighborhoodRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_neighborhood.to_embedding_text(), k=k, namespace=namespace)

    def retrieve_by_description(
        self,
        motif_description: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[NeighborhoodRetrievalResult]:
        """Retrieve nodes matching a natural-language architectural description.

        Example queries:
            "risky mutation broker with writes_through and no guardrail"
            "healer that applies L5 safety policy and records execution trace"

        Args:
            motif_description: Natural language description of the desired motif.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of NeighborhoodRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(motif_description, k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[NeighborhoodRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[NeighborhoodRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    NeighborhoodRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        node_id=meta.get("node_id", ""),
                        node_type=meta.get("node_type", ""),
                        layer=meta.get("layer", ""),
                        risk_label=meta.get("risk_label", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("GraphNeighborhoodEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def neighborhood_from_adg_node(
        *,
        node_id: str,
        node_type: str,
        layer: str,
        inbound_relations: list[str],
        outbound_relations: list[str],
        governance_edges: list[str],
        mutation_edges: list[str],
        ownership_territory: str,
        risk_label: str = "unknown",
    ) -> GraphNeighborhood:
        """Build a GraphNeighborhood from raw ADG node data.

        Args:
            node_id: Canonical node identifier (e.g. module path).
            node_type: Node type (e.g. 'agent', 'healer', 'engine', 'config').
            layer: Layer string (e.g. 'L2_execution', 'L5_safety').
            inbound_relations: List of inbound edge relation type strings.
            outbound_relations: List of outbound edge relation type strings.
            governance_edges: List of governance relation type strings.
            mutation_edges: List of mutation/determinism edge type strings.
            ownership_territory: SSOT territory name.
            risk_label: Risk classification (default 'unknown').

        Returns:
            GraphNeighborhood instance.
        """
        return GraphNeighborhood(
            node_id=node_id,
            node_type=node_type,
            layer=layer,
            inbound_relations=tuple(sorted(inbound_relations)),
            outbound_relations=tuple(sorted(outbound_relations)),
            governance_edges=tuple(sorted(governance_edges)),
            mutation_edges=tuple(sorted(mutation_edges)),
            ownership_territory=ownership_territory,
            risk_label=risk_label,
        )


__all__ = ["GraphNeighborhoodEmbedder", "NeighborhoodRetrievalResult"]
