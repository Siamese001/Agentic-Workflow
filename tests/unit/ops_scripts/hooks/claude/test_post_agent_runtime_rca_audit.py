"""Tests for the post-agent runtime-RCA audit (constitutional §37).

Mirrors the importlib + stdin convention used by test_post_agent_long_command_audit.py.
The audit exposes module-level ``VIOLATIONS_FILE`` (monkeypatched to tmp_path) and a
``main()`` that reads stdin and always returns 0 (advisory, fail-open).
"""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = REPO_ROOT / ".claude" / "governance/scripts" / "post_agent_runtime_rca_audit.py"


@pytest.fixture()
def rca_mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import importlib.util

    name = "_post_agent_runtime_rca_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "VIOLATIONS_FILE", tmp_path / "runtime_rca_violations.jsonl")
    monkeypatch.delenv("RUNTIME_RCA_AUDIT_BYPASS", raising=False)
    return mod


def _run(mod, response_text: str, monkeypatch: pytest.MonkeyPatch) -> int:
    payload = json.dumps({"tool_info": {"response": response_text}})
    monkeypatch.setattr(sys, "stdin", StringIO(payload))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    return mod.main()


def _rows(mod) -> list[dict]:
    log = mod.VIOLATIONS_FILE
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").strip().splitlines()]


_FULL_RCA = (
    "RCA:\n"
    "- symptom: `python -m apps_rg` lane ibm_bullets -> X3_BLOCK on metric anchor\n"
    "- root_cause: stale literal-token anchor rule [DIRECTLY OBSERVED]\n"
    "- evidence: artifacts/w2_b0/terminal_ret_packet.json\n"
    "- fix_or_next: graph-determined ownership in ibm_bullets_generator.py\n"
    "- recurrence_guard: test_ibm_bullets.py::test_held_metric_not_anchored\n"
)

# A refactoring turn = code files changed (or an edit tool invoked). Per the contract it
# must carry the Outcome frame ("Did it pass?") on every turn, so the failing-refactor
# fixtures below include it and exercise the Layered-RCA depth checks.
_REFACTOR_HEADER = (
    "**Outcome**\n"
    "Did it run? Yes.  Did it pass? No.\n"
    "Verdict source: python -m pytest -> exit 1\n"
    "STATUS: FAIL\n"
    "FILES_CHANGED:\n- [foo.py](foo.py)\n"
    "COMMANDS_RUN:\n- python -m pytest -> exit 1\n"
)

# Deep Layered RCA: failing layer isolated, multi-level why-chain, root != symptom.
_DEEP_LAYERED_RCA = (
    "**Layered RCA**\n"
    "Immediate symptom: apps_eval exit 1, verdict fail, outputs missing\n"
    "Failing layer: live apps_rg runtime, not the L6 observer that surfaced it\n"
    "why1: competencies lane failed before resume sections materialized\n"
    "why2: the LLMOps bundle binding was absent from the graph\n"
    "Mechanism: competencies failed first -> downstream PHASE1_PRIOR_LANE_FAILED\n"
    "Root cause: preflight admitted an under-specified fixture into full lane execution\n"
    "Evidence: artifacts/ae_rg_live/eval_record.json\n"
    "Confidence / unknowns: failure location confirmed; final fix needs a rerun\n"
)

# Shallow RCA: 5-field-complete but no layered descent (symptom straight to a vague root).
_SHALLOW_RCA = (
    "RCA:\n"
    "- symptom: the tests fail\n"
    "- root_cause: there is a bug in the code\n"
    "- evidence: artifacts/log.txt\n"
    "- fix_or_next: fix the bug\n"
)

# Symptom restated as the root cause (no real descent), with layer+mechanism present.
_SYMPTOM_EQ_ROOT_RCA = (
    "**Layered RCA**\n"
    "Immediate symptom: competencies lane X3_BLOCK\n"
    "Failing layer: apps_rg runtime\n"
    "Mechanism: the lane failed\n"
    "Root cause: competencies lane X3_BLOCK\n"
    "Evidence: artifacts/log.json\n"
    "Confidence: high\n"
)


class TestRuntimeRcaAudit:
    def test_not_applicable_no_status_line(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _run(rca_mod, "Just prose. Nothing ran. No receipt here.", monkeypatch) == 0
        assert _rows(rca_mod) == []

    def test_clean_pass_no_signal(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = "STATUS: PASS\nCOMMANDS_RUN:\n- pytest x -> 5 passed\n"
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []

    def test_clean_fail_with_full_rca(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = "STATUS: FAIL\nCOMMANDS_RUN:\n- run -> X3_BLOCK\n" + _FULL_RCA
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []  # FAIL is not "green", and RCA is complete

    def test_violation_fail_no_rca(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = "STATUS: FAIL\nCOMMANDS_RUN:\n- run -> X3_BLOCK on lane competencies\n"
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        kinds = {r["kind"] for r in rows}
        assert "missing_rca" in kinds
        assert "status_signal_mismatch" not in kinds  # FAIL is not green

    def test_violation_signal_no_rca(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = (
            "STATUS: FAIL\nTESTS_GATES:\n- pytest -> 2 failed\n"
            "Traceback (most recent call last):\n  File ...\nAssertionError\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        assert any(r["kind"] == "missing_rca" for r in rows)
        signals = rows[0]["failure_signals"]
        assert "pytest_failed" in signals and "python_traceback" in signals

    def test_violation_incomplete_rca(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = (
            "STATUS: FAIL\nCOMMANDS_RUN:\n- run -> exit 1\n"
            "RCA:\n- symptom: it broke\n- root_cause: unclear\n"  # no evidence / fix_or_next
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        assert any(r["kind"] == "incomplete_rca" for r in rows)
        assert not any(r["kind"] == "missing_rca" for r in rows)

    def test_violation_green_theater(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # PASS over a body failure signal, but WITH a complete RCA -> isolates the
        # status_signal_mismatch kind (no missing_rca).
        text = "STATUS: PASS\nCOMMANDS_RUN:\n- run -> X3_BLOCK\n" + _FULL_RCA
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        kinds = {r["kind"] for r in rows}
        assert "status_signal_mismatch" in kinds
        assert "missing_rca" not in kinds  # RCA is present and complete

    def test_refactor_clean_deep_layered_rca(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = _REFACTOR_HEADER + _DEEP_LAYERED_RCA
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []  # deep descent on a refactor failure = compliant

    def test_refactor_shallow_rca_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = _REFACTOR_HEADER + _SHALLOW_RCA  # 5-field complete but no layered descent
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        shallow = [r for r in rows if r["kind"] == "shallow_rca"]
        assert shallow, f"expected shallow_rca, got {[r['kind'] for r in rows]}"
        assert shallow[0]["refactor_turn"] is True
        assert shallow[0]["descent_depth"] < 2
        assert not any(r["kind"] in ("missing_rca", "incomplete_rca") for r in rows)

    def test_refactor_symptom_equals_root_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = _REFACTOR_HEADER + _SYMPTOM_EQ_ROOT_RCA  # descent depth ok, but root == symptom
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        shallow = [r for r in rows if r["kind"] == "shallow_rca"]
        assert shallow, f"expected shallow_rca, got {[r['kind'] for r in rows]}"
        assert shallow[0]["symptom_equals_root"] is True

    def test_non_refactor_shallow_rca_ok(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # Same shallow RCA but NOT a refactor turn (no code files changed) -> no shallow_rca.
        text = "STATUS: FAIL\nCOMMANDS_RUN:\n- run -> exit 1\n" + _SHALLOW_RCA
        assert _run(rca_mod, text, monkeypatch) == 0
        assert not any(r["kind"] == "shallow_rca" for r in _rows(rca_mod))

    def test_refactor_pass_missing_outcome_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # A PASSING refactor turn reported with the bare STATUS floor (no Outcome frame).
        text = "STATUS: PASS\nFILES_CHANGED:\n- [foo.py](foo.py)\nCOMMANDS_RUN:\n- pytest -> 5 passed\n"
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        assert any(r["kind"] == "missing_refactor_outcome" for r in rows), [r["kind"] for r in rows]
        assert rows[0]["refactor_turn"] is True
        assert rows[0]["has_outcome_frame"] is False

    def test_refactor_pass_with_outcome_clean(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # A PASSING refactor turn that DOES carry the Outcome frame -> compliant.
        text = (
            "**Outcome**\nDid it run? Yes.  Did it pass? Yes.\n"
            "Verdict source: pytest -> 5 passed\n"
            "STATUS: PASS\nFILES_CHANGED:\n- [foo.py](foo.py)\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []

    def test_refactor_fail_missing_outcome_subsumes_rca(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # A FAILING refactor turn with neither the Outcome frame nor an RCA -> the single
        # missing_refactor_outcome violation (it subsumes missing_rca).
        text = "STATUS: FAIL\nFILES_CHANGED:\n- [foo.py](foo.py)\nCOMMANDS_RUN:\n- run -> X3_BLOCK\n"
        assert _run(rca_mod, text, monkeypatch) == 0
        kinds = {r["kind"] for r in _rows(rca_mod)}
        assert "missing_refactor_outcome" in kinds
        assert "missing_rca" not in kinds  # subsumed

    def test_bypass(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RUNTIME_RCA_AUDIT_BYPASS", "1")
        text = "STATUS: FAIL\nCOMMANDS_RUN:\n- run -> X3_BLOCK\n"  # would violate without bypass
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []


class TestAfterAgentChainRegistration:
    def test_runtime_rca_registered_in_chain(self) -> None:
        hook = REPO_ROOT / ".claude" / "hooks" / "after_agent_governance_dispatch.py"
        text = hook.read_text(encoding="utf-8")
        assert '"post_agent_runtime_rca_audit.py"' in text
        # registered after the work-classification audit
        assert text.rindex("post_agent_work_classification_audit.py") < text.rindex(
            "post_agent_runtime_rca_audit.py"
        )
