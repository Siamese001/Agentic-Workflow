"""Tests for ADR-027 Anthropic-alignment on the OTel MCP server surface.

Covers:
- traceparent round-trip: ingest stamps it on root span; query lifts it back.
- Service config exposes Anthropic-aligned knobs.
"""

from __future__ import annotations

from tools.otel.otel_config import build_config
from tools.otel.otel_services_ingest import OTelIngestService
from tools.otel.otel_services_query import _attach_trace_context
from tools.otel.otel_state import RuntimeMetrics


class _MemoryGateway:
    """In-memory stand-in for RuntimeADGWriteGateway."""

    def __init__(self):
        self.snapshots = []

    def persist_snapshot(self, snapshot):
        self.snapshots.append(snapshot)
        return snapshot.snapshot_id


class TestIngestAcceptsTraceparent:
    def test_ingest_stamps_traceparent_onto_root_span(self, monkeypatch):
        monkeypatch.setenv("OTEL_MCP_LOG_TOOL_CONTENT", "1")
        cfg = build_config(__file__)
        metrics = RuntimeMetrics()
        gateway = _MemoryGateway()
        svc = OTelIngestService(cfg, metrics, gateway)
        trace_data = {
            "trace_id": "deadbeefcafebabe12345678",
            "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
            "tracestate": "vendor=abc",
            "spans": [
                {
                    "span_id": "root1",
                    "parent_span_id": "",
                    "name": "root",
                    "kind": "orchestrator",
                    "layer": "L3",
                    "component": "Orchestrator",
                    "ts_utc": 1700000000,
                    "duration_ms": 1.0,
                    "status": "ok",
                    "attributes": {},
                },
            ],
        }
        result = svc.ingest_to_runtime_adg(trace_data)
        assert result["success"] is True
        assert result["traceparent"] == trace_data["traceparent"]
        assert result["tracestate"] == trace_data["tracestate"]
        snapshot = gateway.snapshots[0]
        assert snapshot.nodes
        # Root span attributes_json must contain the traceparent
        root_attrs = snapshot.nodes[0].attributes_json
        assert "traceparent" in root_attrs
        assert trace_data["traceparent"] in root_attrs


class TestQueryAttachesTraceContext:
    def test_attach_trace_context_from_attributes_json(self):
        snapshot = {
            "nodes": [
                {
                    "node_id": "root1",
                    "attributes_json": '{"traceparent":"00-x-y-01","tracestate":"v=1"}',
                }
            ]
        }
        result = {}
        _attach_trace_context(result, snapshot)
        assert result["traceparent"] == "00-x-y-01"
        assert result["tracestate"] == "v=1"

    def test_attach_trace_context_no_nodes_is_noop(self):
        result = {}
        _attach_trace_context(result, {"nodes": []})
        assert "traceparent" not in result

    def test_attach_trace_context_missing_field_is_noop(self):
        snapshot = {"nodes": [{"node_id": "root1", "attributes_json": "{}"}]}
        result = {}
        _attach_trace_context(result, snapshot)
        assert "traceparent" not in result


class TestConfigKnobs:
    def test_build_config_exposes_anthropic_knobs(self, monkeypatch):
        monkeypatch.setenv("OTEL_SERVICE_NAME", "otel-mcp-test")
        monkeypatch.setenv("OTEL_SERVICE_VERSION", "1.2.3")
        monkeypatch.setenv("OTEL_DEPLOYMENT_ENVIRONMENT", "ci")
        monkeypatch.setenv("OTEL_MCP_LOG_TOOL_CONTENT", "1")
        monkeypatch.setenv("OTEL_MCP_SPAN_ATTR_MAX_BYTES", "30000")
        cfg = build_config(__file__)
        assert cfg.service_name == "otel-mcp-test"
        assert cfg.service_version == "1.2.3"
        assert cfg.deployment_environment == "ci"
        assert cfg.log_tool_content is True
        assert cfg.span_attr_max_bytes == 30000
