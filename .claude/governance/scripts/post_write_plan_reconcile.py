#!/usr/bin/env python3
"""
post_write_plan_reconcile.py — Cursor post_write_code hook wrapper.

Runs plan_driven_closer.py scoped to a SINGLE plan file, ONLY when Cursor Agent
just edited a file under .claude/plans/*.md. Any other write → immediate
exit 0 (no Notion query, no work).

This keeps pre-commit CI light: Notion reconciliation fires only when a plan
is actually edited, not on every code commit, and is bounded to the single
affected plan (no full-repo sweep).

Reads JSON payload from stdin. Payload fields (same shape as post_write_audit):
    tool_info.file_path  — path of file that was written

Fail policy: OPEN — any error → exit 0 silently.
Bypass:      POST_WRITE_PLAN_RECONCILE_BYPASS=1
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_LOG = REPO_ROOT / "artifacts" / "governance" / "plan_reconcile_hook.jsonl"
CLOSER_SCRIPT = REPO_ROOT / ".claude" / "governance/scripts" / "plan_driven_closer.py"


def _log(record: dict) -> None:
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        record.setdefault("ts", datetime.now(timezone.utc).isoformat())
        with AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- hook audit log: fail-open
        pass


def main() -> int:
    if os.environ.get("POST_WRITE_PLAN_RECONCILE_BYPASS") == "1":
        return 0

    # Read payload
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_info = payload.get("tool_info") or {}
    file_path = str(tool_info.get("file_path") or "").replace("\\", "/")

    if not file_path:
        return 0

    # Fast bail-out: only plan files trigger reconciliation.
    # Forward-only relocation (c1a17d): accept canonical plans/ AND legacy
    # .claude/plans/. A plan file is a *.md whose parent dir is named "plans"
    # and is not under a reports/ tree.
    _pp = Path(file_path)
    if not (
        file_path.endswith(".md")
        and _pp.parent.name == "plans"
        and "reports" not in _pp.parts
    ):
        return 0

    plan_filename = Path(file_path).name
    _log({"event": "triggered", "plan": plan_filename})

    # NOTION_TOKEN required — silently skip if missing
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        _log({"event": "skip_no_token"})
        return 0

    # Run scoped reconciliation
    try:
        result = subprocess.run(
            [sys.executable, str(CLOSER_SCRIPT), "--plan", plan_filename, "--execute"],
            cwd=REPO_ROOT,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        _log(
            {
                "event": "reconcile_done",
                "plan": plan_filename,
                "returncode": result.returncode,
                "stdout_tail": (result.stdout or "").splitlines()[-3:],
                "stderr_tail": (result.stderr or "").splitlines()[-3:],
            }
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        _log({"event": "reconcile_error", "plan": plan_filename, "error": str(exc)})

    return 0  # always fail-open


if __name__ == "__main__":
    sys.exit(main())
