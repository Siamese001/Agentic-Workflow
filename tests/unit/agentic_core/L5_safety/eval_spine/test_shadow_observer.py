"""Tests for the eval_spine shadow observer (plan `-a9c124`).

Covers:
- Env-flag gating (EVAL_SPINE_SHADOW).
- SealedL2Artifact → eval_spine.SealedArtifact conversion.
- ExitDecision JSON written to the output_root directory.
- Live-path safety: shadow failures never raise.
- Hook integration into ExitControlGate.evaluate_sealed: existing behavior
  preserved when flag is off; shadow file appears when flag is on.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L2_execution.types.sealed_l2_artifact import (
    SealedL2Artifact,
    TerminalClassification,
    ValidationCounters,
)
from agentic_core.L5_safety.eval_spine import shadow_observer


@pytest.fixture(autouse=True)
def _clear_shadow_flag(monkeypatch):
    """Every test starts with the flag cleared; tests opt-in explicitly."""
    monkeypatch.delenv("EVAL_SPINE_SHADOW", raising=False)


class TestIsShadowEnabled:
    def test_unset_is_disabled(self):
        assert shadow_observer.is_shadow_enabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "TRUE", "Yes", "on"])
    def test_truthy_values_enable(self, monkeypatch, value):
        monkeypatch.setenv("EVAL_SPINE_SHADOW", value)
        assert shadow_observer.is_shadow_enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", ""])
    def test_falsy_values_disable(self, monkeypatch, value):
        monkeypatch.setenv("EVAL_SPINE_SHADOW", value)
        assert shadow_observer.is_shadow_enabled() is False


class TestConversion:
    def test_defaults_when_bundles_empty(self):
        artifact = SealedL2Artifact(artifact_id="a1", trace_id="t1")
        sealed = shadow_observer.sealed_l2_to_eval_spine(artifact)
        assert sealed.request_id == "a1"
        assert sealed.trace_id == "t1"
        assert sealed.answer_text == ""
        assert sealed.predicted_tool_calls == ()
        assert sealed.failure is False

    def test_failure_flag_from_terminal_classification(self):
        artifact = SealedL2Artifact(
            artifact_id="a2",
            trace_id="t2",
            terminal_classification=TerminalClassification.FAILURE,
        )
        sealed = shadow_observer.sealed_l2_to_eval_spine(artifact)
        assert sealed.failure is True

    def test_tool_calls_filtered_to_canonical_shape(self):
        artifact = SealedL2Artifact(
            artifact_id="a3",
            trace_id="t3",
            exec_trace={
                "tool_calls": [
                    {"tool": "search", "args_hash": "h1"},
                    {"tool": "broken"},  # missing args_hash — dropped
                    "not a dict",  # dropped
                    {"tool": "", "args_hash": "h2"},  # empty tool — dropped
                    {"tool": "summarize", "args_hash": "h3"},
                ]
            },
        )
        sealed = shadow_observer.sealed_l2_to_eval_spine(artifact)
        tools = [call["tool"] for call in sealed.predicted_tool_calls]
        assert tools == ["search", "summarize"]

    def test_exec_trace_numeric_fields(self):
        artifact = SealedL2Artifact(
            artifact_id="a4",
            trace_id="t4",
            exec_trace={
                "retry_count": 2,
                "latency_ms": 1250,
                "tokens": 500,
                "cost_usd": 0.015,
                "tenant": "acme",
                "agent_class": "ResumeAgent",
            },
        )
        sealed = shadow_observer.sealed_l2_to_eval_spine(artifact)
        assert sealed.retry_count == 2
        assert sealed.latency_ms == 1250
        assert sealed.tokens_consumed == 500
        assert sealed.cost_usd_consumed == pytest.approx(0.015)
        assert sealed.tenant == "acme"
        assert sealed.agent_class == "ResumeAgent"

    def test_conversion_never_raises_on_bad_input(self):
        # Mypy/runtime abuse: malformed exec_trace values (e.g. None)
        artifact = SealedL2Artifact(
            artifact_id="a5",
            trace_id="t5",
            exec_trace={
                "retry_count": None,
                "latency_ms": None,
                "tokens": None,
                "cost_usd": None,
                "tool_calls": None,
            },
        )
        sealed = shadow_observer.sealed_l2_to_eval_spine(artifact)
        assert sealed.retry_count == 0
        assert sealed.latency_ms == 0
        assert sealed.predicted_tool_calls == ()


class TestEmitShadowExitDecision:
    def test_flag_off_returns_none(self, tmp_path: Path):
        artifact = SealedL2Artifact(artifact_id="a", trace_id="t")
        result = shadow_observer.emit_shadow_exit_decision(artifact, output_root=tmp_path)
        assert result is None
        assert list(tmp_path.iterdir()) == []

    def test_flag_on_writes_artifact(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("EVAL_SPINE_SHADOW", "1")
        artifact = SealedL2Artifact(
            artifact_id="req-99",
            trace_id="tr-99",
            exec_trace={"latency_ms": 100, "tokens": 30},
        )
        path = shadow_observer.emit_shadow_exit_decision(
            artifact, policy_snapshot="sha-ok", output_root=tmp_path
        )
        assert path is not None
        assert path.exists()
        assert path.name == "tr-99.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["trace_id"] == "tr-99"
        assert payload["request_id"] == "req-99"
        assert payload["policy_snapshot"] == "sha-ok"

    def test_exception_is_swallowed(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("EVAL_SPINE_SHADOW", "1")
        # Point output_root at a path that cannot be created (parent is a file).
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        bad_root = blocker / "subdir"
        artifact = SealedL2Artifact(artifact_id="a", trace_id="t")
        # Must not raise; returns None.
        result = shadow_observer.emit_shadow_exit_decision(artifact, output_root=bad_root)
        assert result is None


class TestExitControlGateHook:
    """Ensure the observer does not perturb ExitControlGate.evaluate_sealed."""

    def _make_gate(self):
        from agentic_core.L5_safety.enforcement.exit_control_gate import (
            ExitControlGate,
        )

        return ExitControlGate(policy_hash="sha-hook-test")

    def _make_artifact(self):
        return SealedL2Artifact(
            artifact_id="hook-1",
            trace_id="hook-trace-1",
            validation_counters=ValidationCounters(),
        )

    def test_flag_off_no_disruption(self, tmp_path: Path, monkeypatch):
        # No EVAL_SPINE_SHADOW → existing behavior unchanged.
        monkeypatch.setattr(shadow_observer, "_DEFAULT_OUTPUT_ROOT", tmp_path)
        gate = self._make_gate()
        result = gate.evaluate_sealed(self._make_artifact())
        assert result.trace_id == "hook-trace-1"
        # No artifact file written.
        assert list(tmp_path.iterdir()) == []

    def test_flag_on_writes_shadow_file(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("EVAL_SPINE_SHADOW", "1")
        monkeypatch.setattr(shadow_observer, "_DEFAULT_OUTPUT_ROOT", tmp_path)
        gate = self._make_gate()
        result = gate.evaluate_sealed(self._make_artifact())
        # Live decision returned as usual.
        assert result.trace_id == "hook-trace-1"
        # Shadow file written under the patched output root.
        shadow_path = tmp_path / "hook-trace-1.json"
        assert shadow_path.exists()
        payload = json.loads(shadow_path.read_text(encoding="utf-8"))
        assert payload["trace_id"] == "hook-trace-1"
        assert payload["policy_snapshot"] == "sha-hook-test"
