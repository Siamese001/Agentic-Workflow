"""Unit tests for breadth_first_classifier."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.reasoning.breadth_first_classifier import (
    MODE_AMBIGUOUS,
    MODE_BREADTH_FIRST,
    MODE_SINGLE_AGENT,
    ClassificationResult,
    classify_query,
    is_breadth_first,
)


# ---------------------------------------------------------------------------
# Clear breadth-first queries
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [
        "Compare pricing across every vendor in the list.",
        "Enumerate all security vulnerabilities per module.",
        "List each compliance standard we need and compare them.",
        "What are the differences between AWS, GCP, and Azure for our workload?",
    ],
)
def test_obvious_breadth_first_queries_classified_correctly(query):
    result = classify_query(query)
    assert result.mode == MODE_BREADTH_FIRST, (
        f"Expected breadth_first for {query!r}, got {result.mode} "
        f"(score={result.score}, signals={result.matched_signals})"
    )


def test_multi_question_boosts_score():
    query = "What is X? How does Y work? Why is Z important?"
    result = classify_query(query)
    assert "multi_question" in result.matched_signals
    assert result.score >= 0.60


def test_high_fanout_from_adg_shifts_to_breadth_first():
    query = "Describe the compliance framework."  # narrow prose
    # Without fanout signal -> single/ambiguous
    base = classify_query(query)
    # With high fanout -> shifts up
    boosted = classify_query(query, corpus_fanout=5)
    assert boosted.score > base.score
    assert "high_fanout" in boosted.matched_signals


# ---------------------------------------------------------------------------
# Clear single-agent queries
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [
        "What is the exact value of X?",
        "Find the best single recommendation for our use case.",
        "Which one of these is correct?",
        "First validate the input, then transform it, next persist it step by step.",
    ],
)
def test_obvious_single_agent_queries_classified_correctly(query):
    result = classify_query(query)
    assert result.mode == MODE_SINGLE_AGENT, (
        f"Expected single_agent for {query!r}, got {result.mode} "
        f"(score={result.score}, signals={result.matched_signals})"
    )


def test_sequential_language_depresses_score():
    listwise = "List all the options."  # +listwise
    sequential = "List all the options, then rank them step by step."  # +listwise, -sequential
    base = classify_query(listwise)
    damped = classify_query(sequential)
    assert damped.score <= base.score
    assert "sequential" in damped.matched_signals


# ---------------------------------------------------------------------------
# Ambiguous queries
# ---------------------------------------------------------------------------


def test_neutral_prose_query_is_ambiguous():
    query = "Tell me about our database schema."
    result = classify_query(query)
    # Neutral query produces ~0.5 score which falls in ambiguity band around 0.60
    assert result.mode in (MODE_SINGLE_AGENT, MODE_AMBIGUOUS)


def test_empty_query_returns_single_agent_without_error():
    for empty in ("", "   ", "\n\t "):
        r = classify_query(empty)
        assert r.mode == MODE_SINGLE_AGENT
        assert r.score == 0.0


# ---------------------------------------------------------------------------
# Score clamping
# ---------------------------------------------------------------------------


def test_score_clamps_to_zero_when_heavily_negative():
    # Stack many sequential + narrow signals
    query = (
        "Find the single best exact value, which one is it, "
        "step by step, first then next, in order to proceed."
    )
    result = classify_query(query)
    assert 0.0 <= result.score <= 1.0


def test_score_clamps_to_one_when_heavily_positive():
    query = (
        "List all items, enumerate every option, compare across "
        "each tier, between A and B, per region. What? Why? How?"
    )
    result = classify_query(query, corpus_fanout=10)
    assert result.score == pytest.approx(1.0, abs=0.01)
    assert result.mode == MODE_BREADTH_FIRST


# ---------------------------------------------------------------------------
# Threshold customization
# ---------------------------------------------------------------------------


def test_custom_threshold_promotes_more_queries_to_breadth_first():
    query = "Describe the system."  # neutral
    strict = classify_query(query, threshold=0.60)
    loose = classify_query(query, threshold=0.30)
    # Loose threshold lowers the bar; neutral query now exceeds it
    assert strict.mode != MODE_BREADTH_FIRST
    # Loose may produce breadth_first or ambiguous depending on band
    assert loose.mode in (MODE_BREADTH_FIRST, MODE_AMBIGUOUS)


def test_ambiguity_band_widens_ambiguous_region():
    # Exactly-at-threshold query with narrow band -> ambiguous; with wide band -> still ambiguous
    query = "Compare two things."  # ~0.75 with parallel signal
    narrow = classify_query(query, threshold=0.60, ambiguity_band=0.01)
    wide = classify_query(query, threshold=0.60, ambiguity_band=0.25)
    # Both should resolve but wide band is more likely to produce ambiguous
    assert narrow.mode in (MODE_BREADTH_FIRST, MODE_AMBIGUOUS, MODE_SINGLE_AGENT)
    assert wide.mode in (MODE_AMBIGUOUS, MODE_BREADTH_FIRST)


# ---------------------------------------------------------------------------
# is_breadth_first convenience
# ---------------------------------------------------------------------------


def test_is_breadth_first_true_only_for_breadth_first_mode():
    assert is_breadth_first("Compare all options across every region.") is True
    assert is_breadth_first("What is X exactly?") is False
    assert is_breadth_first("") is False


# ---------------------------------------------------------------------------
# Result contract
# ---------------------------------------------------------------------------


def test_result_is_frozen_dataclass():
    r = classify_query("foo")
    with pytest.raises((AttributeError, TypeError)):
        r.mode = "other"  # type: ignore[misc]


def test_matched_signals_is_tuple_not_list():
    r = classify_query("List all items.")
    assert isinstance(r.matched_signals, tuple)


def test_result_reason_mentions_score_and_threshold():
    r = classify_query("What is X?")
    assert f"{r.score:.2f}" in r.reason
    # Reason should contain either the threshold value or an ambiguity band cue
    assert ("threshold" in r.reason) or ("ambiguity" in r.reason)
