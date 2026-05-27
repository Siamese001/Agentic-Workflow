#!/usr/bin/env python3
"""W0 helper: link G2 + C0 backlog rows to exec-summary-regen-stuck-c0-split-a4f8e2 plan."""
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
BACKLOG_PAGE_IDS = (
    "36c27693-f55c-81d4-b75e-f9ac99509a07",
    "36c27693-f55c-81b7-916d-c2a65edde07f",
)
TIMEOUT = 30.0


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


def _patch_plan_relation(page_id: str, token: str) -> tuple[bool, str]:
    body = {
        "properties": {
            "Plan": {"relation": [{"id": PLAN_PAGE_ID}]},
            "Last Updated": {"date": {"start": date.today().isoformat()}},
        }
    }
    req = urllib.request.Request(
        f"{NOTION_BASE}/pages/{page_id}",
        data=json.dumps(body).encode("utf-8"),
        method="PATCH",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            resp.read()
        return True, "ok"
    except urllib.error.HTTPError as exc:
        return False, exc.read().decode("utf-8", errors="replace")[:500]


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN required", file=sys.stderr)
        return 1
    results: list[dict[str, object]] = []
    for page_id in BACKLOG_PAGE_IDS:
        ok, msg = _patch_plan_relation(page_id, token)
        results.append({"page_id": page_id, "ok": ok, "msg": msg})
        print(f"{'OK' if ok else 'FAIL'} backlog={page_id} plan={PLAN_PAGE_ID} {msg}")
    if not all(r["ok"] for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
