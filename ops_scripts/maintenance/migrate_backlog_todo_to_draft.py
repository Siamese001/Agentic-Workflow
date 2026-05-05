"""One-shot: migrate Backlog Items Status=Todo -> Not Started (canonical taxonomy).

Plan: .windsurf/plans/fortknox-100pct-static-runtime-gap-9a3d4f.md (adjacent
cleanup). The canonical Backlog Items Status taxonomy (AGENTS.md "Plans DB
Status Taxonomy" + "Shared taxonomy" note) is 7 options: In Progress, Not Started,
Deprioritized, Waiting, Completed, Retired, Archived. `Todo` is a legacy drift that survived the
2026-05-02 `Proposed -> Not Started` rename; this script retires it.

Uses the Notion REST API directly via httpx, bypassing MCP serialization
constraints (§25 is aimed at Cascade tool-call loops, not one-shot
administrative scripts). Requires NOTION_TOKEN env var.

Exit codes:
    0 - all Todo rows migrated OR none found
    2 - API errors mid-migration (partial state; safe to re-run; idempotent)
    3 - harness error (token missing, library missing)
"""
from __future__ import annotations

import os
import sys
import time
from typing import Any

try:
    import httpx
except ImportError:
    print("HARNESS_ERROR: httpx required (pip install httpx)", file=sys.stderr)
    sys.exit(3)

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_TOKEN")
if not NOTION_TOKEN:
    print("HARNESS_ERROR: NOTION_TOKEN env var not set", file=sys.stderr)
    sys.exit(3)

NOTION_VERSION = "2025-09-03"
BASE = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

BACKLOG_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
TARGET_FROM = "Todo"
TARGET_TO = "Not Started"


def query_all_with_status(client: httpx.Client, status: str) -> list[dict]:
    """Pagination-aware. Returns every page with Status=<status>."""
    out: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {
            "filter": {"property": "Status", "select": {"equals": status}},
            "page_size": 100,
        }
        if cursor:
            body["start_cursor"] = cursor
        r = client.post(f"{BASE}/data_sources/{BACKLOG_DS_ID}/query", json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        out.extend(data["results"])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return out


def patch_status(client: httpx.Client, page_id: str, new_status: str) -> bool:
    body = {"properties": {"Status": {"select": {"name": new_status}}}}
    r = client.patch(f"{BASE}/pages/{page_id}", json=body, timeout=30)
    if r.status_code == 200:
        return True
    print(f"  FAIL {page_id}: {r.status_code} {r.text[:200]}", file=sys.stderr)
    return False


def main() -> int:
    with httpx.Client(headers=HEADERS) as client:
        print(f"[migrate] querying Backlog Items where Status={TARGET_FROM}...")
        rows = query_all_with_status(client, TARGET_FROM)
        print(f"[migrate] found {len(rows)} rows to migrate")
        if not rows:
            return 0

        ok = 0
        fail = 0
        total = len(rows)
        t0 = time.time()
        for i, row in enumerate(rows, start=1):
            if patch_status(client, row["id"], TARGET_TO):
                ok += 1
            else:
                fail += 1
            if i % 10 == 0 or i == total:
                elapsed = time.time() - t0
                rate = i / max(elapsed, 0.001)
                eta = (total - i) / max(rate, 0.001)
                bar_len = 30
                filled = int(bar_len * i / total)
                bar = "=" * filled + "-" * (bar_len - filled)
                print(
                    f"  [{bar}] {i}/{total} ({100 * i // total}%) "
                    f"ok={ok} fail={fail} rate={rate:.1f}/s eta={eta:.0f}s",
                    flush=True,
                )
            # Gentle rate limiting to stay under Notion's 3 req/s budget.
            time.sleep(0.35)

        print(f"[migrate] DONE ok={ok} fail={fail} elapsed={time.time() - t0:.1f}s")
        return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
