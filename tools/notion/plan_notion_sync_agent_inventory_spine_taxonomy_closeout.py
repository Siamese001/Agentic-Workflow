#!/usr/bin/env python3
"""Mark agent-inventory-spine-taxonomy-b4e9f2 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "agent-inventory-spine-taxonomy-b4e9f2"
PLAN_PATH = ".cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md"
PAGE_ID = "36b27693-f55c-81d3-b7a7-d9b54d461f83"
FOLLOW_UP_SLUG = "agent-inventory-deferred-followup-c2a8f1"

SUMMARY = (
    "COMPLETED W0–W3 (2026-05-25): ADR-088 function-based spine truth; four-axis taxonomy on "
    "118 agentic_core *Agent rows; CI ARTIFACT_PROVEN=0; RootCustoms orphan archived; W3 live "
    "spine path (0 *Agent in artifacts). Deferred → agent-inventory-deferred-followup-c2a8f1."
)

AI_SUMMARY = """- PLAN_STATUS: Completed (W0–W3)
- W0: ADR-088 + product_spine_taxonomy_invariants + runtime LAYER.md
- W1: agent_taxonomy_spine_axes; 118-row merge; CI A1/A2; ARTIFACT_PROVEN=0
- W2: RootCustoms legacy archived; misplacement ledger; L6 snapshot harness preserved
- W3: run_w3_live_spine_proof.py LIVE path; a1_invoked_agent_classes=0; Decision 1 defer
- Follow-up: agent-inventory-deferred-followup-c2a8f1 (DS-1..DS-5)
- Closeout: docs/reports/cursor/agent_inventory_spine_taxonomy_closeout_receipt.md"""

CLOSEOUT_COMMENT = """Plan closeout — agent-inventory-spine-taxonomy-b4e9f2 (2026-05-25)

All waves complete:
• W0 — ADR-088 spine vs taxonomy separation
• W1 — Four orthogonal axes; inventory-only gap fill; CI enforces A1/A2
• W2 — RootCustomsAgent orphan archived; misplacement ledger (document-only)
• W3 — Live spine (_test_mode=False); 0 *Agent strings in artifacts; HOW class identity deferred

Deferred scope transferred to follow-up plan:
→ agent-inventory-deferred-followup-c2a8f1
Register: docs/reports/cursor/agent_inventory_deferred_scope_register_20260525.md

Receipts:
• docs/reports/cursor/agent_inventory_spine_taxonomy_w{0,1,2,3}_receipt.md
• docs/reports/cursor/agent_inventory_spine_taxonomy_closeout_receipt.md

Parent plan file remains SSOT on disk; do not reopen for DS-1..DS-5."""


def _patch_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:2000]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}]},
            "Waiting For": {"rich_text": [{"text": {"content": f"Follow-up: {FOLLOW_UP_SLUG}"}}]},
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
    commented = _post_comment(PAGE_ID)
    out = {
        "ok": patched,
        "patched": patched,
        "comment_posted": commented,
        "page_id": PAGE_ID,
        "slug": SLUG,
        "status": "Completed",
        "follow_up": FOLLOW_UP_SLUG,
    }
    print(json.dumps(out, indent=2))
    print(f"PLAN_COMPLETED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={PAGE_ID}")
    return 0 if patched else 1


if __name__ == "__main__":
    raise SystemExit(main())
