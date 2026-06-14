"""Tests for the ``missing_plan_persistence`` check in post_agent_work_classification_audit.

The auditor flags genuinely multi-wave EXECUTION that left no minted
plans/<slug>-<6hex>.md SSOT plan (plan-persistence-discipline 2026-06-14, RCA: ADR-104).
Advisory + fail-open. Mirrors the importlib + stdin convention of the sibling audits.
"""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / ".claude" / "governance/scripts" / "post_agent_work_classification_audit.py"


@pytest.fixture()
def mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import importlib.util

    name = "_post_agent_work_classification_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    monkeypatch.setattr(m, "VIOLATIONS_FILE", tmp_path / "work_classification_violations.jsonl")
    monkeypatch.delenv("WORK_CLASSIFICATION_AUDIT_BYPASS", raising=False)
    return m


def _run(mod, response_text: str, monkeypatch: pytest.MonkeyPatch) -> int:
    payload = json.dumps({"tool_info": {"response": response_text}})
    monkeypatch.setattr(sys, "stdin", StringIO(payload))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    return mod.main()


def _kinds(mod) -> list[str]:
    log = mod.VIOLATIONS_FILE
    if not log.exists():
        return []
    return [json.loads(line)["kind"] for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


# Multi-wave execution narrative with NO minted plan path.
_MULTIWAVE_EXEC = (
    "W1(removal): unwired the hooks.\nW2(removal): deleted the scripts.\n"
    "W3(removal): deleted the gates.\nSTATUS: PASS\nFILES_CHANGED:\n- a.py\n- b.py\n"
    "Committed and pushed to main."
)


def test_multiwave_execution_without_plan_flags(mod, monkeypatch):
    assert _run(mod, _MULTIWAVE_EXEC, monkeypatch) == 0
    assert "missing_plan_persistence" in _kinds(mod)


def test_minted_plan_reference_suppresses(mod, monkeypatch):
    text = _MULTIWAVE_EXEC + "\nSaved to plans/notion-removal-e4d8b2.md."
    assert _run(mod, text, monkeypatch) == 0
    assert "missing_plan_persistence" not in _kinds(mod)


def test_plan_mint_ok_suppresses(mod, monkeypatch):
    text = _MULTIWAVE_EXEC + "\nPLAN_MINT_OK=1 authorized."
    assert _run(mod, text, monkeypatch) == 0
    assert "missing_plan_persistence" not in _kinds(mod)


def test_no_execution_evidence_not_flagged(mod, monkeypatch):
    # Mentions waves but is pure planning/discussion (no FILES_CHANGED / STATUS / commit).
    text = "The plan has W1, W2 and W3. I will think about W1 first."
    assert _run(mod, text, monkeypatch) == 0
    assert "missing_plan_persistence" not in _kinds(mod)


def test_single_wave_not_flagged(mod, monkeypatch):
    text = "W1(fix): one small change.\nSTATUS: PASS\nFILES_CHANGED:\n- a.py"
    assert _run(mod, text, monkeypatch) == 0
    assert "missing_plan_persistence" not in _kinds(mod)


def test_detect_helper_direct(mod):
    assert mod._detect_unpersisted_multiwave(_MULTIWAVE_EXEC) is not None
    assert mod._detect_unpersisted_multiwave(_MULTIWAVE_EXEC).__class__ is int
    assert mod._detect_unpersisted_multiwave("plans/x-a1b2c3.md\n" + _MULTIWAVE_EXEC) is None
    assert mod._detect_unpersisted_multiwave("just prose, no waves") is None
