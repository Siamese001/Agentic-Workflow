#!/usr/bin/env python3
"""W4 closeout: Plans Completed + backlog Done with closure evidence."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402

NOTION_BASE = "https://api.notion.com/v1"
NOTION_API_VERSION = "2025-09-03"
PLAN_PAGE_ID = "36d27693-f55c-81d7-847a-c34cd7807849"
PLAN_PATH = ".claude/plans/exec-summary-regen-stuck-c0-split-a4f8e2.md"
SLUG = "exec-summary-regen-stuck-c0-split-a4f8e2"
CLOSEOUT_REPORT = "docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_closeout_20260527.md"
BACKLOG = (
    (
        "36c27693-f55c-81d4-b75e-f9ac99509a07",
        "G2 stuck-loop: x2_stuck_same_failure wired (W1); 6 unit tests PASS.",
    ),
    (
        "36c27693-f55c-81b7-916d-c2a65edde07f",
        "C0 claim/proof split (W2); Brown W3 claim_gate 0/10 regen fails vs baseline 10/10.",
    ),
)
SUMMARY = (
    "COMPLETED (2026-05-27): W0–W4 — G2 stuck-loop early-exit, C0 claim_text/proof_text split, "
    "Brown re-proof exec_summary_20260527_025447_w3. Parent f8a3c2 not reopened."
)
AI_SUMMARY = """- PLAN_STATUS: COMPLETE (2026-05-27)
- W1: x2_stuck_same_failure + regen_lane_stats (9 pytest)
- W2: claim/proof v2 + 2 facts migrated + audit 0/42
- W3: Brown DRAFT_READY; x2_claim_field_maps PASS; regen claim-fail 0/10
- Closeout: docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_closeout_20260527.md
- Deferred: X3 judge cert (Anthropic soft-fail) — same as baseline 230615"""


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


def _patch(token: str, page_id: str, properties: dict) -> tuple[bool, str]:
    req = urllib.request.Request(
        f"{NOTION_BASE}/pages/{page_id}",
        data=json.dumps({"properties": properties}).encode("utf-8"),
        method="PATCH",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
        return True, "ok"
    except urllib.error.HTTPError as exc:
        return False, exc.read().decode("utf-8", errors="replace")[:500]


def _patch_plan(token: str) -> tuple[bool, str]:
    props = {
        "Status": {"select": {"name": "Completed"}},
        "Exists On Disk": {"checkbox": True},
        "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
        "Summary": {"rich_text": [{"text": {"content": SUMMARY[:2000]}}]},
        "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}]},
    }
    return _patch(token, PLAN_PAGE_ID, props)


def _patch_backlog(token: str, page_id: str, evidence: str) -> tuple[bool, str]:
    props = {
        "Status": {"select": {"name": "Done"}},
        "Plan": {"relation": [{"id": PLAN_PAGE_ID}]},
        "Plan File": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
        "Last Updated": {"date": {"start": date.today().isoformat()}},
        "Evidence": {
            "rich_text": [
                {
                    "text": {
                        "content": (
                            f"CLOSED by {SLUG} (2026-05-27). {evidence} "
                            f"Closeout: {CLOSEOUT_REPORT}"
                        )[:2000]
                    }
                }
            ]
        },
    }
    return _patch(token, page_id, props)


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN required", file=sys.stderr)
        return 1
    ok_plan, msg_plan = _patch_plan(token)
    print(f"{'OK' if ok_plan else 'FAIL'} plan={PLAN_PAGE_ID} {msg_plan}")
    if not ok_plan:
        return 1
    for page_id, note in BACKLOG:
        ok, msg = _patch_backlog(token, page_id, note)
        print(f"{'OK' if ok else 'FAIL'} backlog={page_id} {msg}")
        if not ok:
            return 1
    print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={PLAN_PAGE_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
