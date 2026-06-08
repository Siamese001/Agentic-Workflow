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
