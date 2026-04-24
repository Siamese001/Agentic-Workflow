"""Set Notion Wave/Phase row Status by Wave ID (reusable across all l2v2 waves).

Usage:
    python tools/debug/_l2v2_notion_set_status.py W0 Done
    python tools/debug/_l2v2_notion_set_status.py W1 "In Progress"
"""

from __future__ import annotations

import json
import os
import sys

import requests

PLAN_FILENAME = "l2-execute-v2-agent-conformance-c8e4f1.md"
WAVE_DS = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"


def main() -> int:
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: _l2v2_notion_set_status.py <wave_id> <status>\n")
        return 2
    wave_id = sys.argv[1]
    status = sys.argv[2]

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
        f"https://api.notion.com/v1/data_sources/{WAVE_DS}/query",
        headers=h,
        data=json.dumps(
            {
                "filter": {
                    "and": [
                        {"property": "Plan File", "rich_text": {"contains": PLAN_FILENAME}},
                        {"property": "Wave ID", "rich_text": {"equals": wave_id}},
                    ]
                },
                "page_size": 10,
            }
        ),
        timeout=30,
    )
    q.raise_for_status()
    rows = q.json().get("results", [])
    if not rows:
        sys.stderr.write(f"No row found for plan={PLAN_FILENAME} wave={wave_id}\n")
        return 1
    updated = 0
    for p in rows:
        pid = p["id"]
        title = "".join(
            t.get("plain_text", "") for t in p["properties"].get("Phase Title", {}).get("title", [])
        )
        r = requests.patch(
            f"https://api.notion.com/v1/pages/{pid}",
            headers=h,
            data=json.dumps({"properties": {"Status": {"select": {"name": status}}}}),
            timeout=30,
        )
        if r.status_code >= 400:
            sys.stderr.write(f"  FAIL {r.status_code}: {r.text[:300]}\n")
            continue
        print(f"  [notion] {wave_id} -> {status}  {title!r}")
        updated += 1
    return 0 if updated else 1


if __name__ == "__main__":
    sys.exit(main())
