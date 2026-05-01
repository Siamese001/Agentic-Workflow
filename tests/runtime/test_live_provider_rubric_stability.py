"""W2b regression test — rubric-stability probe report must be JSON-serializable.

Precedent: on 2026-05-01 the first live-provider Scenario A run against
Qwen/Qwen2.5-32B-Instruct-AWQ crashed at Step 2/9 because the probe emitted
``result.error`` directly into its run dict. ``VetoResult.error`` is a
classmethod factory on ``tools.certification.safety.veto_protocol.VetoResult``,
not a field, so ``json.dumps(report)`` raised
``TypeError: Object of type method is not JSON serializable``. Scenario A
could not progress until the probe was fixed.

This test locks the fix by running _single_run against a stub
LLMJudgeVeto whose ``evaluate()`` returns a real ``VetoResult`` — the
attribute shape that caused the bug. If the probe regresses to reading
``.error`` (or any other method attribute) the test fails with the same
``TypeError`` signature.

Plan: .windsurf/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md § 7 (P2).
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence import probe_live_provider_rubric_stability as P  # noqa: E402
from tools.certification.safety.veto_protocol import VetoResult, VetoStatus  # noqa: E402


def _make_stub_veto(status: VetoStatus, rationale: str = ""):
    """Build a minimal object with the .evaluate() contract P relies on."""

    def evaluate(**kwargs):
        return VetoResult(
            status=status,
            stage_name="llm_judge_local_qwen",
            confidence=0.9 if status == VetoStatus.SAFE else 0.0,
            rationale=rationale or f"stub-{status.name}",
            metadata={"raw": f"stub-raw-{status.name}"},
            latency_ms=42.0,
        )

    stub = types.SimpleNamespace(evaluate=evaluate)
    return stub


class TestRunDictIsJsonSerializable:
    """Probe's per-run dict must round-trip through json.dumps()."""

    def test_safe_run_serializes(self):
        stub = _make_stub_veto(VetoStatus.SAFE)
        run = P._single_run(stub, run_idx=1)
        # Must not raise
        encoded = json.dumps(run, sort_keys=True)
        # Fields that matter for the rest of the chain
        assert run["verdict"] == "SAFE"
        assert run["is_error"] is False
        assert run["error_message"] == ""
        assert run["stage_name"] == "llm_judge_local_qwen"
        assert "error" not in run, (
            "Field `error` must NOT be surfaced directly from VetoResult — "
            "it is a classmethod factory, not a field. Use `is_error` + "
            "`error_message` instead."
        )
        # Round-trip sanity
        decoded = json.loads(encoded)
        assert decoded["is_error"] is False

    def test_error_run_serializes(self):
        stub = _make_stub_veto(VetoStatus.ERROR, rationale="timeout after 10s")
        run = P._single_run(stub, run_idx=1)
        # Must not raise
        json.dumps(run, sort_keys=True)
        assert run["verdict"] == "ERROR"
        assert run["is_error"] is True
        assert run["error_message"] == "timeout after 10s"


class TestFullReportIsJsonSerializable:
    """The full stability report must serialize — this is the path that crashed."""

    def test_full_report_through_json_dumps(self, monkeypatch):
        stub = _make_stub_veto(VetoStatus.SAFE)

        # Patch LLMJudgeVeto constructor to return our stub
        def fake_ctor(provider, temperature=0.0, **kwargs):
            s = stub
            s.is_available = lambda: True
            return s

        monkeypatch.setattr(P, "LLMJudgeVeto", fake_ctor)

        report = P.run_stability_probe("local_qwen")
        # The exact call-site that failed on 2026-05-01:
        encoded = json.dumps(report, indent=2, sort_keys=True)
        assert encoded  # non-empty
        # Schema-v1 required fields
        assert report["schema_version"] == 1
        assert report["provider"] == "local_qwen"
        assert report["available"] is True
        assert len(report["runs"]) == P.NUM_RUNS
        assert "stability" in report
        for run in report["runs"]:
            assert "is_error" in run
            assert "error" not in run


class TestVetoTimeoutBudget:
    """W2B_VETO_TIMEOUT_MS env override must propagate to both the
    stability PASS threshold AND the veto's internal request timeout.

    Precedent: 2026-05-01 Scenario A run against 32B AWQ timed out at
    every run because DEFAULT_TIMEOUT_MS=2000 was tighter than the
    model's ~7.5s response latency. Hardcoded budgets are not
    certifiable when the target model changes.
    """

    def test_default_budget_is_10s(self, monkeypatch):
        # Module-level constant captures env at import time; reload to
        # re-evaluate after clearing the override.
        import importlib
        monkeypatch.delenv("W2B_VETO_TIMEOUT_MS", raising=False)
        importlib.reload(P)
        assert P.STABILITY_TIMEOUT_MS == 10000

    def test_env_override_raises_budget(self, monkeypatch):
        import importlib
        monkeypatch.setenv("W2B_VETO_TIMEOUT_MS", "15000")
        importlib.reload(P)
        assert P.STABILITY_TIMEOUT_MS == 15000
        # Restore default for other tests
        monkeypatch.delenv("W2B_VETO_TIMEOUT_MS", raising=False)
        importlib.reload(P)

    def test_veto_receives_matching_timeout(self, monkeypatch):
        """run_stability_probe must pass the same budget to LLMJudgeVeto
        that it uses in _evaluate_stability — otherwise the veto times
        out before reaching the probe's PASS threshold."""
        import importlib
        monkeypatch.setenv("W2B_VETO_TIMEOUT_MS", "12000")
        importlib.reload(P)

        captured = {}
        orig_ctor = P.LLMJudgeVeto

        def fake_ctor(**kwargs):
            captured.update(kwargs)
            inst = orig_ctor.__new__(orig_ctor)
            inst.__init__(**kwargs)
            # Force unavailable so we do not actually hit an endpoint
            inst.is_available = lambda: False
            return inst

        monkeypatch.setattr(P, "LLMJudgeVeto", fake_ctor)
        P.run_stability_probe("local_qwen")
        assert captured.get("timeout_ms") == 12000, (
            f"run_stability_probe must pass timeout_ms=STABILITY_TIMEOUT_MS "
            f"to LLMJudgeVeto; got {captured.get('timeout_ms')!r}"
        )
        monkeypatch.delenv("W2B_VETO_TIMEOUT_MS", raising=False)
        importlib.reload(P)


class TestEvaluateStabilityHandlesNewSchema:
    """_evaluate_stability must use the new is_error / error_message fields."""

    def test_error_run_flagged_via_is_error(self):
        runs = [
            {"run_index": 1, "verdict": "SAFE", "confidence": 0.9,
             "latency_ms": 100.0, "raw_response_sha256": "abc",
             "is_error": False, "error_message": ""},
            {"run_index": 2, "verdict": "ERROR", "confidence": 0.0,
             "latency_ms": 100.0, "raw_response_sha256": None,
             "is_error": True, "error_message": "timeout"},
            {"run_index": 3, "verdict": "SAFE", "confidence": 0.9,
             "latency_ms": 100.0, "raw_response_sha256": "abc",
             "is_error": False, "error_message": ""},
        ]
        stab = P._evaluate_stability(runs)
        assert stab["pass"] is False
        # "provider errors present" SHOULD appear in failure_reasons
        assert any("errors present" in r for r in stab["failure_reasons"])

    def test_all_safe_no_errors_passes(self):
        runs = [
            {"run_index": i, "verdict": "SAFE", "confidence": 0.9,
             "latency_ms": 100.0, "raw_response_sha256": "abc",
             "is_error": False, "error_message": ""}
            for i in range(1, P.NUM_RUNS + 1)
        ]
        stab = P._evaluate_stability(runs)
        assert stab["pass"] is True
        assert stab["failure_reasons"] == []
