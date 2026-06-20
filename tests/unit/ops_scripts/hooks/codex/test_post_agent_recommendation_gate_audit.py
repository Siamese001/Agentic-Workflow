"""Tests for the post-agent recommendation-trigger audit.

Advisory detector: flags a decision/options menu surfaced in prose without an AskUserQuestion.
Mirrors the importlib + stdin convention of the sibling post_agent audit tests.
"""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = REPO_ROOT / ".codex" / "governance/scripts" / "post_agent_recommendation_gate_audit.py"


@pytest.fixture()
def gate_mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import importlib.util

    name = "_post_agent_recommendation_gate_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "VIOLATIONS_FILE", tmp_path / "recommendation_gate_violations.jsonl")
    monkeypatch.delenv("RECOMMENDATION_GATE_BYPASS", raising=False)
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


class TestRecommendationGateAudit:
    def test_lettered_or_menu_flagged(self, gate_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = "Want me to (a) push the branch or (b) implement the gate now?"
        assert _run(gate_mod, text, monkeypatch) == 0
        rows = _rows(gate_mod)
        assert any(r["kind"] == "recommendation_not_gated" for r in rows)
        assert "lettered_or_menu" in rows[0]["patterns"]

    def test_bold_option_menu_flagged(self, gate_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = "Here are the choices.\n**Option A** — merge now\n**Option B** — open a PR\n"
        assert _run(gate_mod, text, monkeypatch) == 0
        assert any(r["kind"] == "recommendation_not_gated" for r in _rows(gate_mod))

    def test_prose_decision_question_flagged(self, gate_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = "Looks done. Should I merge to main or open a PR for review?"
        assert _run(gate_mod, text, monkeypatch) == 0
        assert any(r["kind"] == "recommendation_not_gated" for r in _rows(gate_mod))

    def test_askuserquestion_used_is_compliant(self, gate_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        # The confidence marker proves an AskUserQuestion was posed -> suppress.
        text = (
            "I'll ask.\nOption A (Recommended) [RECOMMENDED ⭐ confidence=0.70] merge now\n"
            "Do you want A or B?"
        )
        assert _run(gate_mod, text, monkeypatch) == 0
        assert _rows(gate_mod) == []

    def test_normal_prose_not_flagged(self, gate_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = "STATUS: PASS\nThe migration is complete; tests pass and the gate is green."
        assert _run(gate_mod, text, monkeypatch) == 0
        assert _rows(gate_mod) == []

    def test_bypass(self, gate_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RECOMMENDATION_GATE_BYPASS", "1")
        text = "Want me to (a) merge or (b) PR?"
        assert _run(gate_mod, text, monkeypatch) == 0
        assert _rows(gate_mod) == []


class TestWiredIntoChain:
    def test_registered_in_ag_chain(self) -> None:
        hook = REPO_ROOT / ".codex" / "hooks" / "after_agent_governance_dispatch.py"
        text = hook.read_text(encoding="utf-8")
        assert '"post_agent_recommendation_gate_audit.py"' in text
