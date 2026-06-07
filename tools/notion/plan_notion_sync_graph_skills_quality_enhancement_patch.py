#!/usr/bin/env python3
"""Patch graph-skills-quality-enhancement-c4e8a1 Summary in Notion after plan hardening."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "graph-skills-quality-enhancement-c4e8a1"
PLAN_PATH = ".claude/plans/graph-skills-quality-enhancement-c4e8a1.md"
PAGE_ID = "36b27693-f55c-81c0-bb50-d8df6df2b60e"

SUMMARY = (
    "Not Started (v3.1 pre-W0): Proof classes + X3 normalization (x3_code raw→ALLOW_FINISH). "
    "Pinned Brown JD/briefing SHA-256. Wave command receipts. X2 NA policy. D5 no ad-hoc orchestrator. "
    "NEG-6 capsule≠authority. D10/D13 BLOCKED if no GHA. Canonical CLI only."
)

AI_SUMMARY = """- Plan: graph-skills-quality-enhancement-c4e8a1 v3.1 pre-W0 (2026-05-26)
- X3: normalize x3_code; LIVE_X3_ALLOW_PROOF ≠ literal X3_ALLOW only
- Brown: pinned jd.txt + briefing.md digests in W0/W10
- Receipts: every wave graph_skills_quality_wN_receipt.json (command/cwd/env/exit/git)
- X2: NA gates need gate_id + policy_ref; UNKNOWN blocks
- D5: CONTRACT_TEST + per-section CLI; no custom whole-run script
- NEG-6: allowed_phrases cannot enter allowed_fact_ids / claim ledger
- D10/D13: CI_RATCHET_PROOF only on GHA; local pytest ≠ PASS
- Prior v3: proof classes, phase gates, FEC set equality, agentic_core=false"""


def _patch_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
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
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    if not (REPO / PLAN_PATH).is_file():
        print(f"BLOCKED: missing {PLAN_PATH}", file=sys.stderr)
        return 1
    if _patch_page(PAGE_ID):
        print(json.dumps({"ok": True, "action": "patched", "page_id": PAGE_ID, "slug": SLUG}))
        print(f"PLAN_NOTION_PATCHED: slug={SLUG} notion_page={PAGE_ID}")
        return 0
    print("FAIL: Notion patch failed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
