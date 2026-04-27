"""Tests for apps_shared.proof.otel_export — fail-soft optional OTEL mirror."""

from __future__ import annotations

import os
from typing import Any
from unittest import mock

from apps_shared.proof.otel_export import (
    OtelExportResult,
    _detect_otel,
    maybe_export_spans,
)
from apps_shared.proof.proof_contracts import SpanRecord


def _span(idx: int = 0) -> SpanRecord:
    return SpanRecord(
        trace_id="t1",
        span_id=f"s{idx}",
        parent_span_id=None,
        layer="U0",
        name=f"x{idx}",
        started_at="2026-01-01T00:00:00Z",
        ended_at="2026-01-01T00:00:01Z",
        status="PASS",
        request_id="rq",
        run_id="rn",
        app_id="apps_test",
        scenario_id="t1",
    )


def test_force_disabled_short_circuits():
    r = maybe_export_spans([_span(0), _span(1)], force_disabled=True)
    assert r.status == "DISABLED"
    assert r.spans_attempted == 2
    assert r.spans_exported == 0
    assert "force_disabled" in r.reason


def test_disabled_when_endpoint_missing(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    r = maybe_export_spans([_span(0)])
    assert r.status == "DISABLED"
    # Reason mentions either SDK missing or endpoint missing
    assert "OTEL_EXPORTER_OTLP_ENDPOINT" in r.reason or "SDK not importable" in r.reason


def test_disabled_when_sdk_missing(monkeypatch):
    """When the OTEL SDK is not importable the export must short-circuit."""
    # Simulate ImportError by intercepting the import
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any):
        if name == "opentelemetry":
            raise ImportError("simulated missing SDK")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    r = maybe_export_spans([_span(0)])
    assert r.status == "DISABLED"
    assert "SDK not importable" in r.reason
    assert r.sdk_present is False


def test_result_to_dict_serializable():
    r = OtelExportResult(
        status="DISABLED",
        reason="x",
        spans_attempted=3,
        sdk_present=False,
        endpoint=None,
    )
    d = r.to_dict()
    assert d["status"] == "DISABLED"
    assert d["spans_attempted"] == 3
    assert d["errors"] == []


def test_detect_otel_returns_tuple():
    sdk_present, endpoint = _detect_otel()
    assert isinstance(sdk_present, bool)
    # endpoint is either None or a string
    assert endpoint is None or isinstance(endpoint, str)


def test_empty_span_list_disabled_path(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    r = maybe_export_spans([])
    assert r.status == "DISABLED"
    assert r.spans_attempted == 0


def test_force_disabled_overrides_configured_endpoint(monkeypatch):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    r = maybe_export_spans([_span(0)], force_disabled=True)
    assert r.status == "DISABLED"
    assert r.endpoint == "http://localhost:4318"  # endpoint detected
    # but export was forced disabled
    assert r.spans_exported == 0
