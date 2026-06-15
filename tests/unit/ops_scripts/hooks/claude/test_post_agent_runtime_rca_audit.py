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
# must carry the Outcome frame (keyed on "Verdict source:") on every turn, so the
# failing-refactor fixtures below include it and exercise the Layered-RCA depth checks.
# The frame proves the STATUS verdict; it no longer re-votes with "Did it pass?".
_REFACTOR_HEADER = (
    "**Outcome**\n"
    "Did it run? Yes.\n"
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

# A common reusable deep body: real descent, failing layer isolated, root != symptom.
# Variants below add/remove the confidence line and the next-step line to isolate the two
# new high-confidence / coupled-next-step triggers without tripping the depth or distinctness
# checks.
_DEEP_BODY = (
    "**Layered RCA**\n"
    "Immediate symptom: apps_eval exit 1, outputs missing\n"
    "Failing layer: live apps_rg runtime, not the L6 observer that surfaced it\n"
    "why1: competencies lane failed before resume sections materialized\n"
    "why2: the LLMOps bundle binding was absent from the graph\n"
    "Mechanism: competencies failed first -> PHASE1_PRIOR_LANE_FAILED\n"
    "Root cause: preflight admitted an under-specified fixture into full lane execution\n"
    "Evidence: artifacts/ae_rg_live/eval_record.json\n"
)
_CONFIDENCE_LINE = "Confidence / unknowns: failure location confirmed; final fix needs a rerun\n"
_COUPLED_NEXT_LINE = "Next: add a fixture-completeness assertion in apps_rg preflight\n"

# Deep descent but the root cause is asserted with NO stated confidence -> shallow_rca.
_DEEP_NO_CONFIDENCE = _DEEP_BODY + _COUPLED_NEXT_LINE
# Deep descent + confidence, but the next step is a bare platitude -> shallow_rca.
_DEEP_GENERIC_NEXT = _DEEP_BODY + _CONFIDENCE_LINE + "Next: fix the bug\n"
# Deep descent + confidence + a next step coupled to the diagnosis -> compliant.
_DEEP_FULL_CLEAN = _DEEP_BODY + _CONFIDENCE_LINE + _COUPLED_NEXT_LINE


class TestRuntimeRcaAudit:
    def test_not_applicable_no_status_line(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _run(rca_mod, "Just prose. Nothing ran. No receipt here.", monkeypatch) == 0
        assert _rows(rca_mod) == []

    def test_clean_pass_no_signal(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- NONE\n"
            "COMMANDS_RUN:\n- pytest x -> 5 passed\n"
            "TESTS_GATES:\n- pytest x -> 5 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
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

    def test_refactor_root_cause_without_confidence_flagged(
        self, rca_mod, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Deep descent, failing layer isolated, root != symptom, coupled next step — but the
        # root cause is asserted with NO stated confidence. "High confidence" must be claimed,
        # not implied, so this is shallow_rca via the missing_confidence trigger alone.
        text = _REFACTOR_HEADER + _DEEP_NO_CONFIDENCE
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        shallow = [r for r in rows if r["kind"] == "shallow_rca"]
        assert shallow, f"expected shallow_rca, got {[r['kind'] for r in rows]}"
        r = shallow[0]
        assert r["missing_confidence"] is True
        # isolation: the other triggers must NOT be what fired
        assert r["descent_depth"] >= 2
        assert r["symptom_equals_root"] is False
        assert r["missing_failing_layer"] is False
        assert r["next_step_generic"] is False

    def test_refactor_generic_next_step_flagged(
        self, rca_mod, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Deep descent + stated confidence, but the next step is a bare platitude ("fix the
        # bug") — decoupled from the diagnosis above it. shallow_rca via next_step_generic alone.
        text = _REFACTOR_HEADER + _DEEP_GENERIC_NEXT
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        shallow = [r for r in rows if r["kind"] == "shallow_rca"]
        assert shallow, f"expected shallow_rca, got {[r['kind'] for r in rows]}"
        r = shallow[0]
        assert r["next_step_generic"] is True
        # isolation: depth/distinctness/confidence are all fine here
        assert r["descent_depth"] >= 2
        assert r["symptom_equals_root"] is False
        assert r["missing_failing_layer"] is False
        assert r["missing_confidence"] is False

    def test_refactor_deep_confidence_coupled_next_clean(
        self, rca_mod, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The full contract: deep why-chain, isolated failing layer, root != symptom, stated
        # confidence, AND a next step coupled to the root cause -> no violation.
        text = _REFACTOR_HEADER + _DEEP_FULL_CLEAN
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_non_refactor_shallow_rca_ok(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # Same shallow RCA but NOT a refactor turn (no code files changed) -> no shallow_rca.
        text = "STATUS: FAIL\nCOMMANDS_RUN:\n- run -> exit 1\n" + _SHALLOW_RCA
        assert _run(rca_mod, text, monkeypatch) == 0
        assert not any(r["kind"] == "shallow_rca" for r in _rows(rca_mod))

    def test_refactor_pass_missing_outcome_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # A PASSING refactor turn reported with the bare STATUS floor (no Outcome frame).
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> 5 passed\n"
            "TESTS_GATES:\n- pytest -> 5 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        miss = next((r for r in rows if r["kind"] == "missing_refactor_outcome"), None)
        assert miss is not None, [r["kind"] for r in rows]
        assert miss["refactor_turn"] is True
        assert miss["has_outcome_frame"] is False

    def test_refactor_pass_with_outcome_clean(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # A PASSING refactor turn that DOES carry the Outcome frame -> compliant.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: pytest -> 5 passed\n"
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> 5 passed\n"
            "TESTS_GATES:\n- pytest -> 5 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []

    def test_refactor_frame_sentinel_is_verdict_source_not_passvote(
        self, rca_mod, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Consolidation (one verdict): the frame proves the STATUS verdict via "Verdict source:"
        # and no longer re-votes with "Did it pass?". A passing refactor turn carrying the frame
        # with NO "Did it pass?" line anywhere is fully compliant.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: python -m pytest foo -> exit 0, 5 passed\n"
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- python -m pytest foo -> exit 0\n"
            "TESTS_GATES:\n- python -m pytest foo -> 5 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert "Did it pass" not in text  # the re-vote is gone
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_refactor_outcome_without_verdict_source_flagged(
        self, rca_mod, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The sentinel is the runtime-evidence anchor: an Outcome header + "Did it run?" but
        # NO "Verdict source:" line does not satisfy the frame -> missing_refactor_outcome.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "STATUS: PASS\nFILES_CHANGED:\n- [foo.py](foo.py)\nCOMMANDS_RUN:\n- pytest -> 5 passed\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        kinds = {r["kind"] for r in _rows(rca_mod)}
        assert "missing_refactor_outcome" in kinds, kinds

    def test_refactor_legacy_passvote_without_verdict_source_flagged(
        self, rca_mod, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Clean break: the legacy "Did it pass?" line is no longer the frame sentinel. Without
        # a "Verdict source:" line the frame is not recognized -> missing_refactor_outcome.
        text = (
            "**Outcome**\nDid it run? Yes.  Did it pass? Yes.\n"
            "STATUS: PASS\nFILES_CHANGED:\n- [foo.py](foo.py)\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        kinds = {r["kind"] for r in _rows(rca_mod)}
        assert "missing_refactor_outcome" in kinds, kinds

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

    def test_missing_response_floor_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # A repo-work turn (files changed) that wrapped up in prose with NO STATUS floor — the
        # dominant format-drift mode the rule-001 § Canonical post-turn output section exists to stop.
        text = "Committed the fix and pushed.\nFILES_CHANGED:\n- [foo.py](foo.py)\n"
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        floor = [r for r in rows if r["kind"] == "missing_response_floor"]
        assert floor, [r["kind"] for r in rows]
        assert floor[0]["status"] == "NONE"
        assert "files_changed" in floor[0]["repo_work_signals"]

    def test_pure_prose_still_clean(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # No STATUS line AND no floor signal -> a question / non-repo turn stays clean (guards the
        # missing_response_floor check against false positives on ordinary prose answers).
        text = "Here's how the router works: it picks an arm, then logs the decision. No edits made."
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []

    def test_adg_run_exempt_from_missing_floor(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # An ADG generate/audit run carries its OWN burndown + gates output contract that supersedes
        # the floor (rule 001 § Canonical post-turn output, point 4). Even with a floor signal and no
        # STATUS line it must NOT be flagged missing_response_floor — the ADG burndown audit owns it.
        text = (
            "Ran `python tools/generate_full_adg.py`. ADG generated.\n"
            "ARTIFACTS:\n- [adg_burndown_report.md](artifacts/adg/adg_burndown_report.md)\n"
            "| Gate ID | Band | Verdict |\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []

    def test_adg_run_exempt_from_outcome_frame(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # generate_full_adg runs are governed ONLY by the BCG burndown contract — even a refactor-style
        # ADG turn (code file changed + STATUS:PASS, no Outcome frame) must NOT be flagged
        # missing_refactor_outcome. The whole runtime-rca audit defers to the ADG burndown gate.
        text = (
            "Regenerated the graph via `python tools/generate_full_adg.py`.\n"
            "STATUS: PASS\nFILES_CHANGED:\n- [phase_c.py](tools/generate/phase_c.py)\n"
            "COMMANDS_RUN:\n- python tools/generate_full_adg.py -> exit 0\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == []




class TestStatusMatrix:
    """Full status×refactor matrix — verifies that every valid combination is clean
    and that the two new kinds fire only on the right shapes."""

    # ── REFACTOR TURNS (FILES_CHANGED has a .py, or edit tool present) ────────

    def test_refactor_pass_with_outcome_and_all_proof_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: pytest -> 7 passed\n"
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> 7 passed\n"
            "TESTS_GATES:\n- pytest -> 7 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_refactor_partial_with_outcome_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: pytest -> 3 passed, 2 deferred\n"
            "STATUS: PARTIAL\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> 3 passed\n"
            "TESTS_GATES:\n- pytest -> 3 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_refactor_fail_with_deep_rca_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        # Full contract: Outcome frame + deep why-chain + isolated layer + confidence + coupled next.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: python -m pytest -> exit 1, 2 failed\n"
            "STATUS: FAIL\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- python -m pytest -> exit 1\n"
            "TESTS_GATES:\n- python -m pytest -> 2 failed\n"
            "ARTIFACTS:\n- NONE\n"
            "**Layered RCA**\n"
            "Immediate symptom: lane ibm_bullets X3_BLOCK on metric anchor\n"
            "Failing layer: ibm_bullets_generator.py literal match, not the ibm_narrative that surfaced it\n"
            "why1: the anchor token was a stale literal, not a graph-sourced fact ID\n"
            "why2: ibm_bullets_graph_evidence.py was not updated when fact IDs were renamed\n"
            "Mechanism: stale literal match -> X3_BLOCK -> PHASE1 cascade\n"
            "Root cause: ibm_bullets_graph_evidence.py retained the old fact-ID literals after rename\n"
            "Evidence: artifacts/w2_b0/terminal_ret_packet.json shows bul_ibm_003 not in graph\n"
            "Confidence / unknowns: root cause DIRECTLY OBSERVED; fix path clear\n"
            "Next: rename fact IDs in ibm_bullets_graph_evidence.py to match current graph snapshot\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_refactor_blocked_no_edit_tool_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        # BLOCKED: no files changed, no edit tool → not a refactor turn; no Outcome frame needed.
        text = (
            "STATUS: BLOCKED\n"
            "COMMANDS_RUN:\n- N/A — missing ANTHROPIC_API_KEY\n"
            "TESTS_GATES:\n- N/A\n"
            "ARTIFACTS:\n- NONE\n"
            "NOTES:\n- Cannot proceed until provider key is set.\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    # ── NON-REFACTOR TURNS (no code files, no edit tool) ─────────────────────

    def test_non_refactor_pass_all_proof_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- NONE\n"
            "COMMANDS_RUN:\n- pytest -> 10 passed\n"
            "TESTS_GATES:\n- pytest -> 10 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_non_refactor_partial_no_signals_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        text = (
            "STATUS: PARTIAL\n"
            "COMMANDS_RUN:\n- pytest -> 3 passed, 2 deferred\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_non_refactor_fail_with_rca_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        text = (
            "STATUS: FAIL\n"
            "COMMANDS_RUN:\n- run -> X3_BLOCK\n"
            "RCA:\n"
            "- symptom: lane ibm_bullets X3_BLOCK\n"
            "- root_cause: stale literal anchor [DIRECTLY OBSERVED]\n"
            "- evidence: artifacts/terminal_ret_packet.json\n"
            "- fix_or_next: update anchor in ibm_bullets_graph_evidence.py\n"
            "- recurrence_guard: test_ibm_bullets_anchor.py\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    def test_non_refactor_blocked_no_signals_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        text = (
            "STATUS: BLOCKED\n"
            "COMMANDS_RUN:\n- N/A\n"
            "ARTIFACTS:\n- NONE\n"
            "NOTES:\n- Missing provider key; cannot run E2E.\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]

    # ── VIOLATION PATHS ────────────────────────────────────────────────────────

    def test_refactor_pass_no_outcome_frame_flags(
        self, rca_mod, monkeypatch
    ) -> None:
        # PASS refactor without Outcome frame → missing_refactor_outcome.
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- [bar.py](bar.py)\n"
            "COMMANDS_RUN:\n- pytest -> 5 passed\n"
            "TESTS_GATES:\n- pytest -> 5 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        kinds = {r["kind"] for r in _rows(rca_mod)}
        assert "missing_refactor_outcome" in kinds, kinds

    def test_pass_missing_files_changed_flags(
        self, rca_mod, monkeypatch
    ) -> None:
        # PASS with FILES_CHANGED absent → pass_without_proof.
        text = (
            "STATUS: PASS\n"
            "COMMANDS_RUN:\n- pytest -> 5 passed\n"
            "TESTS_GATES:\n- pytest -> 5 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        hit = next((r for r in rows if r["kind"] == "pass_without_proof"), None)
        assert hit is not None, [r["kind"] for r in rows]
        assert "FILES_CHANGED" in hit["missing_proof"]
        assert "COMMANDS_RUN" not in hit["missing_proof"]

    def test_refactor_fail_shallow_rca_flags(
        self, rca_mod, monkeypatch
    ) -> None:
        # Refactor FAIL: 5-field RCA only (no Layered depth) → shallow_rca.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: pytest -> exit 1\n"
            "STATUS: FAIL\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> exit 1\n"
            "RCA:\n"
            "- symptom: the tests fail\n"
            "- root_cause: there is a bug in the code\n"
            "- evidence: artifacts/log.txt\n"
            "- fix_or_next: fix the bug\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        kinds = {r["kind"] for r in _rows(rca_mod)}
        assert "shallow_rca" in kinds, kinds
        assert "missing_rca" not in kinds
        assert "missing_refactor_outcome" not in kinds

    def test_refactor_fail_missing_confidence_flags(
        self, rca_mod, monkeypatch
    ) -> None:
        # Deep descent, isolated layer, distinct root, coupled next — but NO stated confidence.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: pytest -> exit 1\n"
            "STATUS: FAIL\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> exit 1\n"
        ) + _DEEP_NO_CONFIDENCE
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        shallow = [r for r in rows if r["kind"] == "shallow_rca"]
        assert shallow, [r["kind"] for r in rows]
        assert shallow[0]["missing_confidence"] is True
        assert shallow[0]["descent_depth"] >= 2

    def test_refactor_fail_generic_next_step_flags(
        self, rca_mod, monkeypatch
    ) -> None:
        # Deep descent + confidence, but next = "fix the bug" → shallow_rca.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: pytest -> exit 1\n"
            "STATUS: FAIL\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> exit 1\n"
        ) + _DEEP_GENERIC_NEXT
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        shallow = [r for r in rows if r["kind"] == "shallow_rca"]
        assert shallow, [r["kind"] for r in rows]
        assert shallow[0]["next_step_generic"] is True

    def test_refactor_fail_full_rca_all_dimensions_clean(
        self, rca_mod, monkeypatch
    ) -> None:
        # All 5 shallow_rca triggers absent: ≥2 why levels, isolated layer,
        # root ≠ symptom, stated confidence, coupled next step → no violations.
        text = (
            "**Outcome**\nDid it run? Yes.\n"
            "Verdict source: pytest -> exit 1\n"
            "STATUS: FAIL\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> exit 1\n"
        ) + _DEEP_FULL_CLEAN
        assert _run(rca_mod, text, monkeypatch) == 0
        assert _rows(rca_mod) == [], [r["kind"] for r in _rows(rca_mod)]


class TestProofContractKinds:
    def test_pass_missing_proof_section_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # STATUS:PASS without all four proof sections -> pass_without_proof.
        text = "STATUS: PASS\nCOMMANDS_RUN:\n- pytest -> 5 passed\n"  # missing FILES/TESTS/ARTIFACTS
        assert _run(rca_mod, text, monkeypatch) == 0
        rows = _rows(rca_mod)
        hit = next((r for r in rows if r["kind"] == "pass_without_proof"), None)
        assert hit is not None, [r["kind"] for r in rows]
        assert "FILES_CHANGED" in hit["missing_proof"]
        assert "TESTS_GATES" in hit["missing_proof"]
        assert "ARTIFACTS" in hit["missing_proof"]
        assert "COMMANDS_RUN" not in hit["missing_proof"]  # COMMANDS_RUN IS present

    def test_pass_all_proof_sections_clean(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # STATUS:PASS with all four sections present -> no violation.
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- NONE\n"
            "COMMANDS_RUN:\n- pytest -> 5 passed\n"
            "TESTS_GATES:\n- pytest -> 5 passed\n"
            "ARTIFACTS:\n- NONE\n"
        )
        assert _run(rca_mod, text, monkeypatch) == 0
        assert not any(r["kind"] == "pass_without_proof" for r in _rows(rca_mod))

    def test_speculative_should_pass_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # "should pass" language on a repo-work turn -> speculative_pass.
        text = "STATUS: PARTIAL\nCOMMANDS_RUN:\n- run -> in progress\nThese tests should pass now.\n"
        assert _run(rca_mod, text, monkeypatch) == 0
        kinds = {r["kind"] for r in _rows(rca_mod)}
        assert "speculative_pass" in kinds, kinds

    def test_speculative_likely_pass_flagged(self, rca_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # "likely pass" language on a repo-work turn -> speculative_pass.
        text = "STATUS: PARTIAL\nCOMMANDS_RUN:\n- run -> in progress\nThis will likely pass on next run.\n"
        assert _run(rca_mod, text, monkeypatch) == 0
        kinds = {r["kind"] for r in _rows(rca_mod)}
        assert "speculative_pass" in kinds, kinds


class TestAfterAgentChainRegistration:
    def test_runtime_rca_registered_in_chain(self) -> None:
        hook = REPO_ROOT / ".claude" / "hooks" / "after_agent_governance_dispatch.py"
        text = hook.read_text(encoding="utf-8")
        assert '"post_agent_runtime_rca_audit.py"' in text
        # registered after the work-classification audit
        assert text.rindex("post_agent_work_classification_audit.py") < text.rindex(
            "post_agent_runtime_rca_audit.py"
        )
