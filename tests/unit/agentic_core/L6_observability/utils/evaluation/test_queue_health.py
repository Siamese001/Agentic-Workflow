"""
tests/unit/agentic_core/L6_observability/utils/evaluation/test_queue_health.py

Queue backpressure and health tests for AsyncEvalIngester and ShadowEvalIngester.

Covers:
  - status() keys and types
  - enqueue_count increments on success
  - drop_count increments when queue is full
  - drain_count increments after drain()
  - saturation_pct calculation
  - WARNING log emitted on async packet drop (ingest_eval_packet)
  - WARNING log emitted on shadow packet drop (enqueue_shadow_eval_packet)
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.eval_pipeline

from ops_scripts.reports.async_eval_packet import (
    _QUEUE_MAXSIZE,
    AsyncEvalIngester,
    ShadowEvalIngester,
    get_async_eval_ingester,
    get_shadow_eval_ingester,
    ingest_eval_packet,
    reset_async_eval_ingester,
    reset_shadow_eval_ingester,
)

# ---------------------------------------------------------------------------
# AsyncEvalIngester
# ---------------------------------------------------------------------------


class TestAsyncEvalIngesterHealth:
    def setup_method(self):
        reset_async_eval_ingester()

    def teardown_method(self):
        reset_async_eval_ingester()

    def test_status_keys_present(self):
        ing = AsyncEvalIngester()
        s = ing.status()
        assert set(s.keys()) == {
            "qsize",
            "maxsize",
            "saturation_pct",
            "enqueue_count",
            "drop_count",
            "drain_count",
        }

    def test_initial_status_zeros(self):
        ing = AsyncEvalIngester()
        s = ing.status()
        assert s["qsize"] == 0
        assert s["enqueue_count"] == 0
        assert s["drop_count"] == 0
        assert s["drain_count"] == 0
        assert s["saturation_pct"] == 0.0
        assert s["maxsize"] == _QUEUE_MAXSIZE

    def test_enqueue_count_increments(self):
        ing = AsyncEvalIngester()
        pkt = MagicMock()
        ing.ingest(pkt)
        ing.ingest(pkt)
        assert ing.status()["enqueue_count"] == 2
        assert ing.status()["drop_count"] == 0

    def test_drop_count_increments_when_full(self):
        ing = AsyncEvalIngester()
        ing._queue.maxsize = 2
        pkt = MagicMock()
        ing.ingest(pkt)
        ing.ingest(pkt)
        result = ing.ingest(pkt)
        assert result is False
        assert ing.status()["drop_count"] == 1
        assert ing.status()["enqueue_count"] == 2

    def test_drain_count_increments(self):
        ing = AsyncEvalIngester()
        pkt = MagicMock()
        ing.ingest(pkt)
        ing.ingest(pkt)
        drained = ing.drain(max_packets=5)
        assert len(drained) == 2
        assert ing.status()["drain_count"] == 2

    def test_saturation_pct_computed(self):
        ing = AsyncEvalIngester()
        ing._queue.maxsize = 10
        for _ in range(5):
            ing.ingest(MagicMock())
        s = ing.status()
        assert s["saturation_pct"] == pytest.approx(50.0, abs=1.0)

    def test_status_qsize_reflects_current_depth(self):
        ing = AsyncEvalIngester()
        pkt = MagicMock()
        ing.ingest(pkt)
        assert ing.status()["qsize"] == 1
        ing.drain()
        assert ing.status()["qsize"] == 0


# ---------------------------------------------------------------------------
# ShadowEvalIngester
# ---------------------------------------------------------------------------


class TestShadowEvalIngesterHealth:
    def setup_method(self):
        reset_shadow_eval_ingester()

    def teardown_method(self):
        reset_shadow_eval_ingester()

    def test_status_keys_present(self):
        ing = ShadowEvalIngester()
        s = ing.status()
        assert set(s.keys()) == {
            "qsize",
            "maxsize",
            "saturation_pct",
            "enqueue_count",
            "drop_count",
            "drain_count",
        }

    def test_initial_status_zeros(self):
        ing = ShadowEvalIngester()
        s = ing.status()
        assert s["enqueue_count"] == 0
        assert s["drop_count"] == 0
        assert s["drain_count"] == 0

    def test_enqueue_count_increments(self):
        ing = ShadowEvalIngester()
        pkt = MagicMock()
        ing.enqueue(pkt)
        ing.enqueue(pkt)
        assert ing.status()["enqueue_count"] == 2
        assert ing.status()["drop_count"] == 0

    def test_drop_count_increments_when_full(self):
        ing = ShadowEvalIngester()
        ing._queue.maxsize = 1
        pkt = MagicMock()
        ing.enqueue(pkt)
        result = ing.enqueue(pkt)
        assert result is False
        assert ing.status()["drop_count"] == 1

    def test_drain_count_increments(self):
        ing = ShadowEvalIngester()
        pkt = MagicMock()
        ing.enqueue(pkt)
        ing.drain(max_packets=5)
        assert ing.status()["drain_count"] == 1


# ---------------------------------------------------------------------------
# Drop warning logs
# ---------------------------------------------------------------------------


class TestDropWarningLogs:
    def setup_method(self):
        reset_async_eval_ingester()
        reset_shadow_eval_ingester()

    def teardown_method(self):
        reset_async_eval_ingester()
        reset_shadow_eval_ingester()

    def test_async_drop_emits_warning(self, caplog):
        ing = get_async_eval_ingester()
        ing._queue.maxsize = 1
        ing.ingest(MagicMock())

        mock_gate_result = MagicMock()
        mock_gate_result.to_dict.return_value = {}
        mock_metrics = MagicMock()
        mock_metrics.collection = "test"
        mock_metrics.citation_completeness = 0.5
        mock_metrics.support_coverage = 0.5
        mock_metrics.provenance_completeness = 0.5
        mock_metrics.exact_match_ratio = 0.5
        mock_metrics.grounded_replayable = True
        mock_metrics.contradiction_present = False
        mock_metrics.query_hash = "qh"
        mock_metrics.retrieval_id = "rid"
        mock_weak = MagicMock()
        mock_weak.value = "ADEQUATE"

        with caplog.at_level(
            logging.WARNING, logger="agentic_core.L6_observability.utils.evaluation.async_eval_packet"
        ):
            ingest_eval_packet(
                run_id="r1",
                lane_id="lane1",
                gate_result=mock_gate_result,
                metrics=mock_metrics,
                weak_support_disposition=mock_weak,
            )

        drop_records = [r for r in caplog.records if "AsyncEvalIngester" in r.message and "Drop" in r.message]
        assert drop_records, "Expected at least one AsyncEvalIngester Drop warning"
        assert any("maxsize=1" in r.message for r in drop_records), (
            "Drop warning must log actual queue maxsize (1), not the _QUEUE_MAXSIZE constant (5000)"
        )

    def test_shadow_drop_emits_warning(self, caplog):
        from ops_scripts.reports.async_eval_packet import (
            enqueue_shadow_eval_packet,
        )

        ing = get_shadow_eval_ingester()
        ing._queue.maxsize = 1
        ing.enqueue(MagicMock())

        mock_packet = MagicMock()
        mock_packet.packet_id = "sp-test"

        with caplog.at_level(
            logging.WARNING, logger="agentic_core.L6_observability.utils.evaluation.async_eval_packet"
        ):
            enqueue_shadow_eval_packet(mock_packet)

        drop_records = [
            r for r in caplog.records if "ShadowEvalIngester" in r.message and "Drop" in r.message
        ]
        assert drop_records, "Expected at least one ShadowEvalIngester Drop warning"
        assert any("maxsize=1" in r.message for r in drop_records), (
            "Drop warning must log actual queue maxsize (1), not the _QUEUE_MAXSIZE constant (5000)"
        )
