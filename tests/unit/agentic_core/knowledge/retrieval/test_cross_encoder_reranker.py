"""Unit tests for CrossEncoderReranker + BgeRerankerAdapter (Wave B / ADR-046).

These tests do not load torch or real CrossEncoder weights. The adapter is
either mocked directly or injected through the public constructor so the full
two-stage chain can be verified on CPU-only runners in <1s.

Coverage:
    * BgeRerankerAdapter: lazy model load via singleton, score() normalizes
      numpy/torch/list outputs, input validation, singleton reset.
    * CrossEncoderReranker: two-stage chain preserves heuristic component
      scores while replacing rerank_score, falls back gracefully on
      adapter failure, honors enable flag, bypasses cross-encoder on empty
      stage1, respects pre_filter_top_k cap, stable ordering by
      cross-encoder score.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Make repo root importable for standalone runs.
_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.knowledge.retrieval import bge_reranker_adapter as bga_module
from agentic_core.knowledge.retrieval.bge_reranker_adapter import (
    BgeRerankerAdapter,
    CrossEncoderUnavailable,
    reset_for_testing,
)
from agentic_core.knowledge.retrieval.cross_encoder_reranker import CrossEncoderReranker
from agentic_core.knowledge.retrieval.senior_librarian_reranker import (
    RerankResult,
    SeniorLibrarianReranker,
)


@pytest.fixture(autouse=True)
def _reset_bga_singleton():
    reset_for_testing()
    yield
    reset_for_testing()


# ---------------------------------------------------------------------------
# Candidate fixtures
# ---------------------------------------------------------------------------


@dataclass
class _Candidate:
    """Minimal duck-type of a recall candidate (score / content / metadata)."""

    doc_id: str
    score: float
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _make_candidates(n: int = 5) -> list[_Candidate]:
    """Build n candidates with varied content length + authority signals so
    the heuristic reranker produces meaningfully different scores.

    Candidate i (0-indexed) has content of length (i+1)*120 chars containing
    the word 'python' - enough to let the heuristic's length-based coverage
    score differentiate them."""
    return [
        _Candidate(
            doc_id=f"doc_{i}",
            score=0.5 + i * 0.05,
            content=("python tutorial data " * (i + 1) * 6),
            metadata={"is_official": i % 2 == 0},
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# BgeRerankerAdapter
# ---------------------------------------------------------------------------


def test_adapter_rejects_empty_query():
    adapter = BgeRerankerAdapter()
    with pytest.raises(ValueError, match="query must be a non-empty"):
        adapter.score("   ", ["some text"])


def test_adapter_rejects_empty_candidates():
    adapter = BgeRerankerAdapter()
    with pytest.raises(ValueError, match="candidate_texts must be non-empty"):
        adapter.score("query", [])


def test_adapter_scores_pairs_via_singleton_predict():
    """Happy path: model.predict returns a list; adapter normalizes to
    plain floats and preserves order."""
    fake_model = MagicMock()
    fake_model.predict.return_value = [0.9, 0.3, 0.7]

    bga_module._MODEL = fake_model
    adapter = BgeRerankerAdapter(batch_size=8)
    scores = adapter.score("what is python", ["text a", "text b", "text c"])

    assert scores == [0.9, 0.3, 0.7]
    # Verify the adapter built (query, text) pairs in order.
    call_kwargs = fake_model.predict.call_args
    pairs = call_kwargs.args[0]
    assert pairs == [
        ["what is python", "text a"],
        ["what is python", "text b"],
        ["what is python", "text c"],
    ]
    assert call_kwargs.kwargs["batch_size"] == 8


def test_adapter_normalizes_numpy_output_to_floats():
    """Some CrossEncoder versions return a numpy ndarray; adapter must
    convert to Python floats so downstream JSON / Pydantic never chokes."""
    np = pytest.importorskip("numpy")
    fake_model = MagicMock()
    fake_model.predict.return_value = np.array([0.42, 0.11], dtype=np.float32)

    bga_module._MODEL = fake_model
    adapter = BgeRerankerAdapter()
    scores = adapter.score("q", ["a", "b"])

    assert all(isinstance(s, float) for s in scores)
    assert scores[0] == pytest.approx(0.42, rel=1e-5)
    assert scores[1] == pytest.approx(0.11, rel=1e-5)


def test_adapter_raises_unavailable_when_sentence_transformers_missing(monkeypatch):
    """First ``score`` call must raise CrossEncoderUnavailable when
    sentence-transformers can't be imported. Emulated by making the
    import fail inside the lazy loader."""
    reset_for_testing()
    monkeypatch.setattr(bga_module, "BGE_RERANKER_MODEL", "cross-encoder/test-model")
    # Force the lazy import inside _load_model to fail.
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def _blocked_import(name, *args, **kwargs):
        if name == "sentence_transformers":
            raise ImportError("simulated missing dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _blocked_import)

    adapter = BgeRerankerAdapter()
    with pytest.raises(CrossEncoderUnavailable, match="sentence-transformers required"):
        adapter.score("q", ["a"])


def test_adapter_disabled_without_explicit_reranker_model(monkeypatch):
    reset_for_testing()
    monkeypatch.setattr(bga_module, "BGE_RERANKER_MODEL", "")
    adapter = BgeRerankerAdapter()
    with pytest.raises(CrossEncoderUnavailable, match="BGE reranker disabled"):
        adapter.score("q", ["a"])


def test_reset_for_testing_clears_singleton():
    bga_module._MODEL = MagicMock()
    reset_for_testing()
    assert bga_module._MODEL is None


# ---------------------------------------------------------------------------
# CrossEncoderReranker - two-stage chain
# ---------------------------------------------------------------------------


def _patch_heuristic_prune_threshold() -> SeniorLibrarianReranker:
    """Heuristic reranker with a permissive threshold so tests see all
    candidates flow through to stage 2. The default 0.5 threshold is fine
    for production but aggressively prunes the synthetic fixtures here."""
    return SeniorLibrarianReranker(prune_threshold=0.0)


def test_two_stage_replaces_rerank_score_with_cross_encoder_score():
    """Happy path: cross-encoder score overrides heuristic score, results
    sort by the new score, and the original component scores are preserved
    in the RerankResult for downstream diagnostics.

    Drives the fake adapter by TEXT CONTENT rather than positional index so
    the heuristic's internal reordering doesn't invalidate the expectation:
    whatever stage-1 order is, the candidate whose content contains
    "doc_0_winner" gets the top score and MUST come out first."""
    candidates = _make_candidates(5)
    # Mark doc_0 specially so the adapter can recognize it regardless of stage1 order.
    candidates[0] = _Candidate(
        doc_id="doc_0",
        score=0.5,
        content="python tutorial data doc_0_winner " * 20,
        metadata={"is_official": True},
    )

    fake_adapter = MagicMock()

    def _score_by_content(_query, texts):
        return [0.95 if "doc_0_winner" in t else 0.20 for t in texts]

    fake_adapter.score.side_effect = _score_by_content

    reranker = CrossEncoderReranker(
        heuristic=_patch_heuristic_prune_threshold(),
        cross_encoder_adapter=fake_adapter,
        pre_filter_top_k=5,
    )
    out = reranker.rerank("python tutorial", candidates, top_k=3)

    assert len(out) == 3
    # Winner is doc_0 because the adapter gave its content score 0.95.
    assert out[0].doc_id == "doc_0"
    assert out[0].rerank_score == pytest.approx(0.95)
    # Component scores (relevance / coverage / authority) survive from stage 1.
    assert 0 <= out[0].relevance_score <= 1
    assert 0 <= out[0].coverage_score <= 1
    # Metadata carries the cross-encoder score for downstream observability.
    assert out[0].metadata["cross_encoder_score"] == pytest.approx(0.95)


def test_pre_filter_limits_candidates_forwarded_to_cross_encoder():
    """pre_filter_top_k caps the input to stage 2 - runtime scales with this
    value so the cap must be honored regardless of recall size."""
    candidates = _make_candidates(20)
    fake_adapter = MagicMock()
    fake_adapter.score.side_effect = lambda q, texts: [0.5] * len(texts)

    reranker = CrossEncoderReranker(
        heuristic=_patch_heuristic_prune_threshold(),
        cross_encoder_adapter=fake_adapter,
        pre_filter_top_k=5,
    )
    reranker.rerank("python", candidates, top_k=10)

    # Adapter must have been called with exactly 5 texts (the pre_filter cap).
    call = fake_adapter.score.call_args
    texts_arg = call.args[1]
    assert len(texts_arg) == 5


def test_enable_cross_encoder_false_returns_heuristic_only():
    """Master switch: when disabled, the adapter MUST NOT be touched and the
    heuristic top-K is returned verbatim."""
    candidates = _make_candidates(5)
    fake_adapter = MagicMock()

    reranker = CrossEncoderReranker(
        heuristic=_patch_heuristic_prune_threshold(),
        cross_encoder_adapter=fake_adapter,
        enable_cross_encoder=False,
    )
    out = reranker.rerank("python", candidates, top_k=3)

    assert len(out) == 3
    fake_adapter.score.assert_not_called()


def test_falls_back_to_heuristic_when_adapter_raises_unavailable():
    """Adapter raising CrossEncoderUnavailable during score() is caught and
    the caller gets heuristic results. Never crashes retrieval."""
    candidates = _make_candidates(5)
    fake_adapter = MagicMock()
    fake_adapter.score.side_effect = RuntimeError("CUDA OOM (simulated)")

    reranker = CrossEncoderReranker(
        heuristic=_patch_heuristic_prune_threshold(),
        cross_encoder_adapter=fake_adapter,
    )
    out = reranker.rerank("python", candidates, top_k=3)

    # Heuristic-only: no cross_encoder_score in metadata.
    assert len(out) == 3
    for r in out:
        assert "cross_encoder_score" not in r.metadata


def test_falls_back_when_adapter_returns_wrong_length():
    """Length-mismatch safety: defensive check against adapter bugs. If the
    count of scores doesn't match candidates, heuristic wins."""
    candidates = _make_candidates(5)
    fake_adapter = MagicMock()
    fake_adapter.score.return_value = [0.5, 0.4]  # only 2 for 5 candidates

    reranker = CrossEncoderReranker(
        heuristic=_patch_heuristic_prune_threshold(),
        cross_encoder_adapter=fake_adapter,
        pre_filter_top_k=5,
    )
    out = reranker.rerank("python", candidates, top_k=3)

    # No cross_encoder_score means heuristic path was taken.
    for r in out:
        assert "cross_encoder_score" not in r.metadata


def test_empty_heuristic_output_returns_empty_without_cross_encoding():
    """If stage 1 produces nothing (e.g. prune threshold killed everything),
    stage 2 is skipped entirely - no adapter call."""
    fake_adapter = MagicMock()
    # Use DEFAULT prune_threshold=0.5 so short candidates get pruned to []
    reranker = CrossEncoderReranker(
        heuristic=SeniorLibrarianReranker(prune_threshold=0.99),
        cross_encoder_adapter=fake_adapter,
    )
    out = reranker.rerank("query", _make_candidates(3), top_k=5)

    assert out == []
    fake_adapter.score.assert_not_called()


def test_lazy_adapter_load_on_first_call_when_not_injected():
    """When no adapter is provided to the constructor, it lazy-loads on the
    first rerank call via BgeRerankerAdapter. We simulate a successful
    lazy-load by patching the import path."""
    candidates = _make_candidates(3)

    fake_default_adapter = MagicMock()
    fake_default_adapter.score.return_value = [0.9, 0.5, 0.1]

    with patch(
        "agentic_core.knowledge.retrieval.bge_reranker_adapter.BgeRerankerAdapter",
        return_value=fake_default_adapter,
    ):
        reranker = CrossEncoderReranker(
            heuristic=_patch_heuristic_prune_threshold(),
            cross_encoder_adapter=None,  # force lazy-load
        )
        out = reranker.rerank("q", candidates, top_k=3)

    assert len(out) == 3
    # Top result got the highest cross-encoder score.
    assert out[0].rerank_score == pytest.approx(0.9)


def test_lazy_load_unavailable_falls_back_gracefully():
    """Lazy load raises CrossEncoderUnavailable -> heuristic-only path."""
    candidates = _make_candidates(3)

    with patch(
        "agentic_core.knowledge.retrieval.bge_reranker_adapter.BgeRerankerAdapter",
        side_effect=CrossEncoderUnavailable("sim missing dep"),
    ):
        reranker = CrossEncoderReranker(
            heuristic=_patch_heuristic_prune_threshold(),
            cross_encoder_adapter=None,
        )
        out = reranker.rerank("q", candidates, top_k=3)

    assert len(out) == 3
    for r in out:
        assert "cross_encoder_score" not in r.metadata


def test_drop_in_compatible_with_senior_librarian_signature():
    """Regression guard: CrossEncoderReranker.rerank(query, candidates, top_k)
    must match SeniorLibrarianReranker.rerank so the two are drop-in
    interchangeable in wiring code."""
    heuristic_sig = SeniorLibrarianReranker.rerank.__code__.co_varnames[:4]
    ce_sig = CrossEncoderReranker.rerank.__code__.co_varnames[:4]
    assert heuristic_sig == ce_sig

    # And return types are identical (list[RerankResult]).
    reranker = CrossEncoderReranker(
        heuristic=_patch_heuristic_prune_threshold(),
        enable_cross_encoder=False,
    )
    out = reranker.rerank("q", _make_candidates(2), top_k=2)
    assert all(isinstance(r, RerankResult) for r in out)
