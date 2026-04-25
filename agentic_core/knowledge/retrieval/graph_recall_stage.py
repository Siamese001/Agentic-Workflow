"""Graph Recall Stage — C0.3 graph-traversal retrieval path.

Bridges the existing ``GraphRAGADGIntegration`` (L3) into the C0 retrieval
pipeline.  When a ``RetrievalPlan`` specifies ``retrieval_mode="graph"``,
this stage performs ADG-backed graph traversal instead of (or in addition
to) dense/sparse recall.

Design:
  - ``GraphRecallStage`` accepts an injectable ``GraphRAGProvider`` protocol.
  - Results are normalized to ``RecallResult`` so downstream C0.4 rerank /
    C0.5 evidence contract stages work unchanged.
  - Replay key / policy hash propagation follows the same contract as
    ``HybridRecallStage``.
  - Graceful degradation: if no provider is injected, returns empty list
    with a log warning (no crash).

Architecture reference:
  - C0 Context Engine §C0.3 Graph
  - 00C_index_materialization_runtime_handoff.md §Graph Hydrate
  - adg_integration.py §GraphRAGADGIntegration
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from agentic_core.knowledge.retrieval.hybrid_recall_stage import RecallResult

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GraphRAGProvider protocol (injectable backend)
# ---------------------------------------------------------------------------


@runtime_checkable
class GraphRAGProvider(Protocol):
    """Minimal interface for an injectable graph-RAG backend.

    The existing ``GraphRAGADGIntegration`` satisfies this protocol.
    """

    def hydrate_edges_for_retrieval(
        self,
        chunk_id: str,
        source_path: str,
    ) -> dict[str, Any]: ...

    def bind_edges_for_ingestion(
        self,
        doc_id: str,
        source_path: str,
        chunks: list[dict[str, Any]],
    ) -> dict[str, Any]: ...

    def analyze_impact_for_change(
        self,
        file_path: str,
        max_depth: int = 3,
    ) -> dict[str, Any]: ...

    def traverse_neighbors(
        self,
        node_id: str,
        relation_types: list[str] | None = None,
        max_depth: int = 2,
        max_hops: int = 10,
    ) -> list[dict[str, Any]]: ...

    def get_nodes_for_file(
        self,
        file_path: str,
    ) -> list[dict[str, Any]]: ...

    def resolve_pulls_context(
        self,
        chunk_id: str,
        context_sources: list[str],
    ) -> list[str]: ...


# ---------------------------------------------------------------------------
# GraphTraversalResult — raw traversal output before normalization
# ---------------------------------------------------------------------------


@dataclass
class GraphTraversalResult:
    """Raw result from a graph traversal before normalization to RecallResult.

    Attributes
    ----------
    node_id : str
        ADG node identifier.
    symbol_name : str
        Human-readable symbol name.
    file_path : str
        Source file path.
    content : str
        Resolved content (or summary if content unavailable).
    score : float
        Relevance score (1.0 for direct neighbor, decaying with depth).
    depth : int
        Traversal depth from the seed node.
    relation_type : str
        Edge type traversed (imports, calls, reads_from, etc.).
    metadata : dict
        Additional graph-specific metadata.
    """

    node_id: str
    symbol_name: str
    file_path: str
    content: str = ""
    score: float = 1.0
    depth: int = 1
    relation_type: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# GraphRecallStage
# ---------------------------------------------------------------------------


class GraphRecallStage:
    """C0.3 graph-traversal retrieval stage.

    When the ``RetrievalPlan`` specifies ``retrieval_mode="graph"``, this
    stage performs ADG-backed graph traversal to find structurally related
    chunks.  Results are normalized to ``RecallResult`` for seamless
    integration with downstream C0.4/C0.5 stages.

    Args:
        provider: Injectable graph-RAG backend implementing
            ``GraphRAGProvider``.  ``None`` → safe degradation (empty
            results with log warning).
        max_depth: Maximum traversal depth from seed nodes.
        max_hops: Maximum number of neighbor hops per traversal.
        score_decay: Multiplicative score decay per depth level.
    """

    def __init__(
        self,
        provider: GraphRAGProvider | None = None,
        max_depth: int = 2,
        max_hops: int = 20,
        score_decay: float = 0.7,
    ) -> None:
        if score_decay <= 0.0 or score_decay > 1.0:
            raise ValueError(f"score_decay must be in (0, 1], got {score_decay}")
        if max_depth < 1:
            raise ValueError(f"max_depth must be >= 1, got {max_depth}")
        self._provider = provider
        self.max_depth = max_depth
        self.max_hops = max_hops
        self.score_decay = score_decay

    def recall(
        self,
        seed_file_path: str,
        plan: Any | None = None,
        relation_types: list[str] | None = None,
    ) -> list[RecallResult]:
        """Execute graph-based recall from a seed file.

        Args:
            seed_file_path: Source file to start traversal from.
            plan: ``RetrievalPlan`` from L0.  replay_key / policy_hash are
                propagated to every result.  ``None`` → live mode.
            relation_types: Edge types to traverse.  ``None`` → all types.

        Returns:
            List of ``RecallResult`` from graph traversal, sorted by score.
        """
        plan_id = plan.plan_id if plan is not None else "no_plan"
        replay_key = (plan.replay_key or "") if plan is not None else ""
        policy_hash = plan.policy_hash if plan is not None else ""

        if self._provider is None:
            log.warning(
                "GraphRecallStage.recall: no provider injected; returning empty results [plan=%s]",
                plan_id,
            )
            return []

        # Get seed nodes from the file
        try:
            seed_nodes = self._provider.get_nodes_for_file(seed_file_path)
        except (OSError, ValueError) as exc:
            log.debug("get_nodes_for_file(%s) failed: %s", seed_file_path, exc)
            return []

        if not seed_nodes:
            log.debug("No ADG nodes found for %s", seed_file_path)
            return []

        # Traverse from each seed node
        all_traversal: list[GraphTraversalResult] = []
        seen_node_ids: set[str] = set()

        for node in seed_nodes:
            node_id = node.get("node_id", "") or node.get("id", "")
            if not node_id:
                continue

            try:
                neighbors = self._provider.traverse_neighbors(
                    node_id,
                    relation_types=relation_types,
                    max_depth=self.max_depth,
                    max_hops=self.max_hops,
                )
            except (OSError, ValueError) as exc:
                log.debug("traverse_neighbors(%s) failed: %s", node_id, exc)
                continue

            for neighbor in neighbors:
                nid = neighbor.get("node_id", "") or neighbor.get("id", "")
                if nid in seen_node_ids:
                    continue
                seen_node_ids.add(nid)

                depth = neighbor.get("depth", 1)
                score = self.score_decay ** (depth - 1)

                all_traversal.append(
                    GraphTraversalResult(
                        node_id=nid,
                        symbol_name=neighbor.get("symbol_name", "") or neighbor.get("name", ""),
                        file_path=neighbor.get("file_path", ""),
                        content=neighbor.get("content", ""),
                        score=score,
                        depth=depth,
                        relation_type=neighbor.get("relation_type", ""),
                        metadata=neighbor.get("metadata", {}),
                    )
                )

        # Sort by score descending
        all_traversal.sort(key=lambda t: t.score, reverse=True)

        # Normalize to RecallResult
        results: list[RecallResult] = []
        for t in all_traversal:
            result = RecallResult(
                doc_id=t.node_id,
                score=t.score,
                source="graph",
                content=t.content or f"[graph:{t.symbol_name}] {t.file_path}",
                metadata={
                    "replay_key": replay_key,
                    "policy_hash": policy_hash,
                    "plan_id": plan_id,
                    "graph_depth": t.depth,
                    "graph_relation": t.relation_type,
                    "graph_symbol": t.symbol_name,
                    "graph_file": t.file_path,
                    **t.metadata,
                },
            )
            results.append(result)

        log.debug(
            "Graph recall [plan=%s]: seed=%s, traversed=%d",
            plan_id,
            seed_file_path,
            len(results),
        )
        return results

    def graph_hop(
        self,
        chunk_id: str,
        source_path: str,
        plan: Any | None = None,
    ) -> list[RecallResult]:
        """Execute a single graph hop (C0.6 GRAPH_HOP refinement tactic).

        Used when the evidence contract builder suggests a GRAPH_HOP to
        recover from empty or weak evidence.  Performs one bounded relation
        hop from the given chunk.

        Args:
            chunk_id: Chunk to hop from.
            source_path: Source file of the chunk.
            plan: ``RetrievalPlan`` for metadata propagation.

        Returns:
            ``RecallResult`` list from the single hop.
        """
        plan_id = plan.plan_id if plan is not None else "no_plan"
        replay_key = (plan.replay_key or "") if plan is not None else ""
        policy_hash = plan.policy_hash if plan is not None else ""

        if self._provider is None:
            log.warning("GraphRecallStage.graph_hop: no provider; returning empty")
            return []

        try:
            hydrated = self._provider.hydrate_edges_for_retrieval(
                chunk_id=chunk_id,
                source_path=source_path,
            )
        except (OSError, ValueError) as exc:
            log.debug("hydrate_edges_for_retrieval(%s) failed: %s", chunk_id, exc)
            return []

        # Extract pulls_context as hop results
        pulls_context = hydrated.get("pulls_context", [])
        reads_from = hydrated.get("reads_from", [])

        results: list[RecallResult] = []
        seen: set[str] = set()

        for symbol in pulls_context + reads_from:
            if symbol in seen:
                continue
            seen.add(symbol)
            results.append(
                RecallResult(
                    doc_id=f"hop:{chunk_id}:{symbol}",
                    score=0.5,  # hop results get a moderate score
                    source="graph_hop",
                    content=f"[graph_hop:{symbol}] from {source_path}",
                    metadata={
                        "replay_key": replay_key,
                        "policy_hash": policy_hash,
                        "plan_id": plan_id,
                        "hop_origin_chunk": chunk_id,
                        "hop_symbol": symbol,
                    },
                )
            )

        return results
