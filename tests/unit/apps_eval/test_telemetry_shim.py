"""Unit tests for the apps_eval._telemetry SSOT-delegating shim (ADR-028 §4.3)."""

from __future__ import annotations

import importlib
import sys

import pytest


def _reload_shim():
    """Reload apps_eval._telemetry so we observe a fresh lazy-resolve cycle."""
    if "apps_eval._telemetry" in sys.modules:
        del sys.modules["apps_eval._telemetry"]
    return importlib.import_module("apps_eval._telemetry")


def test_layer_segment_members_match_ssot():
    """LayerSegment must expose the canonical 7 layer members with SSOT values."""
    shim = _reload_shim()
    expected = {
        "L0_ROUTING",
        "L1_REASONING",
        "L2_EXECUTION",
        "L3_ORCHESTRATION",
        "L4_STATE",
        "L5_POLICY",
        "L6_OBSERVABILITY",
    }
    actual = {m.name for m in shim.LayerSegment}
    assert actual == expected
    for name in expected:
        assert getattr(shim.LayerSegment, name).value == name


def test_emit_functions_delegate_to_ssot_when_available():
    """With agentic_core importable, shim emits must resolve to the real SSOT callable."""
    shim = _reload_shim()
    from agentic_core.runtime.contracts import lifecycle_trace_contract as ssot

    shim._emit_records_execution_trace("trace-1", shim.LayerSegment.L3_ORCHESTRATION, "op")

    resolved = shim._emit_records_execution_trace
    assert resolved is ssot._emit_records_execution_trace, (
        "emit function must resolve to the SSOT callable, not the local _noop"
    )


def test_unknown_attribute_raises():
    """Non-emit attribute access must raise AttributeError (no silent noop)."""
    shim = _reload_shim()
    with pytest.raises(AttributeError):
        shim.not_a_real_attribute  # noqa: B018


def test_emit_prefix_returns_callable_and_never_raises():
    """Any ``_emit_*`` or ``emit_*`` name must return a no-argument-safe callable."""
    shim = _reload_shim()
    assert callable(shim._emit_brand_new_never_existing)
    assert shim._emit_brand_new_never_existing() is None
    assert callable(shim.emit_anything_here)
    assert shim.emit_anything_here("a", "b", kw=1) is None


def test_shim_survives_ssot_import_failure(monkeypatch):
    """When SSOT import fails, every emit silently no-ops (fail-open preserved)."""
    if "apps_eval._telemetry" in sys.modules:
        del sys.modules["apps_eval._telemetry"]
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__  # type: ignore[attr-defined]

    def _blocked(name, *args, **kwargs):
        if name.startswith("agentic_core"):
            raise ImportError(f"simulated missing: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _blocked)
    shim = importlib.import_module("apps_eval._telemetry")

    emit = shim._emit_records_execution_trace
    # When SSOT is unavailable, the resolved callable must be the internal _noop
    assert emit is shim._noop
    assert emit("any", "args", "ok") is None
