"""Unit tests for plan→SSOT path handling.

Covers:
  - before_file_edit_branch_guard._is_plan_file (plans/** exempt from worktree isolation)

(The `_plan_registration.canonical_plans_dir` resolver tests were removed with the
windsurf/cursor-era plan-registration pipeline — notion-wave-enforcement-removal.)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GUARD_PATH = REPO_ROOT / ".claude" / "hooks" / "before_file_edit_branch_guard.py"


def _load(mod_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(mod_name, None)
        raise
    return mod


class TestIsPlanFile:
    def setup_method(self):
        self.guard = _load("_branch_guard_under_test", GUARD_PATH)

    def test_repo_root_plan_is_plan_file(self):
        assert self.guard._is_plan_file("C:/Git/Agentic-Workflow-FRESH/plans/foo-abc123.md")
        assert self.guard._is_plan_file("plans/foo-abc123.md")

    def test_legacy_claude_plans_is_plan_file(self):
        assert self.guard._is_plan_file(".claude/plans/legacy-abc123.md")
        assert self.guard._is_plan_file("C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\legacy-abc123.md")

    def test_archived_plan_is_not_exempt(self):
        # Archives must not be silently editable — fall through to the branch guard.
        assert not self.guard._is_plan_file("plans/_archive/2026-05/old-abc123.md")
        assert not self.guard._is_plan_file(".claude/plans/_archive/old-abc123.md")

    def test_non_plan_paths_are_not_plan_files(self):
        assert not self.guard._is_plan_file("agentic_core/x.py")
        assert not self.guard._is_plan_file("docs/reports/plans/report-abc123.md")  # parent != 'plans'
        assert not self.guard._is_plan_file("plans/notes.txt")  # not .md
        assert not self.guard._is_plan_file("")
