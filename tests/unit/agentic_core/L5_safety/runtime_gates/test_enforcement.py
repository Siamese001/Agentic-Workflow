"""Tests for runtime-gate enforcement bridge."""

from __future__ import annotations

import logging

import pytest

from agentic_core.L5_safety.runtime_gates import GateContext
from agentic_core.L5_safety.runtime_gates.dispatch import LAYER_U0
from agentic_core.L5_safety.runtime_gates.enforcement import (
    EnforcementMode,
    RuntimeGateHaltError,
    enforce_layer,
    enforces_layer,
)


def _bad_ctx() -> GateContext:
    """Context guaranteed to fail G01 (missing envelope)."""
    return GateContext()


def _good_ctx() -> GateContext:
    return GateContext(
        request_id="req-1",
        session_id="sess-1",
        trace_root="trace-1",
        tenant_id="tenant-A",
        intent={"objective": "summarize", "raw_text": "x", "payload_bytes": 100},
        caller_scope_baseline={"tenant_id": "tenant-A", "session_id": "sess-1"},
    )


# ---- enforce_layer ----


def test_enforce_layer_audit_passes_clean(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="agentic_core.L5_safety.runtime_gates.enforcement")
    result = enforce_layer(LAYER_U0, _good_ctx(), mode=EnforcementMode.AUDIT)
    assert result.passed
    assert any("result=passed" in rec.message for rec in caplog.records)


def test_enforce_layer_strict_raises_on_halt() -> None:
    with pytest.raises(RuntimeGateHaltError) as excinfo:
        enforce_layer(LAYER_U0, _bad_ctx(), mode=EnforcementMode.STRICT)
    err = excinfo.value
    assert err.layer == LAYER_U0
    assert not err.result.passed
    assert err.result.halted_at == "G01"


def test_enforce_layer_soft_returns_on_halt(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING, logger="agentic_core.L5_safety.runtime_gates.enforcement")
    result = enforce_layer(LAYER_U0, _bad_ctx(), mode=EnforcementMode.SOFT)
    assert not result.passed
    assert result.halted_at == "G01"
    # Soft mode logs a warning but does not raise.
    assert any("result=halted" in rec.message for rec in caplog.records)


def test_enforce_layer_audit_does_not_raise_on_halt() -> None:
    result = enforce_layer(LAYER_U0, _bad_ctx(), mode=EnforcementMode.AUDIT)
    assert not result.passed


def test_enforce_layer_off_returns_empty() -> None:
    result = enforce_layer(LAYER_U0, _bad_ctx(), mode=EnforcementMode.OFF)
    assert result.passed
    assert result.decisions == []


def test_enforce_layer_per_layer_disable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNTIME_GATES_DISABLED_LAYERS", "U0,L0")
    # Even strict mode is bypassed when the layer is disabled.
    result = enforce_layer(LAYER_U0, _bad_ctx(), mode=EnforcementMode.STRICT)
    assert result.passed
    assert result.decisions == []


def test_enforce_layer_env_mode_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNTIME_GATES_ENFORCEMENT_MODE", "strict")
    with pytest.raises(RuntimeGateHaltError):
        enforce_layer(LAYER_U0, _bad_ctx())


def test_enforce_layer_unknown_env_mode_falls_back(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("RUNTIME_GATES_ENFORCEMENT_MODE", "BOGUS")
    caplog.set_level(logging.WARNING, logger="agentic_core.L5_safety.runtime_gates.enforcement")
    # Falls back to AUDIT (default) — no raise.
    result = enforce_layer(LAYER_U0, _bad_ctx())
    assert not result.passed
    assert any("unknown mode" in rec.message for rec in caplog.records)


def test_enforce_layer_explicit_mode_string() -> None:
    with pytest.raises(RuntimeGateHaltError):
        enforce_layer(LAYER_U0, _bad_ctx(), mode="strict")


def test_enforce_layer_invalid_mode_string_raises() -> None:
    with pytest.raises(ValueError, match="unknown enforcement mode"):
        enforce_layer(LAYER_U0, _bad_ctx(), mode="BOGUS")


# ---- @enforces_layer decorator ----


def test_decorator_calls_function_in_audit_mode() -> None:
    @enforces_layer(LAYER_U0, mode=EnforcementMode.AUDIT)
    def handler(*, ctx: GateContext) -> dict:
        return {"ok": True}

    result = handler(ctx=_good_ctx())
    assert result["ok"] is True


def test_decorator_blocks_function_in_strict_on_halt() -> None:
    @enforces_layer(LAYER_U0, mode=EnforcementMode.STRICT)
    def handler(*, ctx: GateContext) -> dict:
        return {"ok": True}

    with pytest.raises(RuntimeGateHaltError):
        handler(ctx=_bad_ctx())


def test_decorator_uses_ctx_builder_when_provided() -> None:
    def builder(**_kwargs):
        return _good_ctx()

    @enforces_layer(LAYER_U0, ctx_builder=builder, mode=EnforcementMode.AUDIT)
    def handler(*, request_id: str) -> dict:
        return {"id": request_id}

    out = handler(request_id="req-99")
    assert out["id"] == "req-99"


def test_decorator_raises_when_ctx_missing_and_no_builder() -> None:
    @enforces_layer(LAYER_U0, mode=EnforcementMode.AUDIT)
    def handler(*, ctx: GateContext = None) -> dict:  # type: ignore[assignment]
        return {}

    with pytest.raises(TypeError, match="no GateContext found"):
        handler()


class _Resp:
    """Plain object that allows attribute attachment (dicts don't)."""

    def __init__(self, ok: bool) -> None:
        self.ok = ok


def test_decorator_attaches_runtime_gate_result_to_object() -> None:
    @enforces_layer(LAYER_U0, mode=EnforcementMode.AUDIT)
    def handler(*, ctx: GateContext) -> _Resp:
        return _Resp(ok=True)

    out = handler(ctx=_good_ctx())
    assert hasattr(out, "__runtime_gate_result__")
    assert out.__runtime_gate_result__.passed  # type: ignore[attr-defined]


def test_decorator_silently_skips_attach_for_immutable_return() -> None:
    """dicts/tuples don't allow attribute attachment; wrapper must not crash."""

    @enforces_layer(LAYER_U0, mode=EnforcementMode.AUDIT)
    def handler(*, ctx: GateContext) -> dict:
        return {"ok": True}

    out = handler(ctx=_good_ctx())
    # Best-effort attach is silently skipped for dict.
    assert out == {"ok": True}


def test_decorator_marks_layer_attribute() -> None:
    @enforces_layer(LAYER_U0, mode=EnforcementMode.AUDIT)
    def handler(*, ctx: GateContext) -> dict:
        return {}

    assert handler.__runtime_gate_layer__ == LAYER_U0  # type: ignore[attr-defined]
