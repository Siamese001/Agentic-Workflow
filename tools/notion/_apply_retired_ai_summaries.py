"""Apply AI Summary patches for Retired Plans rows in bulk.

Reads artifacts/notion/retired_ai_summaries.json (produced by
_gen_retired_ai_summaries.py) and PATCHes each Plans row's "AI Summary "
property via Notion REST. One subprocess, N HTTP calls — out of scope of
constitutional §25 (MCP serialization) since this is a direct REST client,
not an MCP tool dispatch.

Skips rows whose AI Summary is already non-empty (idempotent re-runs).
Prints per-row OK/SKIP/FAIL with running totals.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_INPUT = _REPO_ROOT / "artifacts" / "notion" / "retired_ai_summaries.json"
_NOTION_VERSION = "2025-09-03"


def _token() -> str | None:
    for k in ("NOTION_API_KEY", "NOTION_TOKEN"):
        v = os.environ.get(k)
        if v:
            return v
    return None


def _get_existing_ai_summary(token: str, page_id: str) -> str:
    """Return current AI Summary plain text (empty when blank)."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": _NOTION_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    props = body.get("properties", {})
    prop = props.get("AI Summary ") or props.get("AI Summary") or {}
    rt = prop.get("rich_text") or []
    return "".join(c.get("plain_text", "") for c in rt if isinstance(c, dict)).strip()


def _patch_ai_summary(token: str, page_id: str, summary: str) -> None:
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "AI Summary ": {
                "rich_text": [{"type": "text", "text": {"content": summary}}]
            }
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": _NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()


def main() -> int:
    token = _token()
    if not token:
        print("ERROR: NOTION_API_KEY / NOTION_TOKEN not set")
        return 2

    rows = json.loads(_INPUT.read_text(encoding="utf-8"))
    print(f"Loaded {len(rows)} candidates from {_INPUT}")

    ok = skipped = failed = 0
    for i, r in enumerate(rows, 1):
        slug = r["slug"]
        page_id = r["page_id"]
        target = r["ai_summary"]
        try:
            existing = _get_existing_ai_summary(token, page_id)
            if existing:
                print(f"[{i:3}/{len(rows)}] SKIP {slug} (already set: {existing[:40]!r})")
                skipped += 1
                continue
            _patch_ai_summary(token, page_id, target)
            print(f"[{i:3}/{len(rows)}] OK   {slug}: {target}")
            ok += 1
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:200]
            print(f"[{i:3}/{len(rows)}] FAIL {slug}: HTTP {exc.code} {body}")
            failed += 1
        except urllib.error.URLError as exc:
            print(f"[{i:3}/{len(rows)}] FAIL {slug}: URL error {exc.reason}")
            failed += 1
        # Polite throttle: Notion REST allows ~3 rps, keep 100ms gap.
        time.sleep(0.12)

    print()
    print(f"Done: ok={ok} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
