"""Tests for post_agent_work_classification_audit (plan-reflex Stop-chain auditor)."""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = REPO_ROOT / ".claude" / "governance/scripts" / "post_agent_work_classification_audit.py"


@pytest.fixture()
def wc_mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import importlib.util

    name = "_post_agent_work_classification_audit_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "VIOLATIONS_FILE", tmp_path / "work_classification_violations.jsonl")
    monkeypatch.delenv("WORK_CLASSIFICATION_AUDIT_BYPASS", raising=False)
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


class TestPostAgentWorkClassificationAudit:
    def test_bypass_returns_zero(self, wc_mod, monkeypatch) -> None:
        monkeypatch.setenv("WORK_CLASSIFICATION_AUDIT_BYPASS", "1")
        assert _run(wc_mod, "I'll create a new plan file for this bug.", monkeypatch) == 0
        assert _rows(wc_mod) == []

    def test_empty_response_is_noop(self, wc_mod, monkeypatch) -> None:
        assert _run(wc_mod, "   ", monkeypatch) == 0
        assert _rows(wc_mod) == []

    def test_suppressed_when_plan_mint_ok(self, wc_mod, monkeypatch) -> None:
        text = "PLAN_MINT_OK=1 — I'll create a new plan for the multi-wave migration."
        assert _run(wc_mod, text, monkeypatch) == 0
        assert _rows(wc_mod) == []

    def test_suppressed_for_master_gap_inventory(self, wc_mod, monkeypatch) -> None:
        text = "Logging this as a Master Gap Inventory row instead of minting a plan."
        assert _run(wc_mod, text, monkeypatch) == 0
        assert _rows(wc_mod) == []

    def test_logs_plan_creation_reflex(self, wc_mod, monkeypatch, capsys) -> None:
        text = "I'll create a new plan for this one-line typo fix."
        assert _run(wc_mod, text, monkeypatch) == 0
        rows = _rows(wc_mod)
        assert len(rows) == 1
        assert rows[0]["kind"] == "plan_creation_reflex"
        assert "plan-creation intent phrase" in rows[0]["label"]
        assert "work-classification" in capsys.readouterr().err

    def test_detects_new_plan_slug_reference(self, wc_mod, monkeypatch) -> None:
        text = "Next step: write plans/fix-typo-a1b2c3.md for the regression."
        assert _run(wc_mod, text, monkeypatch) == 0
        rows = _rows(wc_mod)
        assert len(rows) == 1
        assert rows[0]["label"] == "new plan slug reference"

    def test_clean_response_no_violation(self, wc_mod, monkeypatch) -> None:
        text = "Fixed directly in foo.py; no plan artifact needed."
        assert _run(wc_mod, text, monkeypatch) == 0
        assert _rows(wc_mod) == []
