#!/usr/bin/env python3
"""Mark adg-action-dispatch-c9e4a2 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "adg-action-dispatch-c9e4a2"
PLAN_PATH = ".claude/plans/adg-action-dispatch-c9e4a2.md"
PAGE_ID = "36b27693-f55c-8136-a578-d1c743439d4c"

SUMMARY = (
    "COMPLETED W0–W3 (2026-05-25): ADG post-run dispatch — adg_action_queue.json with "
    "provenance; operator playbook; hotspot deterministic linkage; burndown ## Next action; "
    "optional Notion FIX backlog sync (FIX-only, idempotent)."
)

AI_SUMMARY = """- PLAN_STATUS: Completed (W0–W3)
- W0: adg_action_dispatch_playbook + adg-post-run-burndown.mdc
- W1: adg_action_queue.py + schema + generate_full_adg hook (7 tests)
- W2: hotspot_gate_linkage + scan_apps_hotspots + burndown footer (6 tests)
- W3: adg_fix_backlog_sync.py FIX-only Notion sync (6 tests)
- Closeout: docs/reports/cursor/adg_action_dispatch_closeout_receipt.md
- Queue SSOT: artifacts/adg/adg_action_queue_<ts>.json"""

CLOSEOUT_COMMENT = """Plan closeout — adg-action-dispatch-c9e4a2 (2026-05-25)

Waves complete:
• W0 — Operator playbook + post-run FIX-first rule
• W1 — Ranked action queue + provenance digests + non-blocking ADG hook
• W2 — Hotspot linkage_source (no invented gates) + burndown ## Next action
• W3 — Optional FIX-only Notion backlog sync (SKIP_NOTION_TOKEN_MISSING)

Receipt: docs/reports/cursor/adg_action_dispatch_closeout_receipt.md

NON_CLAIMS: no auto-repair; no TRACK mass cleanup; no gate weakening; no agentic_core edits."""


def _patch_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        print("SKIP_NOTION_TOKEN_MISSING", file=sys.stderr)
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "patch_error": str(exc)}), file=sys.stderr)
        return False


def _post_comment(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    chunks = [CLOSEOUT_COMMENT[i : i + 1900] for i in range(0, len(CLOSEOUT_COMMENT), 1900)]
    rich_text = [{"type": "text", "text": {"content": c}} for c in chunks]
    payload = {"parent": {"page_id": page_id}, "rich_text": rich_text}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.notion.com/v1/comments",
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
            json.loads(resp.read().decode("utf-8"))
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "comment_error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    if not (REPO / PLAN_PATH).is_file():
        print(f"BLOCKED: plan file missing: {PLAN_PATH}", file=sys.stderr)
        return 1
    patched = _patch_page(PAGE_ID)
    commented = _post_comment(PAGE_ID) if patched else False
    out = {
        "ok": patched,
        "patched": patched,
        "comment_posted": commented,
        "page_id": PAGE_ID,
        "slug": SLUG,
        "status": "Completed" if patched else "unchanged",
    }
    print(json.dumps(out, indent=2))
    if patched:
        print(f"PLAN_COMPLETED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={PAGE_ID}")
    return 0 if patched else 1


if __name__ == "__main__":
    raise SystemExit(main())
