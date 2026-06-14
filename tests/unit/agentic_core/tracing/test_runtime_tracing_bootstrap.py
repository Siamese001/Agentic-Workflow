"""Regression — the single runtime tracing bootstrap seam (Phase 2).

Proves provider bootstrap is invoked through ``bootstrap_runtime_tracing`` with
honest, structured status: disabled when OTEL env is unset, attempted (not
ignored) when it opts in, local capture always on, and never raising.
"""

from __future__ import annotations

import pytest

from agentic_core.tracing import provider_bootstrap
from agentic_core.tracing.runtime_tracing import (
    RuntimeTracingStatus,
    bootstrap_runtime_tracing,
)


@pytest.fixture(autouse=True)
def _reset_bootstrap_guard():
    # Clear the once-per-process guard so each case re-evaluates the env gate.
    provider_bootstrap._reset_for_tests()
    yield
    provider_bootstrap._reset_for_tests()


def test_bootstrap_disabled_when_otel_env_unset(monkeypatch):
    monkeypatch.delenv("OTEL_TRACES_EXPORTER", raising=False)
    status = bootstrap_runtime_tracing()
    assert isinstance(status, RuntimeTracingStatus)
    assert status.external_otel_activation == "disabled"
    assert status.provider_bootstrap_status == "disabled_env_unset"
    # Local deterministic span records are the L6 source regardless of export.
    assert status.local_capture_enabled is True


def test_bootstrap_attempted_when_console_exporter_set(monkeypatch):
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "console")
    status = bootstrap_runtime_tracing()
    assert status.external_otel_activation == "enabled:console"
    # Bootstrap must NOT report itself disabled/ignored when env opts in. The
    # exact value depends on whether a real provider was already installed in
    # this process (set_tracer_provider is once-per-process).
    assert status.provider_bootstrap_status != "disabled_env_unset"
    assert status.provider_bootstrap_status in {
        "console_installed",
        "provider_already_installed",
        "already_bootstrapped",
        "sdk_unavailable",
    }


def test_bootstrap_never_raises_on_unknown_exporter(monkeypatch):
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "not-a-real-exporter")
    status = bootstrap_runtime_tracing()  # must not raise
    assert isinstance(status, RuntimeTracingStatus)
    assert status.external_otel_activation == "enabled:not-a-real-exporter"
