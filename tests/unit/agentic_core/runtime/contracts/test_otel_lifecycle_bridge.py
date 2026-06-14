"""Unit tests for the OTEL lifecycle bridge logging handler.

Wave 6.1 of adg-testing-hotspots-wave-plan-a7f3c1: pure-surface coverage for
``agentic_core/runtime/contracts/otel_lifecycle_bridge.py``. Tests the
``AdgEmissionToOtelBridge`` logging handler in isolation — record filtering
(non-``adg.*`` records ignored), span shaping, attribute extraction (layer,
edge_kind, req_ids, k=v pairs), buffer cap + overflow accounting, ``stats``,
the no-span ``flush_to_runtime_adg`` short-circuit (no network), and the
module-level install/get/uninstall lifecycle (idempotent). No external OTEL
services are exercised: every test path stays on the buffered side of the
bridge. The install/uninstall tests restore global state in teardown.
"""
from __future__ import annotations

import logging

import pytest

from agentic_core.runtime.contracts import otel_lifecycle_bridge as mod
from agentic_core.runtime.contracts.otel_lifecycle_bridge import (
    AdgEmissionToOtelBridge,
    get_bridge,
    install_bridge,
    uninstall_bridge,
)


def _record(name: str, msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name=name,
        level=logging.DEBUG,
        pathname="/x/y.py",
        lineno=42,
        msg=msg,
        args=(),
        exc_info=None,
    )


class TestRecordFiltering:
    def test_non_adg_record_ignored(self):
        b = AdgEmissionToOtelBridge()
        b.emit(_record("some.other.logger", "layer=L2_EXEC"))
        assert b.buffered_spans() == []

    def test_adg_record_buffered(self):
        b = AdgEmissionToOtelBridge()
        b.emit(_record("adg.records_execution_trace", "hello"))
        assert len(b.buffered_spans()) == 1


class TestSpanShape:
    def test_span_core_fields(self):
        b = AdgEmissionToOtelBridge(root_trace_id="trace-123")
        b.emit(_record("adg.records_execution_trace", "msg"))
        span = b.buffered_spans()[0]
        assert span["trace_id"] == "trace-123"
        assert span["name"] == "adg.records_execution_trace"
        assert span["kind"] == "INTERNAL"
        assert span["status_code"] == "OK"
        assert span["duration_ms"] == 0.0

    def test_edge_kind_in_attributes(self):
        b = AdgEmissionToOtelBridge()
        b.emit(_record("adg.records_execution_trace", "msg"))
        attrs = b.buffered_spans()[0]["attributes"]
        assert attrs["edge_kind"] == "records_execution_trace"
        assert attrs["agentic.req.edge_kind"] == "records_execution_trace"

    def test_app_id_recorded(self):
        b = AdgEmissionToOtelBridge(app_id="apps_eval")
        b.emit(_record("adg.x", "msg"))
        assert b.buffered_spans()[0]["attributes"]["agentic.req.app"] == "apps_eval"


class TestAttributeExtraction:
    def test_layer_extracted(self):
        b = AdgEmissionToOtelBridge()
        b.emit(_record("adg.x", "layer=L2_EXEC something"))
        attrs = b.buffered_spans()[0]["attributes"]
        assert attrs["layer"] == "L2_EXEC"
        assert attrs["agentic.req.layer"] == "L2_EXEC"

    def test_req_ids_extracted_as_list(self):
        b = AdgEmissionToOtelBridge()
        b.emit(_record("adg.x", "req_ids=REQ-A,REQ-B,REQ-C done"))
        attrs = b.buffered_spans()[0]["attributes"]
        assert attrs["agentic.req.ids"] == ["REQ-A", "REQ-B", "REQ-C"]

    def test_kv_pairs_extracted(self):
        b = AdgEmissionToOtelBridge()
        b.emit(_record("adg.x", "source=alpha target=beta"))
        attrs = b.buffered_spans()[0]["attributes"]
        assert attrs["source"] == "alpha"
        assert attrs["target"] == "beta"


class TestBufferCap:
    def test_overflow_dropped_and_counted(self):
        b = AdgEmissionToOtelBridge(max_buffer=2)
        for _ in range(5):
            b.emit(_record("adg.x", "msg"))
        assert len(b.buffered_spans()) == 2
        assert b.stats()["dropped_overflow"] == 3

    def test_stats_shape(self):
        b = AdgEmissionToOtelBridge(max_buffer=10, root_trace_id="rt")
        b.emit(_record("adg.x", "msg"))
        stats = b.stats()
        assert stats["buffered"] == 1
        assert stats["max_buffer"] == 10
        assert stats["root_trace_id"] == "rt"
        assert stats["uptime_seconds"] >= 0.0


class TestFlushNoSpans:
    def test_flush_short_circuits_when_empty(self):
        b = AdgEmissionToOtelBridge()
        result = b.flush_to_runtime_adg()
        assert result == {
            "success": True,
            "spans_ingested": 0,
            "note": "no buffered spans",
        }


class TestInstallLifecycle:
    def teardown_method(self):
        uninstall_bridge()

    def test_install_returns_bridge_and_registers(self):
        b = install_bridge(root_trace_id="abc")
        assert isinstance(b, AdgEmissionToOtelBridge)
        assert get_bridge() is b
        assert b in logging.getLogger().handlers

    def test_install_is_idempotent(self):
        b1 = install_bridge()
        b2 = install_bridge(root_trace_id="ignored")
        assert b1 is b2

    def test_uninstall_clears(self):
        b = install_bridge()
        uninstall_bridge()
        assert get_bridge() is None
        assert b not in logging.getLogger().handlers

    def test_uninstall_when_not_installed_is_noop(self):
        uninstall_bridge()
        uninstall_bridge()
        assert get_bridge() is None
