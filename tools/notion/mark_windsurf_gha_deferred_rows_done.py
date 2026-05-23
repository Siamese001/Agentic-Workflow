#!/usr/bin/env python3
"""Mark windsurf-gha-cutover deferred-scope Wave/Phase rows as Done."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"

PAGE_IDS = (
    "36927693-f55c-81cb-ba6e-d688f8b70608",  # W5.D1
    "36927693-f55c-81d5-a4b8-e3e5d68102c9",  # W1.D1
    "36927693-f55c-8122-89eb-da41c4147bf7",  # W5.D2
    "36927693-f55c-8107-9300-f71d7c94395c",  # W5.D3
    "36927693-f55c-81c0-80bf-e29e47bc5378",  # W5.D4
)


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not tok:
        raise RuntimeError("NOTION_TOKEN not set")
    return tok


def main() -> int:
    tok = _token()
    for page_id in PAGE_IDS:
        body = {
            "properties": {
                "Status": {"select": {"name": "Done"}},
            }
        }
        req = urllib.request.Request(
            f"{NOTION_API}/pages/{page_id}",
            data=json.dumps(body).encode("utf-8"),
            method="PATCH",
            headers={
                "Authorization": f"Bearer {tok}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_VERSION,
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            json.loads(resp.read().decode("utf-8"))
        print(f"Done: {page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
