"""Unit tests for agentic_core.L0_routing.c0_retrieval.candidate_pool.

W2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 C0 retrieval contract.
``candidate_pool`` (fan_in=13, L0_routing) defines the pre-verification evidence
structs: RetrievalScores, HydrationManifest, CandidateChunk, CandidateEvidencePool.
Hard invariant C0.I3: every retrieved item must preserve retrieval-lane provenance.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.c0_retrieval.candidate_pool import (
    CandidateChunk,
    CandidateEvidencePool,
    HydrationManifest,
    RetrievalScores,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import RetrievalLane, SourceClass


def _manifest(**overrides: object) -> HydrationManifest:
    base: dict[str, object] = {"source_id": "src-1"}
    base.update(overrides)
    return HydrationManifest(**base)  # type: ignore[arg-type]


def _chunk(**overrides: object) -> CandidateChunk:
    base: dict[str, object] = {
        "chunk_id": "c1",
        "source_class": SourceClass.DOCS,
        "text": "evidence text",
        "manifest": _manifest(),
        "found_by_lanes": (RetrievalLane.DENSE,),
    }
    base.update(overrides)
    return CandidateChunk(**base)  # type: ignore[arg-type]


class TestRetrievalScores:
    def test_defaults(self) -> None:
        s = RetrievalScores()
        assert s.raw_score == 0.0
        assert s.normalized_score == 0.0
        assert s.rank == 0

    @pytest.mark.parametrize("score", [-0.1, 1.1, 2.0])
    def test_normalized_score_out_of_range_raises(self, score: float) -> None:
        with pytest.raises(ValueError, match="normalized_score must be in"):
            RetrievalScores(normalized_score=score)

    def test_negative_rank_raises(self) -> None:
        with pytest.raises(ValueError, match="rank must be >= 0"):
            RetrievalScores(rank=-1)

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            RetrievalScores().rank = 5  # type: ignore[misc]


class TestHydrationManifest:
    def test_defaults(self) -> None:
        m = _manifest()
        assert m.data_class == "internal"
        assert m.retrieval_lane is RetrievalLane.DENSE
        assert m.line_range == (0, 0)
        assert m.extras == {}

    def test_blank_source_id_raises(self) -> None:
        with pytest.raises(ValueError, match="source_id required"):
            HydrationManifest(source_id="   ")

    def test_negative_line_range_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid line_range"):
            _manifest(line_range=(-1, 5))

    def test_inverted_line_range_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid line_range"):
            _manifest(line_range=(10, 3))

    def test_valid_line_range_accepted(self) -> None:
        assert _manifest(line_range=(3, 10)).line_range == (3, 10)


class TestCandidateChunk:
    def test_construct_valid(self) -> None:
        c = _chunk()
        assert c.chunk_id == "c1"
        assert c.source_class is SourceClass.DOCS
        assert isinstance(c.scores, RetrievalScores)

    def test_blank_chunk_id_raises(self) -> None:
        with pytest.raises(ValueError, match="chunk_id required"):
            _chunk(chunk_id="  ")

    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValueError, match="text must not be empty"):
            _chunk(text="")

    def test_missing_lane_provenance_raises(self) -> None:
        with pytest.raises(ValueError, match="lane provenance"):
            _chunk(found_by_lanes=())

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _chunk().text = "new"  # type: ignore[misc]


class TestCandidateEvidencePool:
    def test_construct_valid(self) -> None:
        pool = CandidateEvidencePool(plan_id="p1", candidates=(_chunk(),))
        assert pool.plan_id == "p1"
        assert pool.fetch_latency_ms == 0
        assert pool.fetch_errors == ()

    def test_blank_plan_id_raises(self) -> None:
        with pytest.raises(ValueError, match="plan_id required"):
            CandidateEvidencePool(plan_id=" ", candidates=())

    def test_negative_latency_raises(self) -> None:
        with pytest.raises(ValueError, match="fetch_latency_ms must be >= 0"):
            CandidateEvidencePool(plan_id="p", candidates=(), fetch_latency_ms=-1)

    def test_lane_not_in_lanes_used_raises(self) -> None:
        chunk = _chunk(found_by_lanes=(RetrievalLane.GRAPH_SEED,))
        with pytest.raises(ValueError, match="not in pool.lanes_used"):
            CandidateEvidencePool(
                plan_id="p",
                candidates=(chunk,),
                lanes_used=(RetrievalLane.DENSE,),
            )

    def test_lanes_used_consistent_accepted(self) -> None:
        chunk = _chunk(found_by_lanes=(RetrievalLane.DENSE,))
        pool = CandidateEvidencePool(
            plan_id="p",
            candidates=(chunk,),
            lanes_used=(RetrievalLane.DENSE, RetrievalLane.SPARSE),
        )
        assert len(pool.candidates) == 1

    def test_by_source_filters(self) -> None:
        docs = _chunk(chunk_id="d", source_class=SourceClass.DOCS)
        code = _chunk(chunk_id="k", source_class=SourceClass.CODE)
        pool = CandidateEvidencePool(plan_id="p", candidates=(docs, code))
        assert pool.by_source(SourceClass.DOCS) == (docs,)
        assert pool.by_source(SourceClass.CODE) == (code,)
        assert pool.by_source(SourceClass.LOGS) == ()

    def test_by_lane_filters(self) -> None:
        a = _chunk(chunk_id="a", found_by_lanes=(RetrievalLane.DENSE,))
        b = _chunk(chunk_id="b", found_by_lanes=(RetrievalLane.SPARSE,))
        pool = CandidateEvidencePool(plan_id="p", candidates=(a, b))
        assert pool.by_lane(RetrievalLane.DENSE) == (a,)
        assert pool.by_lane(RetrievalLane.SPARSE) == (b,)
        assert pool.by_lane(RetrievalLane.CACHE) == ()

    def test_frozen(self) -> None:
        pool = CandidateEvidencePool(plan_id="p", candidates=())
        with pytest.raises(dataclasses.FrozenInstanceError):
            pool.plan_id = "p2"  # type: ignore[misc]
