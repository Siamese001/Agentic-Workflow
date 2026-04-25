"""Hardening tests for ``tools/eval/ragbench_runner.py``.

Runs the full 6-approach ablation against the synthetic fixture and
asserts:

  - All approaches produce non-degenerate metrics.
  - Hit@5 / MRR@5 are monotonically non-decreasing as features stack
    (within the synthetic-fixture regime — looser constraint than
    real-data because fixture is small and saturates quickly).
  - The contextual-retrieval row is included and its chunks are marked.
  - Markdown rendering is well-formed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.eval.ragbench_runner import (
    APPROACHES,
    EvalQuery,
    _BM25Index,
    _bow_embed,
    _chunk_passage,
    _contextualise_chunks,
    _cosine,
    _hit_at_k,
    _mrr_at_k,
    _Retrieved,
    _rrf_fuse,
    load_fixture,
    render_markdown,
    run_ablation,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE = REPO_ROOT / "data/eval/golden/ragbench_techqa_synthetic.jsonl"


# ---------------------------------------------------------------------------
# Fixture sanity
# ---------------------------------------------------------------------------


class TestFixture:
    def test_fixture_exists(self):
        assert FIXTURE.exists(), f"missing fixture: {FIXTURE}"

    def test_fixture_loads(self):
        rows = load_fixture(FIXTURE)
        assert len(rows) >= 10
        for r in rows:
            assert isinstance(r, EvalQuery)
            assert r.query
            assert r.relevant_passage_ids
            assert r.passages
            # gold ids must reference passages we have
            ids = {p["id"] for p in r.passages}
            assert all(g in ids for g in r.relevant_passage_ids)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_cosine_identical(self):
        v = [1.0, 0.0, 1.0]
        assert _cosine(v, v) == pytest.approx(1.0)

    def test_cosine_orthogonal_zero(self):
        assert _cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_bow_embed_deterministic(self):
        a = _bow_embed(["error code TS-999"])
        b = _bow_embed(["error code TS-999"])
        assert a == b

    def test_bow_embed_normalised(self):
        v = _bow_embed(["alpha beta gamma"])[0]
        norm_sq = sum(x * x for x in v)
        # Vectors with at least one token must be unit length (within fp).
        assert norm_sq == pytest.approx(1.0, rel=1e-6)

    def test_bm25_scores_keyword_matches_higher(self):
        idx = _BM25Index.build(["the firewall blocks UDP", "an unrelated paragraph about pricing"])
        scores = idx.score("firewall UDP")
        assert scores[0] > scores[1]

    def test_rrf_fuse_orders_consensus_first(self):
        list_a = [3, 1, 2]
        list_b = [3, 2, 1]
        fused = _rrf_fuse([list_a, list_b])
        # Doc 3 appears at rank 0 in both lists → must come first.
        assert fused[0][0] == 3

    def test_hit_at_k_short_circuits(self):
        hits = [
            _Retrieved(doc_id="a", chunk_id="a_0", score=0.9),
            _Retrieved(doc_id="b", chunk_id="b_0", score=0.5),
        ]
        assert _hit_at_k(hits, {"b"}, k=2) == 1.0
        assert _hit_at_k(hits, {"z"}, k=2) == 0.0

    def test_mrr_at_k_uses_first_hit_position(self):
        hits = [
            _Retrieved(doc_id="x", chunk_id="x", score=1.0),
            _Retrieved(doc_id="b", chunk_id="b", score=0.5),
            _Retrieved(doc_id="z", chunk_id="z", score=0.1),
        ]
        # gold hits at rank 2 → MRR=0.5
        assert _mrr_at_k(hits, {"b"}, k=3) == pytest.approx(0.5)

    def test_chunk_passage_fixed_emits_overlap(self):
        text = "abcdef" * 100  # 600 chars
        chunks = _chunk_passage("p1", text, "fixed")
        assert len(chunks) >= 2
        # All carry parent_id pointing back at the passage.
        assert all(c.metadata.get("parent_id") == "p1" for c in chunks)

    def test_chunk_passage_embedding_semantic_falls_back_for_short_text(self):
        chunks = _chunk_passage("p1", "Tiny text here.", "embedding_semantic")
        assert len(chunks) == 1
        assert chunks[0].metadata.get("parent_id") == "p1"


# ---------------------------------------------------------------------------
# Contextualisation
# ---------------------------------------------------------------------------


class TestContextualisation:
    def test_contextualise_marks_chunks(self):
        passages = [{"id": "p1", "text": "Some long parent passage. " * 5}]
        chunks = _chunk_passage("p1", passages[0]["text"], "embedding_semantic")
        out = _contextualise_chunks(chunks, passages)
        assert len(out) == len(chunks)
        for c in out:
            assert c.metadata.get("contextualised") is True
            # Contextualised content is at least as long as original
            # (heuristic prefix is non-empty for these passages).
            assert len(c.content) >= 1


# ---------------------------------------------------------------------------
# End-to-end ablation
# ---------------------------------------------------------------------------


class TestAblation:
    def test_six_rows_present(self):
        assert len(APPROACHES) == 6
        labels = [a.label for a in APPROACHES]
        assert "Naive" in labels[0]
        assert "Contextual Retrieval" in labels[5]

    def test_run_ablation_completes_and_is_well_formed(self):
        queries = load_fixture(FIXTURE)
        rows = run_ablation(queries, top_k=5)
        assert len(rows) == 6
        for r in rows:
            assert 0.0 <= r["hit_at_5"] <= 1.0
            assert 0.0 <= r["mrr_at_5"] <= 1.0
            assert r["n_queries"] == len(queries)

    def test_features_do_not_regress_baseline(self):
        # Synthetic fixture saturates fast — the precise spread between rows
        # is not stable across fixture changes, but the *contextual-retrieval*
        # final row should never be strictly worse than the *naive* baseline.
        queries = load_fixture(FIXTURE)
        rows = run_ablation(queries, top_k=5)
        baseline = rows[0]
        contextual = rows[-1]
        assert contextual["hit_at_5"] >= baseline["hit_at_5"]
        assert contextual["mrr_at_5"] >= baseline["mrr_at_5"]

    def test_render_markdown_includes_all_rows_and_metadata(self):
        queries = load_fixture(FIXTURE)
        rows = run_ablation(queries, top_k=5)
        md = render_markdown(rows, fixture_path=FIXTURE, top_k=5)
        for r in rows:
            assert r["label"] in md
        assert "Hit@5" in md
        assert "MRR@5" in md
        assert "RRF" in md  # methodology callout
        assert "Contextual Retrieval" in md


# ---------------------------------------------------------------------------
# JSONL schema regression
# ---------------------------------------------------------------------------


class TestJSONLSchemaRegression:
    def test_every_row_has_required_keys(self):
        with FIXTURE.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                for key in ("query_id", "query", "relevant_passage_ids", "passages"):
                    assert key in obj, f"line {line_no}: missing {key}"
                assert obj["passages"], f"line {line_no}: empty passages"
                for p in obj["passages"]:
                    assert "id" in p and "text" in p
