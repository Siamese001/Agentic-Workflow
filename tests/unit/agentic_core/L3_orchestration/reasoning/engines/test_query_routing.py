"""Unit tests for Phase 3 query-side hardening.

Tests:
  - QueryIntentDetector.detect_topic_domain() classifies architecture / best_practice / code / general
  - QueryRouter._get_target_collection() maps domains to canonical collection names
  - QueryRouter._get_arch_prefilter() returns canonical=True filter for architecture domain
  - HybridSearchEngine._apply_authority_rerank() boosts combined_score by authority_level
  - HybridSearchEngine.search() with authority_rerank=True reorders results correctly
  - evidence_shaper.apply_authority_rerank() boosts and sorts result objects
  - evidence_shaper.doc_family_dedup() caps results per doc_family
  - query_router.py default collection_name is "code_chunks" (not "repo_code_chunks")
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[7]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
    LOW_NORMATIVE_COVERAGE,
    CitationAnchor,
    EvidenceBundle,
    apply_authority_rerank,
    collapse_group_dedup,
    doc_family_dedup,
    filter_normative_sources,
    make_citation_anchor_from_chunk,
)
from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
    HybridSearchResult,
)
from agentic_core.L3_orchestration.reasoning.engines.query_intent_detector import (
    QueryIntentDetector,
)
from agentic_core.L3_orchestration.reasoning.engines.query_router import QueryRouter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(
    chunk_id: str,
    score: float,
    authority_level: float | None = None,
    doc_family: str | None = None,
) -> HybridSearchResult:
    meta: dict[str, Any] = {}
    if authority_level is not None:
        meta["authority_level"] = authority_level
    if doc_family is not None:
        meta["doc_family"] = doc_family
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=f"Content for {chunk_id}",
        metadata=meta,
        combined_score=score,
        source="vector",
        vector_score=score,
        lexical_score=0.0,
    )


# ---------------------------------------------------------------------------
# detect_topic_domain
# ---------------------------------------------------------------------------


class TestDetectTopicDomain:
    def setup_method(self) -> None:
        self.detector = QueryIntentDetector()

    @pytest.mark.parametrize(
        "query,expected",
        [
            ("what is the architecture for the retrieval layer", "architecture"),
            ("explain the ADR for hybrid search", "architecture"),
            ("L3 layer design invariants", "architecture"),
            ("constitutional floor standards", "policy"),
            ("contract for the query router interface", "architecture"),
        ],
    )
    def test_architecture_queries(self, query: str, expected: str) -> None:
        result = self.detector.detect_topic_domain(query)
        assert result == expected, f"Query {query!r}: expected {expected!r}, got {result!r}"

    @pytest.mark.parametrize(
        "query,expected",
        [
            ("LangChain RAG agent tutorial", "best_practice"),
            ("OpenAI agents best practice pattern", "best_practice"),
            ("anthropic agent framework example", "best_practice"),
            ("how to build a RAG pipeline", "best_practice"),
        ],
    )
    def test_best_practice_queries(self, query: str, expected: str) -> None:
        result = self.detector.detect_topic_domain(query)
        assert result == expected, f"Query {query!r}: expected {expected!r}, got {result!r}"

    @pytest.mark.parametrize(
        "query,expected",
        [
            ("HybridSearchEngine class implementation", "code"),
            ("what does bge_embed_query function do", "code"),
            ("import error in module agentic_core", "code"),
            ("test_hybrid_search.py code", "code"),
        ],
    )
    def test_code_queries(self, query: str, expected: str) -> None:
        result = self.detector.detect_topic_domain(query)
        assert result == expected, f"Query {query!r}: expected {expected!r}, got {result!r}"

    def test_empty_query_returns_general(self) -> None:
        assert self.detector.detect_topic_domain("") == "general"
        assert self.detector.detect_topic_domain(None) == "general"  # type: ignore[arg-type]

    def test_returns_string(self) -> None:
        result = self.detector.detect_topic_domain("some query")
        assert isinstance(result, str)

    def test_valid_domain_values(self) -> None:
        valid = {"architecture", "best_practice", "code", "general", "policy", "tool_contracts"}
        for query in ["ADR", "LangChain", "class Foo", "random words xyz"]:
            result = self.detector.detect_topic_domain(query)
            assert result in valid, f"detect_topic_domain({query!r}) = {result!r} not in {valid}"


# ---------------------------------------------------------------------------
# QueryRouter static helpers
# ---------------------------------------------------------------------------


class TestQueryRouterHelpers:
    @pytest.mark.parametrize(
        "domain,expected_collection",
        [
            ("architecture", "arch_docs"),
            ("best_practice", "curated_agent_docs"),
            ("tool_contracts", "curated_agent_docs"),
            ("code", "code_chunks"),
            ("general", "code_chunks"),  # falls back to default
            ("unknown_domain", "code_chunks"),
        ],
    )
    def test_get_target_collection(self, domain: str, expected_collection: str) -> None:
        result = QueryRouter._get_target_collection(domain, default_collection="code_chunks")
        assert result == expected_collection, (
            f"_get_target_collection({domain!r}) = {result!r}, expected {expected_collection!r}"
        )

    def test_get_arch_prefilter_returns_canonical_filter(self) -> None:
        result = QueryRouter._get_arch_prefilter("architecture")
        assert result == {"canonical": True}

    @pytest.mark.parametrize("domain", ["best_practice", "code", "general"])
    def test_get_arch_prefilter_returns_none_for_non_arch(self, domain: str) -> None:
        result = QueryRouter._get_arch_prefilter(domain)
        assert result is None, f"_get_arch_prefilter({domain!r}) should return None, got {result!r}"

    def test_default_collection_is_code_chunks(self) -> None:
        import inspect
        from agentic_core.L3_orchestration.reasoning.engines.query_router import QueryRouter

        sig = inspect.signature(QueryRouter.route)
        default = sig.parameters["collection_name"].default
        assert default == "code_chunks", (
            f"QueryRouter.route() default collection_name = {default!r}, expected 'code_chunks'"
        )


# ---------------------------------------------------------------------------
# HybridSearchEngine._apply_authority_rerank
# ---------------------------------------------------------------------------


class TestApplyAuthorityRerank:
    def test_rerank_boosts_high_authority(self) -> None:
        results = [
            _make_result("low", 0.5, authority_level=0.0),
            _make_result("high", 0.5, authority_level=1.0),
        ]
        reranked = HybridSearchEngine._apply_authority_rerank(results, authority_bonus=0.15)
        scores = {r.chunk_id: r.combined_score for r in reranked}
        assert scores["high"] > scores["low"]

    def test_rerank_no_metadata_no_change(self) -> None:
        results = [_make_result("a", 0.7), _make_result("b", 0.5)]
        reranked = HybridSearchEngine._apply_authority_rerank(results, authority_bonus=0.15)
        # No authority_level in metadata → scores unchanged
        assert reranked[0].combined_score == pytest.approx(0.7)
        assert reranked[1].combined_score == pytest.approx(0.5)

    def test_rerank_mixed_metadata(self) -> None:
        results = [
            _make_result("no_meta", 0.8),
            _make_result("authority_half", 0.8, authority_level=0.5),
        ]
        reranked = HybridSearchEngine._apply_authority_rerank(results, authority_bonus=0.20)
        scores = {r.chunk_id: r.combined_score for r in reranked}
        assert scores["authority_half"] == pytest.approx(0.8 + 0.20 * 0.5)
        assert scores["no_meta"] == pytest.approx(0.8)

    def test_rerank_invalid_authority_level_no_crash(self) -> None:
        result = HybridSearchResult(
            chunk_id="bad",
            content="x",
            metadata={"authority_level": "not_a_float"},
            combined_score=0.5,
            source="vector",
            vector_score=0.5,
            lexical_score=0.0,
        )
        reranked = HybridSearchEngine._apply_authority_rerank([result], authority_bonus=0.15)
        assert len(reranked) == 1
        assert reranked[0].combined_score == pytest.approx(0.5)

    def test_rerank_returns_new_list(self) -> None:
        original = [_make_result("a", 0.5, authority_level=0.8)]
        reranked = HybridSearchEngine._apply_authority_rerank(original)
        assert reranked is not original

    def test_rerank_preserves_all_results(self) -> None:
        results = [_make_result(str(i), float(i) / 10, authority_level=0.5) for i in range(5)]
        reranked = HybridSearchEngine._apply_authority_rerank(results)
        assert len(reranked) == 5


# ---------------------------------------------------------------------------
# HybridSearchEngine.search() with authority_rerank
# ---------------------------------------------------------------------------


class TestHybridSearchEngineAuthorityRerank:
    def _make_engine_with_mock_chroma(self, mock_results: list[HybridSearchResult]) -> HybridSearchEngine:
        class _MockCollection:
            def query(self, **kwargs: Any) -> dict:
                ids = [[r.chunk_id for r in mock_results]]
                docs = [[r.content for r in mock_results]]
                metas = [[r.metadata for r in mock_results]]
                distances = [[1.0 - r.combined_score for r in mock_results]]
                return {"ids": ids, "documents": docs, "metadatas": metas, "distances": distances}

        class _MockChroma:
            def get_collection(self, name: str) -> _MockCollection:
                return _MockCollection()

        engine = HybridSearchEngine(chroma_client=_MockChroma(), top_k=10)
        return engine

    def test_authority_rerank_true_boosts_high_authority(self) -> None:
        mock_results = [
            _make_result("low_auth", 0.6, authority_level=0.0),
            _make_result("high_auth", 0.6, authority_level=1.0),
        ]
        engine = self._make_engine_with_mock_chroma(mock_results)
        results = engine.search("test query", collection_name="arch_docs", authority_rerank=True)
        assert len(results) >= 2
        assert results[0].chunk_id == "high_auth", (
            f"Expected 'high_auth' first after rerank, got {results[0].chunk_id!r}"
        )

    def test_authority_rerank_false_no_boost(self) -> None:
        mock_results = [
            _make_result("high_auth", 0.5, authority_level=1.0),
            _make_result("low_auth", 0.7, authority_level=0.0),
        ]
        engine = self._make_engine_with_mock_chroma(mock_results)
        results = engine.search("test query", collection_name="arch_docs", authority_rerank=False)
        assert results[0].chunk_id == "low_auth", (
            "Without authority_rerank, higher base score must rank first"
        )


# ---------------------------------------------------------------------------
# evidence_shaper.apply_authority_rerank
# ---------------------------------------------------------------------------


class TestEvidenceShaperApplyAuthorityRerank:
    def test_boosts_and_sorts(self) -> None:
        results = [
            _make_result("low", 0.5, authority_level=0.0),
            _make_result("mid", 0.5, authority_level=0.5),
            _make_result("high", 0.5, authority_level=1.0),
        ]
        reranked = apply_authority_rerank(results, authority_bonus=0.20)
        ids = [r.chunk_id for r in reranked]
        assert ids[0] == "high"
        assert ids[-1] == "low"

    def test_no_authority_metadata_stable(self) -> None:
        results = [_make_result("a", 0.9), _make_result("b", 0.7)]
        reranked = apply_authority_rerank(results)
        assert reranked[0].chunk_id == "a"
        assert reranked[1].chunk_id == "b"

    def test_empty_list(self) -> None:
        assert apply_authority_rerank([]) == []

    def test_single_result(self) -> None:
        r = _make_result("only", 0.5, authority_level=0.8)
        result = apply_authority_rerank([r])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# evidence_shaper.doc_family_dedup
# ---------------------------------------------------------------------------


class TestDocFamilyDedup:
    def test_caps_per_family(self) -> None:
        results = [_make_result(f"adr_{i}", 0.9 - i * 0.01, doc_family="adr") for i in range(6)]
        deduped = doc_family_dedup(results, max_per_family=3)
        adr_count = sum(1 for r in deduped if r.metadata.get("doc_family") == "adr")
        assert adr_count == 3

    def test_mixed_families_each_capped(self) -> None:
        results = [_make_result(f"adr_{i}", 0.9, doc_family="adr") for i in range(5)] + [
            _make_result(f"guide_{i}", 0.8, doc_family="guide") for i in range(5)
        ]
        deduped = doc_family_dedup(results, max_per_family=2)
        adr_count = sum(1 for r in deduped if r.metadata.get("doc_family") == "adr")
        guide_count = sum(1 for r in deduped if r.metadata.get("doc_family") == "guide")
        assert adr_count == 2
        assert guide_count == 2

    def test_unknown_family_not_deduplicated(self) -> None:
        results = [_make_result(f"x_{i}", 0.5) for i in range(10)]
        deduped = doc_family_dedup(results, max_per_family=2)
        assert len(deduped) == 10

    def test_preserves_order(self) -> None:
        results = [
            _make_result("first", 0.9, doc_family="adr"),
            _make_result("second", 0.8, doc_family="adr"),
            _make_result("third", 0.7, doc_family="adr"),
        ]
        deduped = doc_family_dedup(results, max_per_family=2)
        ids = [r.chunk_id for r in deduped]
        assert ids == ["first", "second"]

    def test_empty_list(self) -> None:
        assert doc_family_dedup([]) == []


# ---------------------------------------------------------------------------
# GAP-R1: HybridSearchEngine.search() with chroma_client=None (failure path)
# ---------------------------------------------------------------------------


class TestHybridSearchEngineNullChroma:
    def test_no_chroma_client_returns_empty(self) -> None:
        """search() with chroma_client=None must return [] (failure path)."""
        engine = HybridSearchEngine(chroma_client=None, top_k=5)
        results = engine.search("what is the retrieval layer?")
        assert results == []

    def test_no_chroma_client_with_embedding_returns_empty(self) -> None:
        """search() with pre-computed embedding but no client must still return []."""
        engine = HybridSearchEngine(chroma_client=None, top_k=5)
        results = engine.search("test", query_embedding=[0.1] * 10)
        assert results == []


# ---------------------------------------------------------------------------
# GAP-R2: enforce_context_budget — happy path, failure path, edge case
# ---------------------------------------------------------------------------


class TestEnforceContextBudget:
    def _engine(self) -> HybridSearchEngine:
        return HybridSearchEngine(chroma_client=None, top_k=5)

    def _results(self, n: int) -> list[HybridSearchResult]:
        return [_make_result(f"r{i}", float(n - i) / n) for i in range(n)]

    def test_budget_allows_all_returns_all(self) -> None:
        """Happy path: large budget → all results returned."""
        out = self._engine().enforce_context_budget(
            self._results(3), max_tokens=1000, avg_tokens_per_chunk=100
        )
        assert len(out) == 3

    def test_zero_max_tokens_returns_empty(self) -> None:
        """Failure path: max_tokens=0 → empty list."""
        out = self._engine().enforce_context_budget(self._results(3), max_tokens=0)
        assert out == []

    def test_budget_caps_at_allowed_count(self) -> None:
        """Edge case: max_tokens//avg_tokens_per_chunk < len(results) → truncated."""
        out = self._engine().enforce_context_budget(
            self._results(10), max_tokens=300, avg_tokens_per_chunk=100
        )
        assert len(out) == 3

    def test_zero_avg_tokens_raises_value_error(self) -> None:
        """Edge case: avg_tokens_per_chunk=0 must raise ValueError."""
        with pytest.raises(ValueError):
            self._engine().enforce_context_budget(self._results(3), max_tokens=100, avg_tokens_per_chunk=0)


# ---------------------------------------------------------------------------
# GAP-R3: EvidenceBundle.dedup_ratio() — happy path and edge case
# ---------------------------------------------------------------------------


def _make_bundle(ranked_chunks: list, shaping_stats: dict | None = None) -> EvidenceBundle:
    return EvidenceBundle(
        query="test query",
        collection="arch_docs",
        ranked_chunks=ranked_chunks,
        citation_anchors={},
        contradiction_flags=[],
        exact_match_winners=[],
        expanded_chunk_ids=[],
        shaping_stats=shaping_stats or {},
    )


class TestEvidenceBundleDedupRatio:
    def test_no_dedup_stats_returns_zero(self) -> None:
        """Happy path: no shaping_stats → input_count == after_dedup → ratio == 0.0."""
        bundle = _make_bundle(ranked_chunks=[object(), object()])
        assert bundle.dedup_ratio() == pytest.approx(0.0)

    def test_partial_dedup_returns_correct_ratio(self) -> None:
        """Edge case: explicit stats give expected ratio."""
        bundle = _make_bundle(
            ranked_chunks=[object()],
            shaping_stats={"input_count": 10, "after_dedup": 7},
        )
        assert bundle.dedup_ratio() == pytest.approx(0.3)

    def test_full_dedup_clamped_to_one(self) -> None:
        """Edge case: all chunks deduped → ratio == 1.0."""
        bundle = _make_bundle(
            ranked_chunks=[object()],
            shaping_stats={"input_count": 5, "after_dedup": 0},
        )
        assert bundle.dedup_ratio() == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# GAP-R4: CitationAnchor.__post_init__ edge cases
# ---------------------------------------------------------------------------


class TestCitationAnchorEdge:
    def _anchor(self, confidence: Any) -> CitationAnchor:
        return CitationAnchor(
            chunk_id="c1",
            collection="arch_docs",
            canonical_digest="abc123",
            file_path="docs/adr001.md",
            layer="docs",
            provenance_confidence=confidence,  # type: ignore[arg-type]
        )

    def test_invalid_string_confidence_clamps_to_zero(self) -> None:
        """Edge case: non-numeric string confidence → clamped to 0.0."""
        anchor = self._anchor("not_a_float")
        assert anchor.provenance_confidence == pytest.approx(0.0)

    def test_confidence_above_one_clamped_to_one(self) -> None:
        """Edge case: confidence > 1.0 → clamped to 1.0."""
        anchor = self._anchor(5.0)
        assert anchor.provenance_confidence == pytest.approx(1.0)

    def test_valid_confidence_preserved(self) -> None:
        """Happy path: valid confidence [0,1] stored exactly."""
        anchor = self._anchor(0.75)
        assert anchor.provenance_confidence == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# GAP-R5: QueryRouter.route() integration — happy path and tuple contract
# ---------------------------------------------------------------------------


class TestQueryRouterRoute:
    def _make_router(self) -> QueryRouter:
        class _MockEngine:
            def search(self, **kwargs: Any) -> list:
                return []

            def _ensure_adg_connection(self) -> None:
                return None

            def _apply_governance_filters(self, results: list, gf: Any) -> list:
                return results

        return QueryRouter(_MockEngine())

    def test_route_semantic_query_returns_semantic_mode(self) -> None:
        """Happy path: semantic query → mode='semantic', list result."""
        router = self._make_router()
        mode, results = router.route("what is the purpose of the retrieval layer?")
        assert mode == "semantic"
        assert isinstance(results, list)

    def test_route_returns_two_tuple(self) -> None:
        """Contract: route() always returns a (str, list) 2-tuple."""
        router = self._make_router()
        out = router.route("explain the architecture design")
        assert isinstance(out, tuple)
        assert len(out) == 2
        mode, results = out
        assert isinstance(mode, str)
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# GAP-R6: doc_family_dedup(max_per_family=0) edge case
# ---------------------------------------------------------------------------


class TestDocFamilyDedupZeroMax:
    def test_max_per_family_zero_excludes_named_families(self) -> None:
        """Edge case: max_per_family=0 → all named-family results excluded; unknown kept."""
        results = [
            _make_result("named_1", 0.9, doc_family="adr"),
            _make_result("named_2", 0.8, doc_family="adr"),
            _make_result("unknown_1", 0.7),  # no doc_family → "_unknown" bucket
        ]
        deduped = doc_family_dedup(results, max_per_family=0)
        ids = {r.chunk_id for r in deduped}
        assert "named_1" not in ids
        assert "named_2" not in ids
        assert "unknown_1" in ids


# ---------------------------------------------------------------------------
# Prompt-3: tool_contracts domain detection
# ---------------------------------------------------------------------------


class TestToolContractsDomainDetection:
    """Verify MCP/FastMCP queries are classified as 'tool_contracts' domain."""

    def setup_method(self) -> None:
        self.detector = QueryIntentDetector()

    @pytest.mark.parametrize(
        "query",
        [
            "how do I author a FastMCP server?",
            "what is the MCP tool call protocol?",
            "configure an agent tool using MCP",
            "explain MCP tool contracts for the retrieval layer",
        ],
    )
    def test_mcp_queries_return_tool_contracts(self, query: str) -> None:
        """Happy path: MCP/FastMCP queries classify as 'tool_contracts'."""
        result = self.detector.detect_topic_domain(query)
        assert result == "tool_contracts", f"Query {query!r}: expected 'tool_contracts', got {result!r}"

    def test_non_mcp_query_does_not_return_tool_contracts(self) -> None:
        """Edge case: standard best_practice query must not bleed into tool_contracts."""
        result = self.detector.detect_topic_domain("LangChain RAG agent tutorial")
        assert result != "tool_contracts"

    def test_tool_contracts_routes_to_curated(self) -> None:
        """Contract: tool_contracts domain maps to curated_agent_docs."""
        collection = QueryRouter._get_target_collection("tool_contracts", "code_chunks")
        assert collection == "curated_agent_docs"

    def test_best_practice_routes_to_curated(self) -> None:
        """Contract: best_practice domain now maps to curated_agent_docs (not ext_knowledge)."""
        collection = QueryRouter._get_target_collection("best_practice", "code_chunks")
        assert collection == "curated_agent_docs"


# ---------------------------------------------------------------------------
# Prompt-3: collapse_group_dedup
# ---------------------------------------------------------------------------


def _make_result_grouped(
    chunk_id: str, score: float, collapse_group: str | None = None
) -> HybridSearchResult:
    meta: dict[str, Any] = {}
    if collapse_group is not None:
        meta["collapse_group"] = collapse_group
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=f"Content for {chunk_id}",
        metadata=meta,
        combined_score=score,
        source="vector",
        vector_score=score,
        lexical_score=0.0,
    )


class TestCollapseGroupDedup:
    def test_caps_results_per_group(self) -> None:
        """Happy path: max_per_group=2 keeps at most 2 per collapse_group."""
        results = [
            _make_result_grouped("lg_1", 0.9, "langgraph"),
            _make_result_grouped("lg_2", 0.85, "langgraph"),
            _make_result_grouped("lg_3", 0.80, "langgraph"),  # should be dropped
            _make_result_grouped("ag_1", 0.75, "autogen"),
            _make_result_grouped("ag_2", 0.70, "autogen"),
        ]
        deduped = collapse_group_dedup(results, max_per_group=2)
        ids = [r.chunk_id for r in deduped]
        assert "lg_1" in ids
        assert "lg_2" in ids
        assert "lg_3" not in ids
        assert "ag_1" in ids
        assert "ag_2" in ids

    def test_distinct_groups_treated_independently(self) -> None:
        """Edge case: langgraph and autogen caps are independent (not shared)."""
        results = [
            _make_result_grouped("lg_1", 0.9, "langgraph"),
            _make_result_grouped("lg_2", 0.8, "langgraph"),
            _make_result_grouped("ag_1", 0.7, "autogen"),
            _make_result_grouped("ag_2", 0.6, "autogen"),
        ]
        deduped = collapse_group_dedup(results, max_per_group=2)
        assert len(deduped) == 4

    def test_ungrouped_results_always_pass(self) -> None:
        """Edge case: results with no collapse_group always pass through uncapped."""
        results = [
            _make_result_grouped("grp_1", 0.9, "langgraph"),
            _make_result_grouped("grp_2", 0.85, "langgraph"),
            _make_result_grouped("grp_3", 0.80, "langgraph"),  # capped
            _make_result_grouped("ung_1", 0.75),  # no collapse_group
            _make_result_grouped("ung_2", 0.70),  # no collapse_group
            _make_result_grouped("ung_3", 0.65),  # no collapse_group
        ]
        deduped = collapse_group_dedup(results, max_per_group=2)
        ids = {r.chunk_id for r in deduped}
        assert "grp_3" not in ids
        assert {"ung_1", "ung_2", "ung_3"} <= ids

    def test_zero_max_per_group_excludes_all_grouped(self) -> None:
        """Failure path: max_per_group=0 removes all grouped results; ungrouped remain."""
        results = [
            _make_result_grouped("grp_1", 0.9, "mcp_protocol_sdk"),
            _make_result_grouped("ung_1", 0.5),
        ]
        deduped = collapse_group_dedup(results, max_per_group=0)
        ids = {r.chunk_id for r in deduped}
        assert "grp_1" not in ids
        assert "ung_1" in ids

    def test_preserves_insertion_order(self) -> None:
        """Contract: order within kept results matches input order."""
        results = [
            _make_result_grouped("a", 0.9, "langgraph"),
            _make_result_grouped("b", 0.8, "autogen"),
            _make_result_grouped("c", 0.7, "langgraph"),
        ]
        deduped = collapse_group_dedup(results, max_per_group=2)
        ids = [r.chunk_id for r in deduped]
        assert ids.index("a") < ids.index("b")


# ---------------------------------------------------------------------------
# HybridSearchEngine.search() collapse_group_dedup_max parameter
# ---------------------------------------------------------------------------


def _make_result_for_search(
    chunk_id: str, score: float, collapse_group: str | None = None
) -> HybridSearchResult:
    meta: dict[str, Any] = {}
    if collapse_group is not None:
        meta["collapse_group"] = collapse_group
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=f"Content for {chunk_id}",
        metadata=meta,
        combined_score=score,
        source="vector",
        vector_score=score,
        lexical_score=0.0,
    )


class TestSearchCollapseGroupDedupMax:
    def _raw(self) -> list[HybridSearchResult]:
        return [
            _make_result_for_search("r0", 0.9, "g1"),
            _make_result_for_search("r1", 0.8, "g1"),
            _make_result_for_search("r2", 0.7, "g2"),
            _make_result_for_search("r3", 0.6, "g2"),
        ]

    def test_collapse_group_dedup_max_limits_per_group(self) -> None:
        """Happy path: collapse_group_dedup_max=1 keeps at most 1 result per group."""
        engine = HybridSearchEngine(chroma_client=None, top_k=4)
        with patch.object(engine, "_vector_search", return_value=self._raw()):
            out = engine.search("test", collapse_group_dedup_max=1)
        g1 = [r for r in out if r.metadata.get("collapse_group") == "g1"]
        g2 = [r for r in out if r.metadata.get("collapse_group") == "g2"]
        assert len(g1) == 1
        assert len(g2) == 1

    def test_collapse_group_dedup_max_none_no_dedup(self) -> None:
        """Default (None): no collapse dedup applied — all 4 results returned."""
        engine = HybridSearchEngine(chroma_client=None, top_k=4)
        with patch.object(engine, "_vector_search", return_value=self._raw()):
            out = engine.search("test")
        assert len(out) == 4

    def test_collapse_group_dedup_max_two_keeps_two_per_group(self) -> None:
        """Edge case: max=2 with 2-item groups keeps both; 3-item group would cap at 2."""
        raw = [
            _make_result_for_search("a0", 0.9, "grp"),
            _make_result_for_search("a1", 0.8, "grp"),
            _make_result_for_search("a2", 0.7, "grp"),
            _make_result_for_search("b0", 0.6, "other"),
        ]
        engine = HybridSearchEngine(chroma_client=None, top_k=4)
        with patch.object(engine, "_vector_search", return_value=raw):
            out = engine.search("test", collapse_group_dedup_max=2)
        grp_ids = [r.chunk_id for r in out if r.metadata.get("collapse_group") == "grp"]
        assert len(grp_ids) == 2
        assert "a2" not in grp_ids


# ---------------------------------------------------------------------------
# Helper: make a result with full provenance metadata
# ---------------------------------------------------------------------------


def _make_provenance_result(
    chunk_id: str,
    score: float,
    source_collection: str = "curated_agent_docs",
    authority_tier: str = "T3_guidance",
    normative_scope: str = "external_authority",
    invalid_for_normative_use: bool = False,
    authority_level: float = 0.9,
) -> HybridSearchResult:
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=f"Content for {chunk_id}",
        metadata={
            "source_collection": source_collection,
            "authority_tier": authority_tier,
            "normative_scope": normative_scope,
            "invalid_for_normative_use": invalid_for_normative_use,
            "authority_level": authority_level,
            "file_path": f"docs/{chunk_id}.md",
            "layer": "ext",
            "canonical_digest": f"digest_{chunk_id}",
            "source": source_collection,
        },
        combined_score=score,
        source="vector",
        vector_score=score,
        lexical_score=0.0,
    )


# ---------------------------------------------------------------------------
# Phase 3 — policy domain detection
# ---------------------------------------------------------------------------


class TestDetectPolicyDomain:
    """policy domain must be returned for constitutional/safety/guardian queries."""

    detector = QueryIntentDetector()

    def test_constitutional_hard_constraints_is_policy(self) -> None:
        domain = self.detector.detect_topic_domain("constitutional hard constraints for agent behavior")
        assert domain == "policy"

    def test_safety_trust_boundary_is_policy_not_architecture(self) -> None:
        domain = self.detector.detect_topic_domain("L5 safety trust boundary enforcement")
        assert domain == "policy"

    def test_guardian_exemption_gate_is_policy(self) -> None:
        domain = self.detector.detect_topic_domain("guardian exemption gate")
        assert domain == "policy"

    def test_safety_rule_is_policy(self) -> None:
        domain = self.detector.detect_topic_domain("what are the safety rules for agentic systems")
        assert domain == "policy"

    def test_injection_control_is_policy(self) -> None:
        domain = self.detector.detect_topic_domain("injection control mechanisms for agents")
        assert domain == "policy"

    def test_adr_still_architecture(self) -> None:
        domain = self.detector.detect_topic_domain("ADR-018 chromadb architecture decision")
        assert domain == "architecture"

    def test_policy_routes_to_curated(self) -> None:
        resolved = QueryRouter._get_target_collection("policy", "code_chunks")
        assert resolved == "curated_agent_docs"

    def test_policy_not_in_arch_prefilter(self) -> None:
        prefilter = QueryRouter._get_arch_prefilter("policy")
        assert prefilter is None

    def test_bare_except_query_is_policy(self) -> None:
        domain = self.detector.detect_topic_domain("Can I use bare except here?")
        assert domain == "policy"

    def test_subprocess_without_timeout_is_policy(self) -> None:
        domain = self.detector.detect_topic_domain("Is subprocess.run without timeout allowed?")
        assert domain == "policy"

    def test_blast_radius_query_is_best_practice(self) -> None:
        domain = self.detector.detect_topic_domain(
            "What should I use for dependency / blast-radius analysis?"
        )
        assert domain == "best_practice"


# ---------------------------------------------------------------------------
# Phase 3 — filter_normative_sources gate
# ---------------------------------------------------------------------------


class TestFilterNormativeSources:
    """filter_normative_sources must reject arch_docs and fail closed on missing metadata."""

    def test_arch_docs_chunk_rejected(self) -> None:
        r = _make_provenance_result(
            "arch_1",
            0.9,
            source_collection="arch_docs",
            authority_tier="T4_implementation_evidence",
            normative_scope="evidence_only",
            invalid_for_normative_use=True,
        )
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert r in rejected

    def test_curated_web_chunk_accepted(self) -> None:
        r = _make_provenance_result("cur_1", 0.9)
        accepted, rejected = filter_normative_sources([r])
        assert r in accepted
        assert rejected == []

    def test_curated_local_adr_accepted(self) -> None:
        r = _make_provenance_result(
            "adr_1",
            0.85,
            source_collection="curated_agent_docs",
            authority_tier="T4_repo_canonical",
            normative_scope="repo_internal",
            invalid_for_normative_use=False,
        )
        accepted, rejected = filter_normative_sources([r])
        assert r in accepted
        assert rejected == []

    def test_missing_source_collection_fails_closed(self) -> None:
        r = HybridSearchResult(
            chunk_id="no_prov",
            content="no provenance",
            metadata={},
            combined_score=0.9,
            source="vector",
            vector_score=0.9,
            lexical_score=0.0,
        )
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert r in rejected

    def test_empty_input_returns_empty_both(self) -> None:
        accepted, rejected = filter_normative_sources([])
        assert accepted == []
        assert rejected == []

    def test_mixed_batch_splits_correctly(self) -> None:
        curated = _make_provenance_result("cur_2", 0.9)
        arch = _make_provenance_result(
            "arch_2",
            0.95,
            source_collection="arch_docs",
            authority_tier="T4_implementation_evidence",
            normative_scope="evidence_only",
            invalid_for_normative_use=True,
        )
        accepted, rejected = filter_normative_sources([curated, arch])
        assert curated in accepted
        assert arch in rejected
        assert arch not in accepted

    def test_curated_with_invalid_true_is_rejected(self) -> None:
        """Curated chunk explicitly marked invalid_for_normative_use=True must be rejected.

        Validates the ``invalid is False`` identity guard from Phase 3: even a
        chunk with an otherwise allowed collection and tier is rejected when the
        flag is True, not merely falsy.
        """
        r = _make_provenance_result(
            "cur_invalid",
            0.9,
            source_collection="curated_agent_docs",
            authority_tier="T3_guidance",
            invalid_for_normative_use=True,
        )
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert r in rejected

    def test_low_normative_coverage_constant_exported(self) -> None:
        assert LOW_NORMATIVE_COVERAGE == "LOW_NORMATIVE_COVERAGE"


# ---------------------------------------------------------------------------
# Phase 3 — tier-aware authority rerank
# ---------------------------------------------------------------------------


class TestApplyAuthorityRerankTierAware:
    """tier_aware=True must give arch_docs zero bonus and discount lower tiers."""

    def test_t4_implementation_evidence_gets_zero_bonus(self) -> None:
        r = _make_provenance_result(
            "arch_3",
            0.5,
            source_collection="arch_docs",
            authority_tier="T4_implementation_evidence",
            authority_level=1.0,
        )
        out = apply_authority_rerank([r], authority_bonus=0.15, tier_aware=True)
        assert out[0].combined_score == pytest.approx(0.5)

    def test_t4_repo_canonical_gets_reduced_bonus(self) -> None:
        r = _make_provenance_result(
            "adr_3",
            0.5,
            authority_tier="T4_repo_canonical",
            authority_level=1.0,
        )
        out = apply_authority_rerank([r], authority_bonus=0.15, tier_aware=True)
        assert out[0].combined_score == pytest.approx(0.5 + 0.15 * 1.0 * 0.50)

    def test_t2_standard_gets_full_bonus(self) -> None:
        r = _make_provenance_result(
            "std_1",
            0.5,
            authority_tier="T2_standard",
            authority_level=1.0,
        )
        out = apply_authority_rerank([r], authority_bonus=0.15, tier_aware=True)
        assert out[0].combined_score == pytest.approx(0.5 + 0.15)

    def test_t3_guidance_gets_discounted_bonus(self) -> None:
        r = _make_provenance_result(
            "guide_1",
            0.5,
            authority_tier="T3_guidance",
            authority_level=1.0,
        )
        out = apply_authority_rerank([r], authority_bonus=0.15, tier_aware=True)
        assert out[0].combined_score == pytest.approx(0.5 + 0.15 * 0.85)

    def test_unknown_tier_gets_zero_bonus_when_tier_aware(self) -> None:
        r = _make_provenance_result(
            "unk_1",
            0.5,
            authority_tier="",
            authority_level=1.0,
        )
        out = apply_authority_rerank([r], authority_bonus=0.15, tier_aware=True)
        assert out[0].combined_score == pytest.approx(0.5)

    def test_tier_aware_false_preserves_original_behaviour(self) -> None:
        r = _make_provenance_result(
            "arch_4",
            0.5,
            authority_tier="T4_implementation_evidence",
            authority_level=1.0,
        )
        out = apply_authority_rerank([r], authority_bonus=0.15, tier_aware=False)
        assert out[0].combined_score == pytest.approx(0.5 + 0.15)

    def test_arch_docs_loses_to_curated_when_tier_aware(self) -> None:
        arch = _make_provenance_result(
            "arch_5",
            0.85,
            authority_tier="T4_implementation_evidence",
            authority_level=1.0,
        )
        curated = _make_provenance_result(
            "cur_5",
            0.80,
            authority_tier="T2_standard",
            authority_level=1.0,
        )
        out = apply_authority_rerank([arch, curated], authority_bonus=0.15, tier_aware=True)
        assert out[0].chunk_id == "cur_5"


# ---------------------------------------------------------------------------
# Phase 3 — make_citation_anchor_from_chunk provenance
# ---------------------------------------------------------------------------


class TestMakeCitationAnchorFromChunk:
    """CitationAnchor.collection must be chunk-derived, not routing-derived."""

    def test_collection_from_source_collection_metadata(self) -> None:
        r = _make_provenance_result("c1", 0.9, source_collection="curated_agent_docs")
        anchor = make_citation_anchor_from_chunk(r)
        assert anchor.collection == "curated_agent_docs"

    def test_arch_docs_collection_preserved(self) -> None:
        r = _make_provenance_result(
            "a1",
            0.9,
            source_collection="arch_docs",
            authority_tier="T4_implementation_evidence",
            invalid_for_normative_use=True,
        )
        anchor = make_citation_anchor_from_chunk(r)
        assert anchor.collection == "arch_docs"

    def test_missing_source_collection_falls_back_to_source_field(self) -> None:
        r = HybridSearchResult(
            chunk_id="fb_1",
            content="fallback",
            metadata={"source": "curated_agent_docs"},
            combined_score=0.8,
            source="vector",
            vector_score=0.8,
            lexical_score=0.0,
        )
        anchor = make_citation_anchor_from_chunk(r)
        assert anchor.collection == "curated_agent_docs"
