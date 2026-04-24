"""Edge-case hardening tests for ``tools/eval/ragbench_runner.py``.

Companion to ``test_ragbench_runner.py``. Focuses on:

  - Robustness of helpers against degenerate inputs (empty docs, empty
    ranked lists, all-stopword queries)
  - CLI surface (``--top-k`` validation, missing fixture, empty fixture,
    output-path nested-dir creation)
  - ``_chunk_passage`` strategy dispatch contract
  - Run-time invariants (every approach returns a row; metrics finite)
  - Idempotence: running twice on the same input gives identical results
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.eval.ragbench_runner import (
    APPROACHES,
    _BM25Index,
    _bow_embed,
    _chunk_passage,
    _cosine,
    _hit_at_k,
    _mrr_at_k,
    _Retrieved,
    _rerank_scores,
    _rrf_fuse,
    load_fixture,
    main,
    render_markdown,
    run_ablation,
)


# ---------------------------------------------------------------------------
# Helper degenerate-input robustness
# ---------------------------------------------------------------------------


class TestHelperDegenerate:
    def test_bow_embed_empty_string_yields_zero_vector(self):
        v = _bow_embed([""])[0]
        assert all(x == 0.0 for x in v)

    def test_bow_embed_only_punctuation_yields_zero_vector(self):
        v = _bow_embed(["!!! ?? ..."])[0]
        assert all(x == 0.0 for x in v)

    def test_cosine_zero_vector_returns_zero(self):
        z = [0.0] * 10
        v = _bow_embed(["alpha"])[0]
        assert _cosine(z, v) == 0.0

    def test_bm25_empty_corpus_does_not_crash(self):
        idx = _BM25Index.build([])
        # No docs → score returns empty list.
        assert idx.score("anything") == []

    def test_bm25_query_with_no_matches_returns_zeros(self):
        idx = _BM25Index.build(["the quick brown fox"])
        scores = idx.score("zzzzz qqqqq")
        assert scores == [0.0]

    def test_bm25_unknown_token_is_silently_ignored(self):
        idx = _BM25Index.build(["alpha beta gamma", "delta epsilon zeta"])
        # Mixed query: one known token + one unknown → ranking still works.
        scores = idx.score("alpha unknownwordxyz")
        assert scores[0] > scores[1]

    def test_rrf_fuse_empty_lists(self):
        assert _rrf_fuse([]) == []
        assert _rrf_fuse([[]]) == []
        assert _rrf_fuse([[], []]) == []

    def test_rrf_fuse_single_list_preserves_order(self):
        fused = _rrf_fuse([[2, 0, 1]])
        ordered_ids = [doc_id for doc_id, _ in fused]
        assert ordered_ids == [2, 0, 1]

    def test_rerank_scores_empty_doc_list_returns_empty(self):
        assert _rerank_scores("query", []) == []

    def test_rerank_scores_finite_values(self):
        scores = _rerank_scores("test query", ["doc one", "doc two", "doc three"])
        assert all(isinstance(s, float) for s in scores)
        assert all(s == s for s in scores)  # NaN check (NaN != NaN)


# ---------------------------------------------------------------------------
# Hit/MRR boundary cases
# ---------------------------------------------------------------------------


class TestMetricsBoundary:
    def test_hit_at_k_with_k_zero_never_hits(self):
        hits = [_Retrieved(doc_id="a", chunk_id="a_0", score=1.0)]
        assert _hit_at_k(hits, {"a"}, k=0) == 0.0

    def test_mrr_at_k_with_no_hits(self):
        hits = [_Retrieved(doc_id="x", chunk_id="x_0", score=0.5)]
        assert _mrr_at_k(hits, {"y"}, k=5) == 0.0

    def test_mrr_at_k_truncates_at_k(self):
        # gold at rank 4, k=3 → no hit
        hits = [
            _Retrieved(doc_id=f"d{i}", chunk_id=f"d{i}_0", score=0.0)
            for i in range(5)
        ]
        assert _mrr_at_k(hits, {"d3"}, k=3) == 0.0
        assert _mrr_at_k(hits, {"d3"}, k=4) == pytest.approx(1 / 4)


# ---------------------------------------------------------------------------
# _chunk_passage contract
# ---------------------------------------------------------------------------


class TestChunkPassage:
    def test_unknown_strategy_raises(self):
        with pytest.raises(ValueError, match="unknown chunk strategy"):
            _chunk_passage("p1", "some text", "no_such_strategy")

    def test_empty_text_returns_empty_list_for_fixed(self):
        assert _chunk_passage("p1", "", "fixed") == []
        assert _chunk_passage("p1", "   \n\n   ", "fixed") == []

    def test_empty_text_returns_empty_list_for_semantic(self):
        assert _chunk_passage("p1", "", "embedding_semantic") == []

    def test_fixed_strategy_overlap_present(self):
        text = "x" * 600
        chunks = _chunk_passage("p1", text, "fixed")
        # With 200-char chunks and 50-char overlap, step = 150.
        # Ranges should overlap: [0,200) [150,350) [300,500) [450,600)
        starts = [c.start_pos for c in chunks]
        assert starts == sorted(starts)
        # Adjacent chunks overlap.
        for prev, nxt in zip(chunks, chunks[1:], strict=False):
            assert nxt.start_pos < prev.end_pos

    def test_semantic_chunks_carry_parent_id(self):
        chunks = _chunk_passage(
            "P-XYZ",
            "Sentence one. Sentence two. Sentence three.",
            "embedding_semantic",
        )
        assert chunks
        for c in chunks:
            assert c.metadata["parent_id"] == "P-XYZ"


# ---------------------------------------------------------------------------
# Run-time invariants
# ---------------------------------------------------------------------------


class TestRunInvariants:
    def _tiny_fixture(self) -> list:
        from tools.eval.ragbench_runner import EvalQuery

        return [
            EvalQuery(
                query_id="q1",
                query="how to reset password",
                relevant_passage_ids=["p1"],
                passages=[
                    {"id": "p1", "text": "To reset password, use the recovery flow. " * 3},
                    {"id": "p2", "text": "Unrelated info about networking ports. " * 3},
                ],
            ),
        ]

    def test_every_approach_produces_a_row(self):
        rows = run_ablation(self._tiny_fixture(), top_k=3)
        assert len(rows) == len(APPROACHES)
        for r in rows:
            assert r["n_queries"] == 1

    def test_metrics_are_finite(self):
        rows = run_ablation(self._tiny_fixture(), top_k=3)
        for r in rows:
            assert r["hit_at_3"] == r["hit_at_3"]  # not NaN
            assert r["mrr_at_3"] == r["mrr_at_3"]
            assert 0.0 <= r["hit_at_3"] <= 1.0
            assert 0.0 <= r["mrr_at_3"] <= 1.0

    def test_idempotent_under_repeat(self):
        rows1 = run_ablation(self._tiny_fixture(), top_k=3)
        rows2 = run_ablation(self._tiny_fixture(), top_k=3)
        assert rows1 == rows2

    def test_top_k_propagates_to_metric_keys(self):
        rows = run_ablation(self._tiny_fixture(), top_k=7)
        for r in rows:
            assert "hit_at_7" in r
            assert "mrr_at_7" in r


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


class TestCLI:
    def _write_tiny_fixture(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "query_id": "q1",
                        "query": "alpha beta gamma",
                        "relevant_passage_ids": ["p1"],
                        "passages": [
                            {"id": "p1", "text": "Alpha beta gamma delta. " * 5},
                        ],
                    }
                )
            )
            f.write("\n")

    def test_top_k_zero_rejected(self, tmp_path: Path):
        fixture = tmp_path / "f.jsonl"
        self._write_tiny_fixture(fixture)
        rc = main(["--fixture", str(fixture), "--top-k", "0"])
        assert rc == 2

    def test_top_k_negative_rejected(self, tmp_path: Path):
        fixture = tmp_path / "f.jsonl"
        self._write_tiny_fixture(fixture)
        rc = main(["--fixture", str(fixture), "--top-k", "-3"])
        assert rc == 2

    def test_empty_fixture_rejected(self, tmp_path: Path):
        fixture = tmp_path / "empty.jsonl"
        fixture.write_text("", encoding="utf-8")
        rc = main(["--fixture", str(fixture)])
        assert rc == 2

    def test_output_path_creates_nested_dirs(self, tmp_path: Path):
        fixture = tmp_path / "f.jsonl"
        self._write_tiny_fixture(fixture)
        out = tmp_path / "deeply" / "nested" / "report.md"
        rc = main(["--fixture", str(fixture), "--output", str(out)])
        assert rc == 0
        assert out.exists()
        assert out.read_text(encoding="utf-8").startswith("# RAGBench Ablation")

    def test_help_does_not_crash(self):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        # argparse exits 0 on --help.
        assert exc.value.code == 0


# ---------------------------------------------------------------------------
# Render robustness
# ---------------------------------------------------------------------------


class TestRender:
    def test_render_handles_zero_rows_without_index_error(self):
        md = render_markdown([], fixture_path=Path("x.jsonl"), top_k=5)
        # No rows means `rows[0]` would be illegal; we already guard via
        # `rows[0]['n_queries'] if rows else 0`. Just assert no crash and
        # the heading is present.
        assert "RAGBench Ablation" in md
        assert "Queries: 0" in md

    def test_render_uses_dynamic_approach_count(self):
        rows = [
            {"label": "L1", "hit_at_5": 0.5, "mrr_at_5": 0.4, "n_queries": 1},
            {"label": "L2", "hit_at_5": 0.7, "mrr_at_5": 0.6, "n_queries": 1},
        ]
        md = render_markdown(rows, fixture_path=Path("x.jsonl"), top_k=5)
        assert "2-Approach" in md
        assert "L1" in md and "L2" in md
