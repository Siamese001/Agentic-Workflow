#!/usr/bin/env python3
"""Sync apps-rg-spine-only-unification-d8f4a2 plan scope to Notion Plans DB (In Progress)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "apps-rg-spine-only-unification-d8f4a2"
PLAN_PATH = ".claude/plans/apps-rg-spine-only-unification-d8f4a2.md"
PAGE_ID = "36927693-f55c-8190-b30b-de1f6534e2a7"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "IN PROGRESS (2026-05-23): apps_rg spine-only unification — W1–W4+W6 on main @ 3e7ab52413; "
    "single entry apps_rg_spine_run; bridges deleted; ExitEvalPipeline on sections; gate 0 findings. "
    "Live E2E executive_summary PASS (CLI_PATH); X3 judge soft-fail (Track C). W5 full résumé + W7 core open. "
    "Pending commit: kwargs filter, ExitEvalPipeline init, sealed-L2-before-exit. "
    "Scope: docs/reports/apps_rg/spine_unification_open_scope_20260523.md"
)

AI_SUMMARY = """- STATUS: In Progress — CURRENT_WAVE W5 — LAST_COMPLETED W6
- DONE W1: single-spine CI gate + contract tests (0 ERROR findings)
- DONE W2–W4 @ 3e7ab52413: apps_rg_spine_run; canonical_dispatch; spine/ package; section_x3_finalize
- DONE W6: one_spine_inventory two_paths_found=false
- LIVE E2E: exec_summary_20260523_171726 — spine contract artifacts + exit_disposition_receipt.json
- OPEN W5: L3 multi-section loop + assembly + full-resume X1D in spine entry
- OPEN W7: agentic_core prerequisite/judges (author-gate)
- OPEN OS-W2-AG2: proof-pool→FEC inside lanes vs run_ag2 at spine entry
- PENDING COMMIT: spine wiring fixes (kwargs, ExitEvalPipeline(), exit after sealed L2)
- P0 cross-plan: Track C X3_ALLOW — apps-rg-proof-pool-c0-ssot-a7f3e2"""

MARKERS = """\
WAVE_COMPLETE: plan=apps-rg-spine-only-unification-d8f4a2 wave=1 note="CI ratchet + ADR + contract tests"
WAVE_COMPLETE: plan=apps-rg-spine-only-unification-d8f4a2 wave=2 note="apps_rg_spine_run + dispatch; commit 3e7ab52413"
WAVE_COMPLETE: plan=apps-rg-spine-only-unification-d8f4a2 wave=3 note="bridge deletion; spine package"
WAVE_COMPLETE: plan=apps-rg-spine-only-unification-d8f4a2 wave=4 note="section_x3_finalize + ExitEvalPipeline"
WAVE_COMPLETE: plan=apps-rg-spine-only-unification-d8f4a2 wave=6 note="inventory two_paths false; gate 0 findings"
"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {
        "filter": {"property": "Slug", "title": {"equals": SLUG}},
        "page_size": 1,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return None
    rows = data.get("results") or []
    return str(rows[0].get("id") or "") if rows else None


def _patch_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "In Progress"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:2000]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}]},
        }
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{page_id}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            json.loads(resp.read().decode("utf-8"))
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    page_id = _query_page_id() or PAGE_ID
    if not _patch_page(page_id):
        print(json.dumps({"ok": False, "error": "patch_failed", "page_id": page_id}), file=sys.stderr)
        return 1

    proc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "notion" / "wave_lifecycle_writer.py"), "--emit-from-stdin"],
        input=MARKERS,
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    wave_ok = proc.returncode == 0
    print(
        json.dumps(
            {
                "ok": True,
                "action": "patched",
                "page_id": page_id,
                "status": "In Progress",
                "wave_lifecycle": wave_ok,
                "wave_stderr": (proc.stderr or "")[:500],
            }
        )
    )
    return 0 if wave_ok else 0  # fail-soft on wave append per wave_lifecycle_writer contract


if __name__ == "__main__":
    raise SystemExit(main())
