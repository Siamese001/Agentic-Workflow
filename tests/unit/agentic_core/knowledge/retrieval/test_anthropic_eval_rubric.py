"""Unit tests for anthropic_eval_rubric."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.anthropic_eval_rubric import (
    FAILURE_ABSTAIN,
    FAILURE_CITATION_GAP,
    FAILURE_JSON_PARSE,
    QueryMeasurement,
    ReportCard,
    build_report_card,
    report_card_to_markdown,
)


def _m(**kwargs) -> QueryMeasurement:
    """Test-local factory with sensible defaults."""
    kwargs.setdefault("query_id", "q")
    return QueryMeasurement(**kwargs)


# ---------------------------------------------------------------------------
# Empty / minimal runs
# ---------------------------------------------------------------------------


def test_empty_run_produces_unknown_everywhere():
    card = build_report_card("empty-run", [])
    assert card.query_count == 0
    assert card.overall_status == "unknown"
    for dim in card.dimensions:
        assert dim.sample_count == 0
        assert dim.status == "unknown"
        assert dim.mean is None


def test_single_query_all_green():
    m = _m(
        relevance_score=0.95,
        faithfulness_score=0.98,
        citation_correctness=0.92,
        latency_ms=1200.0,
        cost_usd=0.02,
    )
    card = build_report_card("happy-path", [m])
    assert card.query_count == 1
    assert card.overall_status == "green"
    status_by_name = {d.name: d.status for d in card.dimensions}
    for name in ("relevance", "faithfulness", "citation_correctness", "latency_ms", "cost_usd"):
        assert status_by_name[name] == "green", f"{name} should be green"


# ---------------------------------------------------------------------------
# Dimension isolation — missing data doesn't poison other dimensions
# ---------------------------------------------------------------------------


def test_missing_dimension_is_unknown_not_zero():
    # Query has relevance only; other dimensions should be 'unknown'
    m = _m(relevance_score=0.9)
    card = build_report_card("sparse", [m])
    status_by_name = {d.name: d.status for d in card.dimensions}
    assert status_by_name["relevance"] == "green"
    assert status_by_name["faithfulness"] == "unknown"
    assert status_by_name["cost_usd"] == "unknown"


def test_mixed_present_missing_across_queries():
    measurements = [
        _m(query_id="q1", relevance_score=0.9, latency_ms=100.0),
        _m(query_id="q2", relevance_score=0.8),  # no latency
        _m(query_id="q3", latency_ms=200.0),  # no relevance
    ]
    card = build_report_card("mixed", measurements)
    rel = next(d for d in card.dimensions if d.name == "relevance")
    lat = next(d for d in card.dimensions if d.name == "latency_ms")
    assert rel.sample_count == 2
    assert lat.sample_count == 2


# ---------------------------------------------------------------------------
# Traffic-light logic
# ---------------------------------------------------------------------------


def test_relevance_yellow_within_10_points_of_green():
    m = _m(relevance_score=0.72)  # 0.80 green -> 0.72 yellow (within 10pt)
    card = build_report_card("rel-yellow", [m])
    rel = next(d for d in card.dimensions if d.name == "relevance")
    assert rel.status == "yellow"


def test_relevance_red_more_than_10_points_below():
    m = _m(relevance_score=0.50)
    card = build_report_card("rel-red", [m])
    rel = next(d for d in card.dimensions if d.name == "relevance")
    assert rel.status == "red"


def test_latency_p95_red_threshold():
    measurements = [_m(latency_ms=20000.0) for _ in range(5)]
    card = build_report_card("slow", measurements)
    lat = next(d for d in card.dimensions if d.name == "latency_ms")
    assert lat.status == "red"


def test_latency_p95_yellow_between_thresholds():
    measurements = [_m(latency_ms=7500.0) for _ in range(5)]
    card = build_report_card("mid", measurements)
    lat = next(d for d in card.dimensions if d.name == "latency_ms")
    assert lat.status == "yellow"


def test_cost_red_above_expensive_threshold():
    m = _m(cost_usd=2.0)
    card = build_report_card("expensive", [m])
    cost = next(d for d in card.dimensions if d.name == "cost_usd")
    assert cost.status == "red"


def test_custom_thresholds_change_status():
    m = _m(relevance_score=0.70)
    # With default threshold 0.80 this would be yellow; lower to 0.60 -> green
    card = build_report_card("custom", [m], relevance_green=0.60)
    rel = next(d for d in card.dimensions if d.name == "relevance")
    assert rel.status == "green"


# ---------------------------------------------------------------------------
# Overall status aggregation
# ---------------------------------------------------------------------------


def test_overall_status_is_worst_of_dimensions():
    # Relevance red + everything else green -> overall red
    measurements = [
        _m(relevance_score=0.4, faithfulness_score=0.95, citation_correctness=0.9,
           latency_ms=500.0, cost_usd=0.01),
    ]
    card = build_report_card("worst-wins", measurements)
    assert card.overall_status == "red"


def test_overall_yellow_when_no_red_but_any_yellow():
    measurements = [
        _m(relevance_score=0.72, faithfulness_score=0.95, citation_correctness=0.9,
           latency_ms=500.0, cost_usd=0.01),
    ]
    card = build_report_card("yellow", measurements)
    assert card.overall_status == "yellow"


def test_overall_green_when_all_green():
    measurements = [
        _m(relevance_score=0.95, faithfulness_score=0.98, citation_correctness=0.92,
           latency_ms=500.0, cost_usd=0.01),
    ]
    card = build_report_card("green", measurements)
    assert card.overall_status == "green"


# ---------------------------------------------------------------------------
# Percentile correctness
# ---------------------------------------------------------------------------


def test_percentile_is_stable_for_uniform_values():
    measurements = [_m(latency_ms=100.0) for _ in range(10)]
    card = build_report_card("uniform", measurements)
    lat = next(d for d in card.dimensions if d.name == "latency_ms")
    assert lat.p50 == 100.0
    assert lat.p95 == 100.0


def test_percentile_orders_by_rank():
    values = [100.0, 200.0, 300.0, 400.0, 500.0]
    measurements = [_m(latency_ms=v) for v in values]
    card = build_report_card("ordered", measurements)
    lat = next(d for d in card.dimensions if d.name == "latency_ms")
    assert lat.p50 == 300.0
    # p95 of 5 evenly-spaced values interpolates to ~480
    assert 450.0 <= (lat.p95 or 0) <= 500.0


# ---------------------------------------------------------------------------
# Failure mode tracking
# ---------------------------------------------------------------------------


def test_failure_modes_counted_separately_from_dimensions():
    measurements = [
        _m(query_id="q1", failure_mode=FAILURE_ABSTAIN),
        _m(query_id="q2", failure_mode=FAILURE_ABSTAIN),
        _m(query_id="q3", failure_mode=FAILURE_CITATION_GAP),
        _m(query_id="q4", relevance_score=0.9),  # success
    ]
    card = build_report_card("mixed", measurements)
    assert card.failure_mode_counts[FAILURE_ABSTAIN] == 2
    assert card.failure_mode_counts[FAILURE_CITATION_GAP] == 1
    assert card.query_count == 4


def test_no_failures_produces_empty_counter():
    card = build_report_card("clean", [_m(relevance_score=0.9)])
    assert card.failure_mode_counts == {}


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def test_markdown_contains_key_sections():
    measurements = [
        _m(relevance_score=0.9, latency_ms=1000.0, cost_usd=0.05,
           failure_mode=FAILURE_JSON_PARSE),
    ]
    card = build_report_card("md-test", measurements)
    md = report_card_to_markdown(card)
    assert "# Retrieval Eval Report" in md
    assert "md-test" in md
    assert "relevance" in md
    assert "latency_ms" in md
    assert "Failure modes" in md
    assert FAILURE_JSON_PARSE in md


def test_markdown_omits_failure_section_when_no_failures():
    card = build_report_card("clean", [_m(relevance_score=0.9)])
    md = report_card_to_markdown(card)
    assert "Failure modes" not in md


# ---------------------------------------------------------------------------
# Result dataclass contract
# ---------------------------------------------------------------------------


def test_report_card_is_frozen():
    card = build_report_card("x", [])
    with pytest.raises((AttributeError, TypeError)):
        card.run_id = "changed"  # type: ignore[misc]


def test_report_card_dimensions_is_tuple_not_list():
    card = build_report_card("x", [])
    assert isinstance(card.dimensions, tuple)
    assert len(card.dimensions) == 5  # relevance, faithfulness, citation, latency, cost
