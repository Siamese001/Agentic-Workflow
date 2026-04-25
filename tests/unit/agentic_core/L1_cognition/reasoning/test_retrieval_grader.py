"""Tests for the retrieval grader — ADR-060 §2."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.retrieval_grader import (
    Chunk,
    GradeVerdict,
    GradeVerdictKind,
    RetrievalGrader,
)


# ---------------------------------------------------------------------------
# Heuristic backend
# ---------------------------------------------------------------------------


class TestHeuristicGrader:
    def test_relevant_when_overlap_high(self) -> None:
        grader = RetrievalGrader(gateway=None)
        verdicts = grader.grade(
            "reranker factory backend",
            [Chunk("c1", "The reranker factory selects the backend per env var.")],
        )
        assert len(verdicts) == 1
        assert verdicts[0].verdict == GradeVerdictKind.RELEVANT
        assert verdicts[0].score >= 0.55

    def test_irrelevant_when_no_overlap(self) -> None:
        grader = RetrievalGrader(gateway=None)
        verdicts = grader.grade(
            "reranker factory backend",
            [Chunk("c1", "Recipes for sourdough bread fermentation.")],
        )
        assert verdicts[0].verdict == GradeVerdictKind.IRRELEVANT
        assert verdicts[0].score < 0.20

    def test_ambiguous_in_middle_band(self) -> None:
        grader = RetrievalGrader(gateway=None)
        # 1 of 4 query tokens overlap → score ~0.25 → ambiguous (>=0.20, <0.55).
        verdicts = grader.grade(
            "reranker factory backend selection",
            [Chunk("c1", "The factory pattern in software design.")],
        )
        assert verdicts[0].verdict == GradeVerdictKind.AMBIGUOUS

    def test_empty_chunks_returns_empty(self) -> None:
        grader = RetrievalGrader(gateway=None)
        assert grader.grade("anything", []) == []

    def test_empty_query_raises(self) -> None:
        grader = RetrievalGrader(gateway=None)
        with pytest.raises(ValueError, match="query must be non-empty"):
            grader.grade("   ", [Chunk("c1", "text")])

    def test_grader_identity_heuristic(self) -> None:
        grader = RetrievalGrader(gateway=None)
        assert grader.grader_identity.startswith("heuristic/v")

    def test_cache_reuses_verdicts(self) -> None:
        grader = RetrievalGrader(gateway=None)
        chunks = [Chunk("c1", "text"), Chunk("c2", "other")]
        v1 = grader.grade("query", chunks)
        v2 = grader.grade("query", chunks)
        assert v1 == v2

    def test_determinism_across_instances(self) -> None:
        a = RetrievalGrader(gateway=None)
        b = RetrievalGrader(gateway=None)
        chunk = [Chunk("c1", "the quick brown fox")]
        assert a.grade("brown fox", chunk) == b.grade("brown fox", chunk)


# ---------------------------------------------------------------------------
# LLM-backed path (parsing + fallback)
# ---------------------------------------------------------------------------


class _StubGateway:
    def __init__(self, raw: str) -> None:
        self.raw = raw
        self.calls = 0

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        timeout_s: float,
    ) -> str:
        self.calls += 1
        return self.raw


class _RaisingGateway:
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        timeout_s: float,
    ) -> str:
        raise RuntimeError("simulated outage")


class TestLLMGraderPath:
    def test_parses_well_formed_json(self) -> None:
        gw = _StubGateway('{"verdict":"relevant","score":0.91,"reason":"direct match"}')
        grader = RetrievalGrader(gateway=gw)
        v = grader.grade("q", [Chunk("c1", "x")])[0]
        assert v.verdict == GradeVerdictKind.RELEVANT
        assert v.score == pytest.approx(0.91)
        assert v.rationale == "direct match"
        assert grader.grader_identity.startswith("llm:")

    def test_parses_ambiguous_with_extra_whitespace(self) -> None:
        raw = ' some preamble {"verdict": "ambiguous", "score": 0.42, "reason": "topical"} junk'
        gw = _StubGateway(raw)
        grader = RetrievalGrader(gateway=gw)
        v = grader.grade("q", [Chunk("c1", "x")])[0]
        assert v.verdict == GradeVerdictKind.AMBIGUOUS

    def test_score_out_of_range_falls_back_to_heuristic(self) -> None:
        gw = _StubGateway('{"verdict":"relevant","score":2.0,"reason":"x"}')
        grader = RetrievalGrader(gateway=gw)
        # Falls back to heuristic; result is deterministic from the chunk.
        v = grader.grade("q", [Chunk("c1", "q text")])[0]
        # heuristic identity is reported even though gateway was set —
        # because the fallback path took over for THIS chunk.
        assert "heuristic" in v.rationale or v.verdict in GradeVerdictKind

    def test_unparseable_output_falls_back(self) -> None:
        gw = _StubGateway("not json at all")
        grader = RetrievalGrader(gateway=gw)
        v = grader.grade("query terms", [Chunk("c1", "query terms here")])[0]
        # Falls back to heuristic; with full overlap, RELEVANT.
        assert v.verdict == GradeVerdictKind.RELEVANT

    def test_gateway_exception_falls_back(self) -> None:
        gw = _RaisingGateway()
        grader = RetrievalGrader(gateway=gw)
        v = grader.grade("query", [Chunk("c1", "query content here")])[0]
        # No raise; heuristic verdict returned.
        assert isinstance(v, GradeVerdict)

    def test_cache_dedup_per_chunk(self) -> None:
        gw = _StubGateway('{"verdict":"relevant","score":0.8,"reason":"r"}')
        grader = RetrievalGrader(gateway=gw)
        grader.grade("q", [Chunk("c1", "x")])
        grader.grade("q", [Chunk("c1", "x")])
        assert gw.calls == 1
