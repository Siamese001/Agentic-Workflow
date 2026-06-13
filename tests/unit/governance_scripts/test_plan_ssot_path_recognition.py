"""Regression: plan-governance hooks must recognize the canonical repo-root ``plans/``
SSOT location (relocation c1a17d), not only legacy ``.claude/plans/``.

Locks RCA 2026-06-08 Option B so the disk→Notion reconcile/registration fires for
plans written to repo-root ``plans/``. Guards against reverting to ``.claude/plans/``-only.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HELPER = REPO / ".claude" / "governance" / "scripts" / "_plan_registration.py"
RECONCILE_HOOK = REPO / ".claude" / "governance" / "scripts" / "post_write_plan_reconcile.py"
AFTER_FILE_EDIT = REPO / ".claude" / "hooks" / "after_file_edit.py"
CAPTURE = REPO / ".claude" / "governance" / "scripts" / "post_agent_plan_registration_capture.py"
RECONCILE_LOG = REPO / "artifacts" / "governance" / "plan_reconcile_hook.jsonl"


def _load_helper():
    spec = importlib.util.spec_from_file_location("_plan_registration_test", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- shared helper
def test_helper_canonical_plan_path_is_repo_root():
    m = _load_helper()
    slug = f"zzregtest-{uuid.uuid4().hex[:6]}"  # not on disk anywhere → canonical
    assert m.plan_file_path(slug) == f"plans/{slug}.md"


def test_helper_plan_file_re_is_location_agnostic():
    m = _load_helper()
    assert m.PLAN_FILE_RE.match("some-plan-abc123.md")
    assert not m.PLAN_FILE_RE.match("not-a-plan.md")


# ---------------------------------------------------------- post_write_plan_reconcile (real subprocess)
def _reconcile_triggers(parent_relpath: str) -> bool:
    name = f"zzssotreg-{uuid.uuid4().hex[:6]}.md"
    file_path = f"{parent_relpath}/{name}"
    env = {**os.environ, "NOTION_TOKEN": "", "POST_WRITE_PLAN_RECONCILE_BYPASS": ""}
    subprocess.run(
        [sys.executable, str(RECONCILE_HOOK)],
        input=json.dumps({"tool_info": {"file_path": file_path}}),
        text=True, cwd=str(REPO), env=env, timeout=30, check=False,
    )
    if not RECONCILE_LOG.exists():
        return False
    for line in reversed(RECONCILE_LOG.read_text(encoding="utf-8").splitlines()[-100:]):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("event") == "triggered" and rec.get("plan") == name:
            return True
    return False


def test_reconcile_recognizes_repo_root_and_legacy_plans():
    assert _reconcile_triggers("plans") is True              # canonical repo-root
    assert _reconcile_triggers(".claude/plans") is True      # legacy still valid


def test_reconcile_excludes_reports_and_non_plan_dirs():
    assert _reconcile_triggers("docs/reports/plans") is False  # reports/ excluded
    assert _reconcile_triggers("apps_rg/runtime") is False     # parent != "plans"


# ---------------------------------------------------------- source guards (import-side-effecting hooks)
def test_after_file_edit_recognizes_repo_root_plans():
    src = AFTER_FILE_EDIT.read_text(encoding="utf-8")
    assert "_is_active_plan_file" in src
    assert 'startswith("plans/")' in src or "startswith('plans/')" in src, (
        "after_file_edit must accept repo-root plans/ (relocation c1a17d)"
    )


def test_capture_default_path_is_repo_root_plans():
    # The marker-capture default path lives in the shared helper; assert it is canonical.
    m = _load_helper()
    slug = f"zzregtest-{uuid.uuid4().hex[:6]}"
    assert m.plan_file_path(slug).startswith("plans/")
    # and the capture script docstring/contract references plans/<slug>.md, not .claude/plans/
    src = CAPTURE.read_text(encoding="utf-8")
    assert "plans/<slug>.md" in src and ".claude/plans/<slug>.md" not in src
