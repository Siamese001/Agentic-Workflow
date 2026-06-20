"""Tests for the W2 hook fail-open ledger + budget gate.

Covers (claude-enforcement-runtime-truth-hardening W2):
  * lib.codex_hook_common.write_failopen_receipt — schema, non-dict payload, write-failure
    must not raise (a receipt failure can never wedge a fail-open hook).
  * before_ask_user_question — self-contained inline fail-open receipt when the gate is missing.
  * ops_scripts/ci/check_hook_failopen_budget.py — critical_target_missing, critical_failopen
    regression-vs-baseline, advisory=warn, and advisory/fail-closed/bypass exit semantics.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOKS_DIR = REPO_ROOT / ".codex" / "hooks"
CHC_PATH = HOOKS_DIR / "lib" / "codex_hook_common.py"
ASK_HOOK = HOOKS_DIR / "before_ask_user_question.py"
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_hook_failopen_budget.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------- #
# write_failopen_receipt
# --------------------------------------------------------------------------- #

class TestWriteFailopenReceipt:
    @pytest.fixture()
    def chc(self, monkeypatch, tmp_path):
        mod = _load("_chc_failopen_test", CHC_PATH)
        monkeypatch.setattr(mod, "_FAILOPEN_RECEIPT_LOG", tmp_path / "failopen.jsonl")
        return mod

    def test_writes_expected_row(self, chc) -> None:
        chc.write_failopen_receipt("beforeGrep", {"session_id": "s9"}, "pre_grep_gate_script_missing", "absent", chc.CRIT_PRETOOL)
        rows = _rows(chc._FAILOPEN_RECEIPT_LOG)
        assert len(rows) == 1
        r = rows[0]
        assert r["hook"] == "beforeGrep"
        assert r["failure_class"] == "pre_grep_gate_script_missing"
        assert r["criticality"] == "CRITICAL_PRETOOL"
        assert r["session_id"] == "s9"
        assert r["ts"]  # timestamp present

    def test_non_dict_payload_yields_blank_session(self, chc) -> None:
        chc.write_failopen_receipt("h", "not a dict", "fc", "why", chc.ADVISORY_CAPTURE)
        assert _rows(chc._FAILOPEN_RECEIPT_LOG)[0]["session_id"] == ""

    def test_write_failure_does_not_raise(self, chc, tmp_path) -> None:
        # Point the log under a path whose parent is a FILE so mkdir(parents=True) fails.
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        chc._FAILOPEN_RECEIPT_LOG = blocker / "nested" / "failopen.jsonl"
        # Must not raise despite the unwritable path.
        chc.write_failopen_receipt("h", {}, "fc", "why", chc.CRIT_PRETURN)


# --------------------------------------------------------------------------- #
# before_ask_user_question — self-contained inline receipt
# --------------------------------------------------------------------------- #

class TestAskUserQuestionInlineReceipt:
    def test_missing_gate_writes_failopen_receipt(self, monkeypatch, tmp_path) -> None:
        mod = _load("_ask_hook_failopen_test", ASK_HOOK)
        monkeypatch.setattr(mod, "_GATE", tmp_path / "absent_gate.py")
        monkeypatch.setattr(mod, "_FAILOPEN_RECEIPT_LOG", tmp_path / "failopen.jsonl")
        monkeypatch.setattr(sys, "stdin", StringIO(json.dumps({"session_id": "aq1"})))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        assert mod.main() == 0  # fail-open
        rows = _rows(mod._FAILOPEN_RECEIPT_LOG)
        assert len(rows) == 1
        assert rows[0]["hook"] == "beforeAskUserQuestion"
        assert rows[0]["failure_class"] == "ask_rec_gate_script_missing"
        assert rows[0]["criticality"] == "CRITICAL_PRETOOL"
        assert rows[0]["session_id"] == "aq1"


# --------------------------------------------------------------------------- #
# check_hook_failopen_budget.py
# --------------------------------------------------------------------------- #

class TestBudgetGate:
    @pytest.fixture()
    def gate(self, monkeypatch, tmp_path):
        mod = _load("_hook_failopen_budget_test", GATE_PATH)
        # Default: clean settings (one existing critical hook), empty ledger, no baseline.
        settings = tmp_path / "hooks.json"
        settings.write_text(
            json.dumps(
                {"hooks": {"PreToolUse": [{"matcher": "Grep", "hooks": [{"type": "command", "command": 'python "$AGENTIC_REPO_ROOT/.codex/hooks/before_grep.py"'}]}]}}
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(mod, "SETTINGS", settings)
        monkeypatch.setattr(mod, "LEDGER", tmp_path / "ledger.jsonl")
        monkeypatch.setattr(mod, "BASELINE", tmp_path / "baseline.json")
        monkeypatch.delenv("HOOK_FAILOPEN_BUDGET_FAIL_CLOSED", raising=False)
        monkeypatch.delenv("HOOK_FAILOPEN_BUDGET_BYPASS", raising=False)
        return mod

    def _write_ledger(self, mod, *rows: dict) -> None:
        mod.LEDGER.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    def test_clean_is_ok(self, gate) -> None:
        result = gate.evaluate()
        assert result["errors"] == []

    def test_critical_target_missing_errors(self, gate) -> None:
        gate.SETTINGS.write_text(
            json.dumps(
                {"hooks": {"PreToolUse": [{"matcher": "X", "hooks": [{"type": "command", "command": 'python "$AGENTIC_REPO_ROOT/.codex/hooks/does_not_exist.py"'}]}]}}
            ),
            encoding="utf-8",
        )
        errors = gate.evaluate()["errors"]
        assert any("critical_target_missing" in e for e in errors)

    def test_critical_failopen_regression_over_baseline(self, gate) -> None:
        self._write_ledger(
            gate,
            {"hook": "beforeGrep", "criticality": "CRITICAL_PRETOOL", "failure_class": "x"},
            {"hook": "beforeGrep", "criticality": "CRITICAL_PRETOOL", "failure_class": "x"},
        )
        errors = gate.evaluate()["errors"]
        assert any("critical_failopen_regression" in e for e in errors)

    def test_baseline_acknowledges_known_failopen(self, gate) -> None:
        self._write_ledger(gate, {"hook": "beforeGrep", "criticality": "CRITICAL_PRETOOL", "failure_class": "x"})
        gate.BASELINE.write_text(json.dumps({"critical_per_hook": {"beforeGrep": 1}}), encoding="utf-8")
        assert gate.evaluate()["errors"] == []

    def test_advisory_failopen_is_warn_not_error(self, gate) -> None:
        self._write_ledger(gate, {"hook": "beforeSubmitPrompt", "criticality": "ADVISORY_CAPTURE", "failure_class": "x"})
        result = gate.evaluate()
        assert result["errors"] == []
        assert any("advisory_failopen" in w for w in result["warns"])

    def test_main_advisory_exit_zero_even_with_errors(self, gate) -> None:
        self._write_ledger(gate, {"hook": "beforeGrep", "criticality": "CRITICAL_PRETOOL", "failure_class": "x"})
        assert gate.main([]) == 0  # advisory default never blocks

    def test_main_fail_closed_exit_one(self, gate, monkeypatch) -> None:
        self._write_ledger(gate, {"hook": "beforeGrep", "criticality": "CRITICAL_PRETOOL", "failure_class": "x"})
        monkeypatch.setenv("HOOK_FAILOPEN_BUDGET_FAIL_CLOSED", "1")
        assert gate.main([]) == 1

    def test_main_bypass_exit_zero(self, gate, monkeypatch) -> None:
        self._write_ledger(gate, {"hook": "beforeGrep", "criticality": "CRITICAL_PRETOOL", "failure_class": "x"})
        monkeypatch.setenv("HOOK_FAILOPEN_BUDGET_FAIL_CLOSED", "1")
        monkeypatch.setenv("HOOK_FAILOPEN_BUDGET_BYPASS", "1")
        assert gate.main([]) == 0  # bypass wins

    def test_init_writes_baseline(self, gate) -> None:
        self._write_ledger(gate, {"hook": "beforeGrep", "criticality": "CRITICAL_PRETOOL", "failure_class": "x"})
        assert gate.main(["--init"]) == 0
        data = json.loads(gate.BASELINE.read_text(encoding="utf-8"))
        assert data["critical_per_hook"]["beforeGrep"] == 1
