"""Contract test: the core spine installs the OTEL provider bootstrap at entry.

``run_integrated_single_action_spine`` is the single chokepoint every app
crosses. Its first executable statement must invoke the generic, env-gated
provider bootstrap so OTEL spans actually export when opted in — before any
L2/L3 emitter resolves (and caches) its tracer.
"""

from __future__ import annotations

from pathlib import Path

import agentic_core.tracing.provider_bootstrap as pb
from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
    run_integrated_single_action_spine,
)

# Minimal request that returns a CACHE_PREFLIGHT fault (no raise) — enough to
# cross the spine entry where the bootstrap call lives.
_MIN_REQUEST = {"jd_payload": {"title": "t", "description": "d"}}


def test_spine_invokes_otel_bootstrap_at_entry(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("OTEL_TRACES_EXPORTER", raising=False)
    calls = {"n": 0}

    def _spy() -> str:
        calls["n"] += 1
        return "disabled_env_unset"

    monkeypatch.setattr(pb, "ensure_tracer_provider_from_env", _spy)

    result = run_integrated_single_action_spine(
        raw_request=_MIN_REQUEST,
        app_name="apps_rg",
        artifact_dir=tmp_path,
    )

    assert calls["n"] >= 1, "spine must invoke ensure_tracer_provider_from_env at entry"
    assert result is not None  # normal (fault) return path — no raise
    assert result.observability_status["external_otel_activation"] == "disabled"
    assert result.observability_status["collector_export_mode"] == "none"
    assert result.observability_status["local_capture_enabled"] is True
    assert (
        result.observability_status["l6_observability_role"]
        == "consume_local_span_records"
    )


def test_spine_installs_recording_provider_when_env_set(monkeypatch, tmp_path: Path):
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider

    pb._reset_for_tests()
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "console")

    run_integrated_single_action_spine(
        raw_request=_MIN_REQUEST,
        app_name="apps_rg",
        artifact_dir=tmp_path,
    )

    # Crossing the spine entry with the env set installs a real recording provider.
    assert isinstance(trace.get_tracer_provider(), TracerProvider)


def test_spine_reports_otlp_collector_mode(monkeypatch, tmp_path: Path):
    pb._reset_for_tests()
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "otlp")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    result = run_integrated_single_action_spine(
        raw_request=_MIN_REQUEST,
        app_name="apps_rg",
        artifact_dir=tmp_path,
    )

    assert result.observability_status["external_otel_activation"] == "enabled:otlp"
    assert result.observability_status["collector_export_mode"] == "otlp"
    assert result.observability_status["collector_endpoint"] == "http://localhost:4318"
    assert result.observability_status["local_capture_enabled"] is True
