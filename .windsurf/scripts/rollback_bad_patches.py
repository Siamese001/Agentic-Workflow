#!/usr/bin/env python3
"""
rollback_bad_patches.py — revert Status=Done patches made by
post_commit_phase_closer when a bare-wave trigger over-fanned out.

Reads the last run from artifacts/windsurf/phase_close_audit.jsonl. For each
patch where `via` matches an over-broad bare wave (W1, W2, W3, W5, E1), reverts
the Notion page Status to Todo and strips the appended [AUTO-CLOSE ...] line
from Blocking Items.

Dry-run by default. Use --execute to actually patch.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "phase_close_audit.jsonl"
ROLLBACK_LOG = REPO_ROOT / "artifacts" / "windsurf" / "phase_close_rollback.jsonl"

NOTION_API_VERSION = "2025-09-03"
NOTION_BASE = "https://api.notion.com/v1"

# Triggers known to cause over-fanout due to short bare wave IDs with starts_with
OVER_BROAD_VIAS = {"W1", "W2", "W3", "W5", "E1"}


def _log(record: dict[str, Any]) -> None:
    ROLLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ROLLBACK_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _notion_request(method: str, path: str, token: str, body: dict | None = None) -> dict | None:
    url = f"{NOTION_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            parsed: Any = json.loads(resp.read().decode("utf-8"))
            return parsed if isinstance(parsed, dict) else None
    except urllib.error.HTTPError as exc:
        print(
            f"  HTTP {exc.code} on {path}: {exc.read().decode('utf-8', errors='replace')[:300]}",
            file=sys.stderr,
        )
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  NET err on {path}: {exc}", file=sys.stderr)
        return None


def find_bad_patches() -> list[dict[str, Any]]:
    """Read audit log, find patches from last run with over-broad `via`."""
    all_lines = [json.loads(l) for l in AUDIT_LOG.open(encoding="utf-8")]
    summary_idxs = [i for i, l in enumerate(all_lines) if l.get("event") == "run_summary"]
    start = summary_idxs[-2] + 1 if len(summary_idxs) >= 2 else 0
    recent = all_lines[start:]
    bad: list[dict[str, Any]] = []
    for entry in recent:
        patched = entry.get("patched", [])
        if not isinstance(patched, list):
            continue
        for p in patched:
            if isinstance(p, dict) and p.get("via") in OVER_BROAD_VIAS and "page_id" in p:
                bad.append(
                    {
                        "page_id": p["page_id"],
                        "phase_id": p.get("phase_id", "?"),
                        "via": p.get("via"),
                        "sha": entry.get("sha", "?"),
                    }
                )
    return bad


AUTO_CLOSE_LINE_RE = re.compile(r"\n?\[AUTO-CLOSE \d{4}-\d{2}-\d{2}\] commit=[0-9a-f]+")


def rollback_page(page: dict[str, Any], token: str, dry_run: bool) -> bool:
    page_id = page["page_id"]
    # Fetch current blocking text
    cur = _notion_request("GET", f"/pages/{page_id}", token)
    if cur is None:
        return False
    rt = cur.get("properties", {}).get("Blocking Items", {}).get("rich_text") or []
    current_text = "".join(t.get("plain_text", "") for t in rt)
    cleaned = AUTO_CLOSE_LINE_RE.sub("", current_text).strip()

    body = {
        "properties": {
            "Status": {"select": {"name": "Todo"}},
            "Blocking Items": {"rich_text": [{"type": "text", "text": {"content": cleaned[:2000]}}]},
        }
    }
    if dry_run:
        print(f"  DRY: would revert {page_id} ({page['phase_id']} via {page['via']})")
        return True
    resp = _notion_request("PATCH", f"/pages/{page_id}", token, body)
    ok = resp is not None
    _log({"event": "rollback", "ok": ok, **page})
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually patch (default: dry-run)")
    args = parser.parse_args()

    bad = find_bad_patches()
    # Dedupe by page_id (multiple patches may target same page)
    seen: set[str] = set()
    unique = []
    for b in bad:
        if b["page_id"] not in seen:
            seen.add(b["page_id"])
            unique.append(b)

    print(f"Found {len(unique)} unique rows to roll back (from {len(bad)} total bad patches).")
    by_via: dict[str, int] = {}
    for b in unique:
        by_via[b["via"]] = by_via.get(b["via"], 0) + 1
    for via, n in sorted(by_via.items()):
        print(f"  via={via}: {n} rows")

    if not args.execute:
        print("\nDRY RUN — use --execute to actually roll back.")
        for b in unique[:10]:
            print(f"  {b['page_id']} phase={b['phase_id']} via={b['via']} sha={b['sha']}")
        if len(unique) > 10:
            print(f"  ... and {len(unique) - 10} more")
        return 0

    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        print("NOTION_TOKEN not set", file=sys.stderr)
        return 1

    ok_count = 0
    for b in unique:
        if rollback_page(b, token, dry_run=False):
            ok_count += 1
    print(f"\nRolled back: {ok_count}/{len(unique)}")
    return 0 if ok_count == len(unique) else 1


if __name__ == "__main__":
    sys.exit(main())
