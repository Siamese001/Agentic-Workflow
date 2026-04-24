"""Mark W5 completed Wave/Phase Convergence rows as Done.

Items completed in session 2026-04-23:
  GEN-PIPELINE-DRIFT        -> Done (W5.2 commit c03e5896b3)
  GUARDIAN-TOKEN-SSOT       -> Done (W5.1 commit 2a65ada79a + 855f0e6c23 normalization)
  SCANNER-EDGEKIND-MISCLASSIFY -> Done (W5.1 alias accepted; deeper scanner fix re-deferred)
  TIER-B-ANNOTATIONS        -> Done (all 9 HIGH auto-approved after W5.1)

Deferred (stay Todo):
  SSOT-HARDCODING-W2        -> constants added in 855f0e6c23; 123-site migration separate
  SC1-STRUCTURAL-BLOCK      -> Out of scope per plan G5

Reads NOTION_TOKEN from env. Uses Notion HTTP API v2025-09-03.
"""
from __future__ import annotations
import json
import os
import sys

import requests

TOKEN = os.environ.get("NOTION_TOKEN")
if not TOKEN:
    print("NOTION_TOKEN not in env", file=sys.stderr)
    sys.exit(2)

DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
PLAN_FILE = "repo-tech-debt-wave1-b3c8d1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

# Phase IDs (exact match on Phase ID field) to mark Done
TO_MARK_DONE = {
    "GEN-PIPELINE-DRIFT",
    "GUARDIAN-TOKEN-SSOT",
    "SCANNER-EDGEKIND-MISCLASSIFY",
    "TIER-B-ANNOTATIONS",
}


def query_rows() -> list[dict]:
    url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
    pages: list[dict] = []
    cursor = None
    while True:
        body: dict = {
            "filter": {
                "property": "Plan File",
                "rich_text": {"contains": PLAN_FILE},
            },
            "page_size": 100,
        }
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(url, headers=HEADERS, data=json.dumps(body), timeout=30)
        r.raise_for_status()
        data = r.json()
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return pages


def _prop_text(page: dict, prop_name: str) -> str:
    props = page.get("properties", {})
    chunk = props.get(prop_name, {})
    if chunk.get("type") == "title":
        return "".join(t.get("plain_text", "") for t in chunk.get("title", []))
    if chunk.get("type") == "rich_text":
        return "".join(t.get("plain_text", "") for t in chunk.get("rich_text", []))
    return ""


def _prop_status(page: dict) -> str:
    sel = page.get("properties", {}).get("Status", {}).get("select") or {}
    return sel.get("name", "")


def patch_status_done(page_id: str) -> None:
    url = f"https://api.notion.com/v1/pages/{page_id}"
    body = {"properties": {"Status": {"select": {"name": "Done"}}}}
    r = requests.patch(url, headers=HEADERS, data=json.dumps(body), timeout=30)
    r.raise_for_status()


def main() -> int:
    rows = query_rows()
    print(f"[query] found {len(rows)} row(s) for plan={PLAN_FILE}")
    updated = 0
    skipped = 0
    for p in rows:
        pid = p["id"]
        title = _prop_text(p, "Phase Title")
        phase_id = _prop_text(p, "Phase ID")
        status = _prop_status(p)
        # Match either the Phase ID column or the phase name in title
        matched = phase_id in TO_MARK_DONE or any(pid_tag in title for pid_tag in TO_MARK_DONE)
        if not matched:
            print(f"  [keep-todo] {title!r}  status={status!r}")
            continue
        if status == "Done":
            print(f"  [skip-done] {title!r} already Done")
            skipped += 1
            continue
        patch_status_done(pid)
        print(f"  [patch] {title!r}  ({status!r} -> Done)")
        updated += 1
    print(f"[done] updated={updated} already_done={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
