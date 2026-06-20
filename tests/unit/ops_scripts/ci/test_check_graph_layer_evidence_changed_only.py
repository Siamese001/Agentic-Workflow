"""Tests for the diff-scoped mode of check_graph_layer_evidence (--changed-only).

A pre-existing non-compliant plan that this PR did NOT touch must not fail the gate. Only plans
changed vs the base ref are evaluated in --changed-only mode; the full whole-repo scan remains the
default (and the git-unavailable fallback).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_graph_layer_evidence.py"
_spec = importlib.util.spec_from_file_location("check_graph_layer_evidence_mod", _GATE_PATH)
assert _spec and _spec.loader
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

_NONCOMPLIANT_PLAN = """---
plan_type: refactor
---

# Some refactor plan

This plan declares a refactoring intent but carries no graph-layer evidence sections.
"""


@pytest.fixture
def fake_repo(tmp_path, monkeypatch):
    plans = tmp_path / ".codex" / "plans"
    plans.mkdir(parents=True)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "PLANS_DIR", plans)
    monkeypatch.setattr(mod, "BASELINE_FILE", tmp_path / "baseline.json")
    monkeypatch.setattr(mod, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "logs" / "graph_layer_violations.jsonl")
    monkeypatch.setattr(mod, "_PLAN_INTEGRITY_ROOTS", (plans,))
    return tmp_path, plans


# ----------------------------- _select_changed_plan_paths ----------------------------- #


class TestSelectChangedPlanPaths:
    def test_keeps_top_level_plan_md(self, fake_repo):
        _, plans = fake_repo
        (plans / "foo.md").write_text("x", encoding="utf-8")
        out = mod._select_changed_plan_paths([".codex/plans/foo.md"])
        assert out == [plans / "foo.md"]

    def test_ignores_non_plan_paths_and_missing_files(self, fake_repo):
        _, plans = fake_repo
        (plans / "real.md").write_text("x", encoding="utf-8")
        out = mod._select_changed_plan_paths(
            [".codex/plans/real.md", "tools/x.py", ".codex/plans/deleted.md", "README.md"]
        )
        assert out == [plans / "real.md"]  # non-plan + nonexistent dropped

    def test_excludes_readme_template(self, fake_repo):
        _, plans = fake_repo
        (plans / "README.md").write_text("x", encoding="utf-8")
        assert mod._select_changed_plan_paths([".codex/plans/README.md"]) == []


# ----------------------------- main(--changed-only) ----------------------------- #


class TestChangedOnlyMode:
    def test_unchanged_bad_plan_is_ignored(self, fake_repo, monkeypatch):
        """THE key case: a non-compliant plan exists on disk but this PR changed nothing → PASS."""
        _, plans = fake_repo
        (plans / "preexisting-bad.md").write_text(_NONCOMPLIANT_PLAN, encoding="utf-8")
        monkeypatch.setattr(mod, "_changed_plan_files", lambda base_ref: [])  # nothing changed
        assert mod.main(["--changed-only", "--base-ref", "main"]) == 0

    def test_changed_bad_plan_fails(self, fake_repo, monkeypatch):
        _, plans = fake_repo
        (plans / "touched-bad.md").write_text(_NONCOMPLIANT_PLAN, encoding="utf-8")
        monkeypatch.setattr(
            mod, "_changed_plan_files", lambda base_ref: [".codex/plans/touched-bad.md"]
        )
        assert mod.main(["--changed-only", "--base-ref", "main"]) == 1

    def test_git_unavailable_falls_back_to_full_scan(self, fake_repo, monkeypatch):
        """If git can't resolve the base, do NOT pass silently — fall back to the full scan."""
        _, plans = fake_repo
        (plans / "preexisting-bad.md").write_text(_NONCOMPLIANT_PLAN, encoding="utf-8")
        monkeypatch.setattr(mod, "_changed_plan_files", lambda base_ref: None)  # git unavailable
        assert mod.main(["--changed-only", "--base-ref", "main"]) == 1  # full scan catches it

    def test_full_scan_default_still_evaluates_all(self, fake_repo):
        _, plans = fake_repo
        (plans / "preexisting-bad.md").write_text(_NONCOMPLIANT_PLAN, encoding="utf-8")
        assert mod.main([]) == 1  # no --changed-only → whole-repo scan → fails on the bad plan


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
