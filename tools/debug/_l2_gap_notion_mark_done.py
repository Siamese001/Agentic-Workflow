"""Mark all Wave/Phase Convergence rows for plan b7c4e2 as Done.

Reads NOTION_TOKEN from env. Uses requests against Notion HTTP API v2025-09-03.
Queries the data source, filters by Plan File, patches Status to 'Done'.
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
PLAN_FILE = "l2-execute-best-practices-gap-b7c4e2.md"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
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


def extract_title(page: dict) -> str:
    props = page.get("properties", {})
    pt = props.get("Phase Title", {}).get("title", [])
    return "".join(t.get("plain_text", "") for t in pt)


def extract_status(page: dict) -> str:
    props = page.get("properties", {})
    sel = props.get("Status", {}).get("select") or {}
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
        title = extract_title(p)
        status = extract_status(p)
        if status == "Done":
            print(f"  [skip] {title!r} already Done")
            skipped += 1
            continue
        patch_status_done(pid)
        print(f"  [patch] {title!r} -> Done  (was {status!r})")
        updated += 1
    print(f"[done] updated={updated} skipped={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
