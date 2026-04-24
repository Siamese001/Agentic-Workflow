"""Mark the Plans DB row for l2-execute-v2-agent-conformance-c8e4f1 as Completed."""
from __future__ import annotations

import json
import os
import sys

import requests

PLAN_SLUG = "l2-execute-v2-agent-conformance-c8e4f1"
PLANS_DS = "ac53d31b-3068-4039-9ebe-856c12caab32"


def main() -> int:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.stderr.write("NOTION_TOKEN not set\n")
        return 2
    h = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }
    q = requests.post(
        f"https://api.notion.com/v1/data_sources/{PLANS_DS}/query",
        headers=h,
        data=json.dumps(
            {
                "filter": {"property": "Slug", "title": {"equals": PLAN_SLUG}},
                "page_size": 1,
            }
        ),
        timeout=30,
    )
    q.raise_for_status()
    rows = q.json().get("results", [])
    if not rows:
        sys.stderr.write(f"No Plans row for {PLAN_SLUG}\n")
        return 1
    pid = rows[0]["id"]
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{pid}",
        headers=h,
        data=json.dumps({"properties": {"Status": {"select": {"name": "Completed"}}}}),
        timeout=30,
    )
    if r.status_code >= 400:
        sys.stderr.write(f"FAIL {r.status_code}: {r.text[:300]}\n")
        return 1
    print(f"[plans] {PLAN_SLUG} -> Completed  page_id={pid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
