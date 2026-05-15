"""Archive the 6 duplicate Notion pages created by retry of deferred_scope hook."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

# Newer duplicates to archive (from post_cursor_agent_deferred_scope_capture.jsonl)
DUPLICATE_PAGE_IDS = [
    "34b27693-f55c-817a-a7bc-f003f5a08617",  # E.E.1 dup
    "34b27693-f55c-815d-955a-de27e2f4200d",  # F.F.1 dup
    "34b27693-f55c-81ec-8679-f9627dc92d5f",  # G.G.1 dup
    "34b27693-f55c-816d-8be0-d08993fb8fed",  # B.B.4 dup
    "34b27693-f55c-81ad-b3e8-db5b0eeeaec9",  # B.B.5 dup
    "34b27693-f55c-810b-bcef-f8bdc09c395b",  # C.C.3sub dup
]

TOKEN = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
if not TOKEN:
    print("ERROR: NOTION_TOKEN / NOTION_API_KEY not set in env", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

ok = 0
fail = 0
for pid in DUPLICATE_PAGE_IDS:
    url = f"https://api.notion.com/v1/pages/{pid}"
    body = json.dumps({"in_trash": True}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=HEADERS, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            status = "archived" if data.get("in_trash") or data.get("archived") else "ok-unknown"
            print(f"  {status}  {pid}")
            ok += 1
    except urllib.error.HTTPError as e:
        print(f"  FAIL  {pid}  HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}")
        fail += 1
    except (urllib.error.URLError, OSError) as e:
        print(f"  FAIL  {pid}  {type(e).__name__}: {e}")
        fail += 1

print(f"\nArchived {ok}/{len(DUPLICATE_PAGE_IDS)} (fail: {fail})")
