"""Unit tests for corpus_size_gate."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.corpus_size_gate import (
    DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS,
    CorpusSizeGateResult,
    estimate_corpus_tokens,
    should_skip_rag,
    should_skip_rag_from_texts,
)


# ---------------------------------------------------------------------------
# estimate_corpus_tokens
# ---------------------------------------------------------------------------


def test_estimate_empty_corpus_returns_zero():
    assert estimate_corpus_tokens([]) == 0
    assert estimate_corpus_tokens(["", "", None]) == 0  # type: ignore[list-item]


def test_estimate_single_chunk_uses_default_ratio():
    # 4000 chars @ 4 chars/tok = 1000 tokens
    chunk = "x" * 4000
    assert estimate_corpus_tokens([chunk]) == 1000


def test_estimate_multiple_chunks_sums_char_count():
    chunks = ["x" * 400, "x" * 800, "x" * 1600]
    # 2800 chars / 4 = 700 tokens
    assert estimate_corpus_tokens(chunks) == 700


def test_estimate_custom_ratio_for_code():
    # Code has ~3.2 chars/tok; caller can pass that
    chunks = ["x" * 320]
    assert estimate_corpus_tokens(chunks, chars_per_token=3.2) == 100


def test_estimate_rejects_non_positive_ratio():
    with pytest.raises(ValueError):
        estimate_corpus_tokens(["abc"], chars_per_token=0)
    with pytest.raises(ValueError):
        estimate_corpus_tokens(["abc"], chars_per_token=-1.0)


# ---------------------------------------------------------------------------
# should_skip_rag
# ---------------------------------------------------------------------------


def test_skip_rag_when_corpus_below_threshold():
    result = should_skip_rag(50_000)
    assert result.skip_rag is True
    assert result.estimated_tokens == 50_000
    assert result.threshold_tokens == DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS
    assert "full-context" in result.reason


def test_skip_rag_at_exact_threshold():
    # Boundary: corpus == threshold means skip (≤, not <)
    result = should_skip_rag(DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS)
    assert result.skip_rag is True


def test_keep_rag_when_corpus_above_threshold():
    result = should_skip_rag(DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS + 1)
    assert result.skip_rag is False
    assert "use RAG pipeline" in result.reason


def test_custom_threshold_overrides_default():
    result = should_skip_rag(50_000, threshold_tokens=10_000)
    assert result.skip_rag is False
    assert result.threshold_tokens == 10_000


def test_zero_token_corpus_skips_rag():
    # An empty corpus trivially fits — skip RAG (caller will decide
    # downstream whether to even call the model).
    result = should_skip_rag(0)
    assert result.skip_rag is True
    assert result.estimated_tokens == 0


def test_negative_corpus_count_raises():
    with pytest.raises(ValueError):
        should_skip_rag(-1)


# ---------------------------------------------------------------------------
# should_skip_rag_from_texts (composition)
# ---------------------------------------------------------------------------


def test_from_texts_small_corpus_skips_rag():
    chunks = ["short chunk one.", "short chunk two."]
    result = should_skip_rag_from_texts(chunks)
    assert result.skip_rag is True
    assert result.estimated_tokens < 100


def test_from_texts_large_corpus_keeps_rag():
    # 1M chars @ 4 chars/tok = 250k tokens -> way above default threshold
    huge = ["x" * 1_000_000]
    result = should_skip_rag_from_texts(huge)
    assert result.skip_rag is False
    assert result.estimated_tokens == 250_000


def test_from_texts_custom_threshold_and_ratio():
    chunks = ["x" * 1000]
    # 1000 chars @ 2 chars/tok = 500 tokens > threshold 100 -> keep RAG
    result = should_skip_rag_from_texts(chunks, threshold_tokens=100, chars_per_token=2.0)
    assert result.skip_rag is False
    assert result.estimated_tokens == 500


# ---------------------------------------------------------------------------
# Result dataclass contract
# ---------------------------------------------------------------------------


def test_result_is_frozen_dataclass():
    r = should_skip_rag(1000)
    with pytest.raises((AttributeError, TypeError)):
        r.skip_rag = False  # type: ignore[misc]


def test_result_reason_contains_numbers():
    # Reason string is used for logging — must include the numeric decision
    # drivers so operators can trace a skip/keep decision back to inputs.
    r = should_skip_rag(50_000, threshold_tokens=100_000)
    assert "50000" in r.reason
    assert "100000" in r.reason


@pytest.mark.parametrize(
    "corpus,threshold,expected",
    [
        (0, 100, True),
        (100, 100, True),
        (101, 100, False),
        (DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS - 1, None, True),
        (DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS, None, True),
        (DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS + 1, None, False),
    ],
)
def test_gate_decision_matrix(corpus, threshold, expected):
    kwargs = {} if threshold is None else {"threshold_tokens": threshold}
    assert should_skip_rag(corpus, **kwargs).skip_rag is expected
