#!/usr/bin/env python3
"""triage_plans_duplicates.py — resolve duplicate Plans-DB slug groups.

Reads the live Notion Plans DB, identifies slugs with ≥2 active rows, and
archives losers (in_trash=true) while keeping a single canonical winner
per slug. Decision rules:

  1. If statuses differ, status priority picks the winner:
       Completed > In Progress > Lower Priority > Waiting > Not Started > Retired > Archived
     (Completed always wins because the user explicitly tracked work-done.)
  2. If statuses tie, most-recently-edited wins (last_edited_time desc).

Losers are PATCHed with ``archived: true`` (recoverable from Notion trash).
NEVER deletes — preserves an audit trail.

Usage:
    python tools/notion/triage_plans_duplicates.py --dry-run
    python tools/notion/triage_plans_duplicates.py --execute

Plan: notion-plans-status-rca-followups-b8e3f2 (W2.P1).
RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B follow-up.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
)

# Unified Plans-DB write telemetry (RCA §8).
from tools.notion._plan_registration_helpers import log_plans_db_write  # noqa: E402

AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "triage_plans_duplicates.jsonl"
TIMEOUT_S = 30.0
THROTTLE_S = 0.35

# Status priority — higher = better. Ties broken by last_edited_time.
_STATUS_PRIORITY: dict[str, int] = {
    "Completed": 100,
    "In Progress": 80,
    "Lower Priority": 60,
    "Deferred": 55,
    "Deprioritized": 55,
    "Waiting": 50,
    "Not Started": 40,
    "Retired": 20,
    "Archived": 10,
}


def _token() -> str:
    t = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY", "")
    if not t:
        sys.exit("ERROR: set NOTION_TOKEN or NOTION_API_KEY")
    return t


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }


def _http(
    method: str,
    url: str,
    tok: str,
    body: dict | None = None,
    *,
    timeout: float = TIMEOUT_S,
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch_all_plans(tok: str) -> list[dict]:
    """Return every active (non-trashed, non-archived) Plans-DB page."""
    url = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
    pages: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = _http("POST", url, tok, body)
        for p in data.get("results", []):
            if p.get("in_trash") or p.get("archived"):
                continue
            pages.append(p)
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return pages


def _slug(page: dict) -> str:
    chunks = page.get("properties", {}).get("Slug", {}).get("title", [])
    return "".join(c.get("plain_text", "") for c in chunks)


def _status(page: dict) -> str:
    sel = page.get("properties", {}).get("Status", {}).get("select")
    return (sel or {}).get("name", "")


def _last_edited(page: dict) -> str:
    return page.get("last_edited_time", "")


def pick_winner(rows: list[dict]) -> tuple[dict, list[dict]]:
    """Return (winner, losers) for one duplicate group."""
    def sort_key(p: dict) -> tuple[int, str]:
        # Higher priority, then more recent edit time.
        return (_STATUS_PRIORITY.get(_status(p), 0), _last_edited(p))

    ranked = sorted(rows, key=sort_key, reverse=True)
    return ranked[0], ranked[1:]


def archive_page(page_id: str, reason: str, tok: str) -> tuple[bool, str]:
    """Soft-delete via PATCH archived=true. Plans schema lacks an Evidence
    field, so the audit trail lives in artifacts/cursor/triage_plans_duplicates.jsonl.
    """
    url = f"{NOTION_BASE}/pages/{page_id}"
    body = {"archived": True}
    try:
        _http("PATCH", url, tok, body)
        return True, "ok"
    except urllib.error.HTTPError as exc:
        return False, f"http_{exc.code}:{exc.read().decode('utf-8', 'replace')[:200]}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"net:{exc!r}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.execute:
        parser.error("specify exactly one of --dry-run / --execute")

    tok = _token()
    print("Fetching all active Plans rows…", flush=True)
    pages = fetch_all_plans(tok)
    print(f"  {len(pages)} active rows", flush=True)

    by_slug: dict[str, list[dict]] = {}
    for p in pages:
        s = _slug(p)
        if s:
            by_slug.setdefault(s, []).append(p)

    groups = {s: rows for s, rows in by_slug.items() if len(rows) >= 2}
    if not groups:
        print("No duplicate groups. Nothing to do.")
        return 0

    print(f"\n{len(groups)} duplicate slug groups to triage:\n")
    archived = 0
    failed = 0
    for slug in sorted(groups):
        rows = groups[slug]
        winner, losers = pick_winner(rows)
        win_status = _status(winner)
        win_id = winner.get("id", "")
        win_edit = _last_edited(winner)
        print(f"  {slug}")
        print(f"    KEEP   {win_id}  [{win_status}]  edited={win_edit}")
        for loser in losers:
            l_status = _status(loser)
            l_id = loser.get("id", "")
            l_edit = _last_edited(loser)
            print(f"    ARCH   {l_id}  [{l_status}]  edited={l_edit}")
            if args.dry_run:
                _audit({
                    "step": "dry_run_archive", "slug": slug,
                    "winner_id": win_id, "winner_status": win_status,
                    "loser_id": l_id, "loser_status": l_status,
                })
                continue
            reason = (
                f"Duplicate of slug {slug!r}; winner page_id={win_id} "
                f"(status={win_status}, edited={win_edit}). RCA "
                f"NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B."
            )
            ok, msg = archive_page(l_id, reason, tok)
            _audit({
                "step": "archive", "slug": slug,
                "winner_id": win_id, "winner_status": win_status,
                "loser_id": l_id, "loser_status": l_status,
                "ok": ok, "msg": msg,
            })
            # Unified telemetry (RCA §8 mandate).
            log_plans_db_write(
                event="archive_duplicate",
                slug=slug,
                page_id=l_id,
                writer="triage_plans_duplicates.py",
                status_before=l_status,
                status_after=None,  # archived, not status-changed
                ok=ok,
                detail=msg,
                winner_page_id=win_id,
                winner_status=win_status,
            )
            if ok:
                archived += 1
                print(f"           ✓ archived")
            else:
                failed += 1
                print(f"           ✗ FAILED: {msg}")
            time.sleep(THROTTLE_S)

    if args.dry_run:
        print(f"\n--dry-run: would archive {sum(len(g)-1 for g in groups.values())} loser rows")
        return 0

    print(f"\nDone. archived={archived} failed={failed}")
    print(f"Audit: {AUDIT_LOG}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
