#!/usr/bin/env python3
"""One-off: retire all apps-lic Plans DB rows pending apps_lic rebaseline."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

DS_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
SUMMARY = (
    "RETIRED 2026-05-24: Pre-rebaseline apps_lic scope superseded — apps_rg spine "
    "materially changed (apps-rg-spine-only-unification-d8f4a2). Full apps_lic "
    "rebaseline required before executing any lic plan."
)
AI = "Retired — pending apps_lic spine rebaseline vs apps_rg"


def main() -> int:
    tok = os.environ.get("NOTION_TOKEN", "").strip()
    if not tok:
        print("NOTION_TOKEN missing", file=sys.stderr)
        return 1
    headers = {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }
    # Query all apps-lic slugs
    page_ids: list[str] = []
    cursor = None
    while True:
        body: dict = {
            "page_size": 100,
            "filter": {"property": "Slug", "title": {"contains": "apps-lic"}},
        }
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            f"https://api.notion.com/v1/data_sources/{DS_ID}/query",
            data=json.dumps(body).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
        for row in data.get("results", []):
            page_ids.append(row["id"])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    props = {
        "Status": {"select": {"name": "Retired"}},
        "Summary": {"rich_text": [{"type": "text", "text": {"content": SUMMARY}}]},
        "AI Summary ": {"rich_text": [{"type": "text", "text": {"content": AI}}]},
        "Waiting For": {"rich_text": []},
    }
    ok = 0
    for pid in page_ids:
        req = urllib.request.Request(
            f"https://api.notion.com/v1/pages/{pid}",
            data=json.dumps({"properties": props}).encode(),
            headers=headers,
            method="PATCH",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                slug = json.load(resp)["properties"]["Slug"]["title"][0]["plain_text"]
            print(f"OK {pid} {slug}")
            ok += 1
        except urllib.error.HTTPError as e:
            print(f"FAIL {pid} {e.code} {e.read().decode()[:200]}", file=sys.stderr)
    print(f"patched {ok}/{len(page_ids)}")
    return 0 if ok == len(page_ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
