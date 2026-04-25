"""Tests for OTEL → BaselineRegistry live feed."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.baseline_registry import BaselineRegistry
from agentic_core.L5_safety.runtime_gates.otel_feed import (
    OtelBaselineFeed,
    consume_span_stream,
    default_span_extractor,
)


# ---- default_span_extractor ----


def test_extractor_standard_otel_attributes() -> None:
    span = {
        "attributes": {
            "task.class": "summarize",
            "gen_ai.usage.input_tokens": 500,
            "gen_ai.usage.output_tokens": 200,
            "gen_ai.cost.usd": 0.05,
        },
        "duration_ms": 1500,
    }
    extracted = default_span_extractor(span)
    assert extracted is not None
    task_class, obs = extracted
    assert task_class == "summarize"
    assert obs["tokens"] == 700.0
    assert obs["cost_usd"] == 0.05
    assert obs["latency_ms"] == 1500.0


def test_extractor_top_level_keys_fallback() -> None:
    span = {
        "task_class": "translate",
        "tokens": 1000,
        "cost_usd": 0.10,
        "latency_ms": 500,
        "tool_count": 3,
        "retry_count": 1,
    }
    extracted = default_span_extractor(span)
    assert extracted is not None
    task_class, obs = extracted
    assert task_class == "translate"
    assert obs == {
        "tokens": 1000.0,
        "cost_usd": 0.10,
        "latency_ms": 500.0,
        "tool_count": 3.0,
        "retry_count": 1.0,
    }


def test_extractor_latency_from_ns_diff() -> None:
    span = {
        "attributes": {"task.class": "x", "tokens": 100},
        "start_time_ns": 1_000_000_000,  # 1s
        "end_time_ns": 1_500_000_000,  # 1.5s
    }
    extracted = default_span_extractor(span)
    assert extracted is not None
    _, obs = extracted
    assert obs["latency_ms"] == 500.0


def test_extractor_no_task_class_returns_none() -> None:
    assert default_span_extractor({"tokens": 100}) is None


def test_extractor_no_metrics_returns_none() -> None:
    assert default_span_extractor({"task_class": "x"}) is None


def test_extractor_invalid_metric_value_skipped() -> None:
    span = {"task_class": "x", "tokens": "not-a-number", "cost_usd": 0.05}
    extracted = default_span_extractor(span)
    assert extracted is not None
    _, obs = extracted
    assert "tokens" not in obs
    assert obs["cost_usd"] == 0.05


# ---- OtelBaselineFeed ----


def test_feed_ingest_span_updates_registry() -> None:
    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg)
    accepted = feed.ingest_span({"task_class": "x", "tokens": 100, "cost_usd": 0.01})
    assert accepted is True
    assert feed.spans_accepted == 1
    assert reg.has("x")


def test_feed_ingest_span_skips_when_no_task_class() -> None:
    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg)
    assert feed.ingest_span({"tokens": 100}) is False
    assert feed.spans_skipped == 1


def test_feed_ingest_span_skips_non_dict() -> None:
    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg)
    assert feed.ingest_span("not a dict") is False  # type: ignore[arg-type]
    assert feed.spans_skipped == 1


def test_feed_ingest_batch_returns_accepted_count() -> None:
    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg)
    spans = [
        {"task_class": "x", "tokens": 100},
        {"task_class": "x", "tokens": 200},
        {"tokens": 100},  # no task_class -> skip
    ]
    assert feed.ingest_batch(spans) == 2
    assert feed.stats() == {
        "spans_seen": 3,
        "spans_accepted": 2,
        "spans_skipped": 1,
        "spans_errored": 0,
    }


def test_feed_custom_extractor() -> None:
    def extractor(span):
        if "x" not in span:
            return None
        return "manual", {"tokens": float(span["x"])}

    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg, span_to_observation=extractor)
    feed.ingest_batch([{"x": 5}, {"x": 10}, {"y": 1}])
    assert feed.spans_accepted == 2
    assert reg.get("manual")["tokens"] > 0


def test_feed_extractor_exception_is_caught(caplog: pytest.LogCaptureFixture) -> None:
    def bad_extractor(_span):
        raise ValueError("boom")

    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg, span_to_observation=bad_extractor)
    feed.ingest_span({"task_class": "x", "tokens": 1})
    assert feed.spans_errored == 1


def test_feed_ema_blend_via_multiple_spans() -> None:
    reg = BaselineRegistry(alpha=0.5)
    feed = OtelBaselineFeed(reg)
    feed.ingest_span({"task_class": "x", "tokens": 1000})
    feed.ingest_span({"task_class": "x", "tokens": 2000})
    # 0.5 * 2000 + 0.5 * 1000 = 1500
    assert reg.get("x")["tokens"] == pytest.approx(1500.0)


# ---- consume_span_stream ----


def test_consume_span_stream_respects_max_spans() -> None:
    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg)
    stream = ({"task_class": "x", "tokens": i} for i in range(100))
    stats = consume_span_stream(feed, stream, max_spans=5)
    assert stats["spans_seen"] == 5


def test_consume_span_stream_full_iteration() -> None:
    reg = BaselineRegistry()
    feed = OtelBaselineFeed(reg)
    stream = [{"task_class": "x", "tokens": 1}, {"task_class": "y", "tokens": 2}]
    stats = consume_span_stream(feed, stream)
    assert stats["spans_seen"] == 2
    assert stats["spans_accepted"] == 2
