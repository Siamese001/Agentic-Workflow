"""Tandem enforcement: a plan must exist on disk (SSOT) AND in Notion, fail-closed by default.

Locks the 2026-06-08 Author-Gate decision (full fail-closed, both directions):
- pre_notion_plan_creation_gate: blocks a Plans-DB post-page when the real disk file is absent.
- check_plan_registration_freshness: fail-closed by DEFAULT (opt out with =0).
- pre_notion_plan_write_gate: identity mismatch blocks by DEFAULT (opt out with =0).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[3]


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # register so @dataclass introspection (sys.modules[__module__]) works
    spec.loader.exec_module(mod)
    return mod


CREATION = _load(".claude/governance/scripts/pre_notion_plan_creation_gate.py", "tandem_creation_gate")
FRESH = _load("ops_scripts/ci/check_plan_registration_freshness.py", "tandem_freshness")
WRITE = _load(".claude/governance/scripts/pre_notion_plan_write_gate.py", "tandem_write_gate")


def _payload(slug: str) -> dict:
    return {
        "properties": {
            "Slug": {"title": [{"text": {"content": slug}}]},
            "Status": {"select": {"name": "Not Started"}},
            "Summary": {"rich_text": []},
            "AI Summary ": {"rich_text": []},
            "Exists On Disk": {"checkbox": True},
        }
    }


# ----------------------------------------------------- creation gate: real disk file
def test_creation_blocks_when_disk_file_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(CREATION, "REPO_ROOT", tmp_path)
    ok, errors = CREATION._check_payload(_payload("ghost-plan-abc123"))
    assert ok is False
    assert any("disk file missing" in e.lower() for e in errors)


def test_creation_allows_when_repo_root_plans_file_present(monkeypatch, tmp_path):
    monkeypatch.setattr(CREATION, "REPO_ROOT", tmp_path)
    (tmp_path / "plans").mkdir()
    (tmp_path / "plans" / "real-plan-abc123.md").write_text("# plan", encoding="utf-8")
    ok, errors = CREATION._check_payload(_payload("real-plan-abc123"))
    assert ok is True, errors


def test_creation_allows_legacy_claude_plans_file(monkeypatch, tmp_path):
    monkeypatch.setattr(CREATION, "REPO_ROOT", tmp_path)
    (tmp_path / ".claude" / "plans").mkdir(parents=True)
    (tmp_path / ".claude" / "plans" / "legacy-plan-abc123.md").write_text("# plan", encoding="utf-8")
    ok, _ = CREATION._check_payload(_payload("legacy-plan-abc123"))
    assert ok is True


# ----------------------------------------------------- freshness: fail-closed default
def test_freshness_fail_closed_by_default(monkeypatch):
    monkeypatch.delenv("PLAN_REGISTRATION_FAIL_CLOSED", raising=False)
    assert FRESH._fail_closed() is True


def test_freshness_advisory_opt_out(monkeypatch):
    for v in ("0", "false", "no", "NO"):
        monkeypatch.setenv("PLAN_REGISTRATION_FAIL_CLOSED", v)
        assert FRESH._fail_closed() is False
    monkeypatch.setenv("PLAN_REGISTRATION_FAIL_CLOSED", "1")
    assert FRESH._fail_closed() is True


# ----------------------------------------------------- identity gate: fail-closed default
def _mismatch_query(*_a, **_k):
    return {"id": "correct-page", "properties": {"Slug": {"title": [{"text": {"content": "x"}}]}}}


def test_identity_fail_closed_by_default(monkeypatch):
    monkeypatch.delenv("NOTION_PLAN_IDENTITY_FAIL_CLOSED", raising=False)
    monkeypatch.delenv("NOTION_PLAN_IDENTITY_BYPASS", raising=False)
    with mock.patch.object(WRITE, "_query_notion_plans_db", side_effect=_mismatch_query):
        assert WRITE.run_gate("x", "wrong-page") == 2


def test_identity_advisory_opt_out(monkeypatch):
    monkeypatch.setenv("NOTION_PLAN_IDENTITY_FAIL_CLOSED", "0")
    monkeypatch.delenv("NOTION_PLAN_IDENTITY_BYPASS", raising=False)
    with mock.patch.object(WRITE, "_query_notion_plans_db", side_effect=_mismatch_query):
        assert WRITE.run_gate("x", "wrong-page") == 0
