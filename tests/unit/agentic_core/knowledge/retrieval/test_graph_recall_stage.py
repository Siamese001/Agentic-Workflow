"""Unit tests for Graph Recall Stage (C0.3 — GraphRAG traversal)."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.graph_recall_stage import (
    GraphRecallStage,
    GraphTraversalResult,
)
from agentic_core.knowledge.retrieval.hybrid_recall_stage import RecallResult
from agentic_core.knowledge.retrieval.retrieval_plan import RetrievalPlan


# ---------------------------------------------------------------------------
# Stub GraphRAGProvider for testing
# ---------------------------------------------------------------------------


class StubProvider:
    """Minimal stub satisfying GraphRAGProvider protocol."""

    def __init__(
        self,
        nodes: list[dict] | None = None,
        neighbors: list[dict] | None = None,
        hydrated: dict | None = None,
    ) -> None:
        self._nodes = nodes or []
        self._neighbors = neighbors or []
        self._hydrated = hydrated or {}

    def get_nodes_for_file(self, file_path: str) -> list[dict]:
        return self._nodes

    def traverse_neighbors(
        self,
        node_id: str,
        relation_types: list[str] | None = None,
        max_depth: int = 2,
        max_hops: int = 10,
    ) -> list[dict]:
        return self._neighbors

    def hydrate_edges_for_retrieval(
        self,
        chunk_id: str,
        source_path: str,
    ) -> dict:
        return self._hydrated

    def bind_edges_for_ingestion(
        self,
        doc_id: str,
        source_path: str,
        chunks: list[dict],
    ) -> dict:
        return {}

    def analyze_impact_for_change(
        self,
        file_path: str,
        max_depth: int = 3,
    ) -> dict:
        return {}

    def resolve_pulls_context(
        self,
        chunk_id: str,
        context_sources: list[str],
    ) -> list[str]:
        return []


# ---------------------------------------------------------------------------
# Tests — GraphRecallStage
# ---------------------------------------------------------------------------


class TestGraphRecallStageInit:
    def test_defaults(self) -> None:
        stage = GraphRecallStage()
        assert stage.max_depth == 2
        assert stage.max_hops == 20
        assert stage.score_decay == 0.7

    def test_invalid_decay_raises(self) -> None:
        with pytest.raises(ValueError, match="score_decay"):
            GraphRecallStage(score_decay=0.0)
        with pytest.raises(ValueError, match="score_decay"):
            GraphRecallStage(score_decay=1.5)

    def test_invalid_max_depth_raises(self) -> None:
        with pytest.raises(ValueError, match="max_depth"):
            GraphRecallStage(max_depth=0)


class TestGraphRecall:
    def test_no_provider_returns_empty(self) -> None:
        stage = GraphRecallStage()
        results = stage.recall("some/file.py")
        assert results == []

    def test_no_nodes_returns_empty(self) -> None:
        provider = StubProvider(nodes=[])
        stage = GraphRecallStage(provider=provider)
        results = stage.recall("some/file.py")
        assert results == []

    def test_traversal_produces_recall_results(self) -> None:
        provider = StubProvider(
            nodes=[{"node_id": "n1", "symbol_name": "Foo"}],
            neighbors=[
                {
                    "node_id": "n2",
                    "symbol_name": "Bar",
                    "file_path": "bar.py",
                    "content": "class Bar:",
                    "depth": 1,
                    "relation_type": "imports",
                },
                {
                    "node_id": "n3",
                    "symbol_name": "Baz",
                    "file_path": "baz.py",
                    "content": "def baz():",
                    "depth": 2,
                    "relation_type": "calls",
                },
            ],
        )
        stage = GraphRecallStage(provider=provider, score_decay=0.7)
        results = stage.recall("foo.py")

        assert len(results) == 2
        # First result should be higher score (depth 1)
        assert results[0].score > results[1].score
        assert results[0].source == "graph"
        assert results[0].metadata["graph_depth"] == 1
        assert results[1].metadata["graph_depth"] == 2

    def test_deduplication_across_seed_nodes(self) -> None:
        provider = StubProvider(
            nodes=[
                {"node_id": "n1", "symbol_name": "A"},
                {"node_id": "n2", "symbol_name": "B"},
            ],
            neighbors=[
                {"node_id": "shared", "symbol_name": "Shared", "file_path": "s.py", "depth": 1},
            ],
        )
        stage = GraphRecallStage(provider=provider)
        results = stage.recall("file.py")
        # Same neighbor from two seeds → deduplicated
        assert len(results) == 1
        assert results[0].doc_id == "shared"

    def test_plan_metadata_propagation(self) -> None:
        provider = StubProvider(
            nodes=[{"node_id": "n1"}],
            neighbors=[{"node_id": "n2", "depth": 1}],
        )
        stage = GraphRecallStage(provider=provider)
        plan = RetrievalPlan(
            query_id="q1",
            replay_key="rk_test",
            policy_hash="ph_test",
        )
        results = stage.recall("file.py", plan=plan)
        assert len(results) == 1
        assert results[0].metadata["replay_key"] == "rk_test"
        assert results[0].metadata["policy_hash"] == "ph_test"

    def test_score_decay(self) -> None:
        provider = StubProvider(
            nodes=[{"node_id": "n1"}],
            neighbors=[
                {"node_id": "d1", "depth": 1},
                {"node_id": "d2", "depth": 2},
                {"node_id": "d3", "depth": 3},
            ],
        )
        stage = GraphRecallStage(provider=provider, score_decay=0.5)
        results = stage.recall("file.py")
        assert results[0].score == pytest.approx(1.0)  # depth 1
        assert results[1].score == pytest.approx(0.5)  # depth 2
        assert results[2].score == pytest.approx(0.25)  # depth 3


class TestGraphHop:
    def test_no_provider_returns_empty(self) -> None:
        stage = GraphRecallStage()
        results = stage.graph_hop("c1", "file.py")
        assert results == []

    def test_hop_from_pulls_context(self) -> None:
        provider = StubProvider(
            hydrated={
                "pulls_context": ["SymbolA", "SymbolB"],
                "reads_from": ["SymbolC"],
            },
        )
        stage = GraphRecallStage(provider=provider)
        results = stage.graph_hop("c1", "file.py")
        assert len(results) == 3
        assert all(r.source == "graph_hop" for r in results)
        assert results[0].metadata["hop_origin_chunk"] == "c1"

    def test_hop_deduplicates_symbols(self) -> None:
        provider = StubProvider(
            hydrated={
                "pulls_context": ["Sym"],
                "reads_from": ["Sym"],  # duplicate
            },
        )
        stage = GraphRecallStage(provider=provider)
        results = stage.graph_hop("c1", "file.py")
        assert len(results) == 1

    def test_hop_with_plan_metadata(self) -> None:
        provider = StubProvider(
            hydrated={"pulls_context": ["X"]},
        )
        stage = GraphRecallStage(provider=provider)
        plan = RetrievalPlan(query_id="q1", replay_key="rk_h", policy_hash="ph_h")
        results = stage.graph_hop("c1", "file.py", plan=plan)
        assert results[0].metadata["replay_key"] == "rk_h"
        assert results[0].metadata["policy_hash"] == "ph_h"

    def test_hop_empty_hydrated(self) -> None:
        provider = StubProvider(hydrated={})
        stage = GraphRecallStage(provider=provider)
        results = stage.graph_hop("c1", "file.py")
        assert results == []


class TestGraphTraversalResult:
    def test_defaults(self) -> None:
        r = GraphTraversalResult(node_id="n1", symbol_name="Foo", file_path="f.py")
        assert r.score == 1.0
        assert r.depth == 1
        assert r.relation_type == ""
        assert r.metadata == {}


class TestGraphRecallStageProviderErrors:
    def test_get_nodes_raises_returns_empty(self) -> None:
        class FailProvider(StubProvider):
            def get_nodes_for_file(self, file_path: str) -> list[dict]:
                raise OSError("db locked")

        stage = GraphRecallStage(provider=FailProvider())
        results = stage.recall("file.py")
        assert results == []

    def test_traverse_raises_returns_partial(self) -> None:
        class PartialProvider(StubProvider):
            def __init__(self) -> None:
                super().__init__(
                    nodes=[{"node_id": "n1"}, {"node_id": "n2"}],
                )
                self._call_count = 0

            def traverse_neighbors(  # type: ignore[override]
                self,
                node_id: str,
                relation_types: list[str] | None = None,
                max_depth: int = 2,
                max_hops: int = 10,
            ) -> list[dict]:
                self._call_count += 1
                if self._call_count == 1:
                    raise ValueError("timeout")
                return [{"node_id": "n3", "depth": 1}]

        stage = GraphRecallStage(provider=PartialProvider())  # type: ignore[arg-type]
        results = stage.recall("file.py")
        assert len(results) == 1  # second seed succeeded

    def test_hydrate_raises_returns_empty(self) -> None:
        class FailHydrate(StubProvider):
            def hydrate_edges_for_retrieval(self, chunk_id: str, source_path: str) -> dict:
                raise OSError("connection lost")

        stage = GraphRecallStage(provider=FailHydrate())
        results = stage.graph_hop("c1", "file.py")
        assert results == []
