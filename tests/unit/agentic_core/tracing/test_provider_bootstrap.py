"""Unit tests for the generic OTEL provider bootstrap.

OpenTelemetry's ``set_tracer_provider`` is once-per-process, so once any test
installs a real SDK provider it stays global for the rest of the session.
Assertions are therefore written to accept either the fresh-install status or
``provider_already_installed`` and to verify the *observable* outcome (a real
``TracerProvider`` + a recording tracer), which holds regardless of order.

The ``console`` exporter is intentionally the first installer below — it prints
spans (no network), avoiding OTLP connection noise at interpreter exit.
"""

from __future__ import annotations

import pytest

from agentic_core.tracing import provider_bootstrap as pb


@pytest.fixture(autouse=True)
def _reset_guard():
    pb._reset_for_tests()
    yield
    pb._reset_for_tests()


def test_bootstrap_noop_when_env_unset(monkeypatch):
    monkeypatch.delenv("OTEL_TRACES_EXPORTER", raising=False)
    assert pb.ensure_tracer_provider_from_env() == "disabled_env_unset"
    assert pb.otel_activation_status() == "disabled"


def test_bootstrap_installs_recording_provider_when_console_env_set(monkeypatch):
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider

    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "console")
    status = pb.ensure_tracer_provider_from_env()
    assert status in ("console_installed", "provider_already_installed")
    assert isinstance(trace.get_tracer_provider(), TracerProvider)
    # A real (recording) tracer, not the ProxyTracerProvider no-op.
    span = trace.get_tracer("test.bootstrap").start_span("probe")
    try:
        assert span.is_recording()
    finally:
        span.end()
    # Drain the batch processor now (while captured stdout is still open) so the
    # console exporter does not try to flush at interpreter exit against a closed
    # capture file — a benign-but-noisy pytest teardown artifact otherwise.
    trace.get_tracer_provider().force_flush()


def test_bootstrap_idempotent(monkeypatch):
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "console")
    first = pb.ensure_tracer_provider_from_env()
    assert first in ("console_installed", "provider_already_installed")
    second = pb.ensure_tracer_provider_from_env()
    assert second == "already_bootstrapped"


def test_bootstrap_otlp_http_branch(monkeypatch):
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider

    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "otlp")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    status = pb.ensure_tracer_provider_from_env()
    assert status in ("otlp_http_installed", "provider_already_installed")
    assert isinstance(trace.get_tracer_provider(), TracerProvider)


def test_bootstrap_never_raises_on_install_error(monkeypatch):
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "console")

    def _boom(_kind):
        raise RuntimeError("simulated install failure")

    monkeypatch.setattr(pb, "_install_provider", _boom)
    # Fail-soft: must not propagate the exception.
    assert pb.ensure_tracer_provider_from_env() == "bootstrap_failed:RuntimeError"


def test_unknown_exporter_kind(monkeypatch):
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "nope")
    status = pb.ensure_tracer_provider_from_env()
    # If a real provider was installed by an earlier test, OTEL short-circuits
    # before exporter selection; otherwise we get the explicit unknown sentinel.
    assert status in ("unknown_exporter:nope", "provider_already_installed")


def test_activation_status_reflects_env(monkeypatch):
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "otlp")
    assert pb.otel_activation_status() == "enabled:otlp"
    monkeypatch.delenv("OTEL_TRACES_EXPORTER", raising=False)
    assert pb.otel_activation_status() == "disabled"
