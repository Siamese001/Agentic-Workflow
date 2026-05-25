"""W7 wiring test: otel_runtime_ingest publishes TRACE_INGEST_FRESHNESS."""

from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability import otel_runtime_ingest as mod
from agentic_core.L6_observability.utils.evaluation.learning_metrics_dashboard import (
    get_v6_kpi_board,
    reset_v6_kpi_board,
)
from agentic_core.L6_system_learning.v6_kpi_board import V6KPIName


@pytest.fixture(autouse=True)
def _reset():
    reset_v6_kpi_board()
    yield
    reset_v6_kpi_board()


class TestNewestSpanEpoch:
    def test_end_time_unix_nano_preferred(self):
        spans = [
            {"end_time_unix_nano": 1_000_000_000},
            {"end_time_unix_nano": 2_000_000_000},
        ]
        assert mod._newest_span_epoch(spans) == 2.0  # pylint: disable=protected-access

    def test_falls_back_to_end_time_seconds(self):
        spans = [{"end_time": 42.0}]
        assert mod._newest_span_epoch(spans) == 42.0  # pylint: disable=protected-access

    def test_falls_back_to_start_time(self):
        spans = [{"start_time_unix_nano": 3_000_000_000}]
        assert mod._newest_span_epoch(spans) == 3.0  # pylint: disable=protected-access

    def test_falls_back_to_timestamp(self):
        spans = [{"timestamp": 99.0}]
        assert mod._newest_span_epoch(spans) == 99.0  # pylint: disable=protected-access

    def test_invalid_span_skipped(self):
        spans = ["not a dict", {"end_time": 10.0}, None]
        assert mod._newest_span_epoch(spans) == 10.0  # pylint: disable=protected-access

    def test_no_timestamp_returns_none(self):
        spans = [{"name": "no timing"}]
        assert mod._newest_span_epoch(spans) is None  # pylint: disable=protected-access


class TestPublishFreshness:
    def test_fresh_span_records_small_age(self):
        now = time.time()
        mod._publish_trace_ingest_freshness([{"end_time": now - 30.0}])  # pylint: disable=protected-access
        sample = get_v6_kpi_board().latest(V6KPIName.TRACE_INGEST_FRESHNESS)
        assert sample is not None
        assert sample.value < 120.0  # well within 10-min green band

    def test_no_timestamp_no_record(self):
        mod._publish_trace_ingest_freshness([{"name": "empty"}])  # pylint: disable=protected-access
        assert get_v6_kpi_board().latest(V6KPIName.TRACE_INGEST_FRESHNESS) is None

    def test_empty_list_no_record(self):
        mod._publish_trace_ingest_freshness([])  # pylint: disable=protected-access
        assert get_v6_kpi_board().latest(V6KPIName.TRACE_INGEST_FRESHNESS) is None
