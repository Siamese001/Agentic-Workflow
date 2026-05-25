#!/usr/bin/env python3
"""Comprehensive historical plan status backfill — detect and repair all drift.

This script extends repair_notion_plan_statuses.py to:
1. Query ALL plans in the Notion Plans DB (not just "Not Started")
2. Compare each plan's Notion Status to its on-disk frontmatter status
3. Report drift (Notion status != on-disk status)
4. Optionally patch Notion to match on-disk state

Usage:
    python tools/notion/backfill_historical_plan_statuses.py --dry-run
    python tools/notion/backfill_historical_plan_statuses.py --patch

Exit codes:
    0 - success (or dry-run complete)
    1 - error (API failure, auth missing)
    2 - drift detected (CI mode)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
)
from _notion_plans_status_check import (  # noqa: E402
    CANONICAL_STATUSES,
    STALE_EQUIVALENTS,
)

sys.path.insert(0, str(REPO_ROOT))
from tools.notion._plan_registration_helpers import log_plans_db_write  # noqa: E402  DS-1

PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
TIMEOUT = 30.0
THROTTLE_S = 0.35

_STATUS_MAP: dict[str, str] = {
    **{s.lower(): s for s in CANONICAL_STATUSES},
    **{k.lower(): v for k, v in STALE_EQUIVALENTS.items() if k.isascii() and not k.startswith("🟢")},
    "done": "Completed",
}


def _token() -> str:
    t = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY", "")
    if not t:
        sys.exit("ERROR: set NOTION_TOKEN or NOTION_API_KEY")
    return t


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_token()}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }


def _req(method: str, url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


def _query_all_plans() -> list[dict]:
    """Query ALL plans in the Plans DB (no status filter)."""
    url = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
    pages: list[dict] = []
    cursor = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        result = _req("POST", url, body)
        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
        time.sleep(THROTTLE_S)
    return pages


def _extract_notion_status(page: dict) -> str | None:
    """Extract the Status select value from a Notion page."""
    props = page.get("properties", {})
    status_prop = props.get("Status", {})
    select_val = status_prop.get("select")
    if select_val:
        return select_val.get("name")
    return None


def _extract_slug(page: dict) -> str:
    """Extract the Slug (title property) from a Notion page."""
    props = page.get("properties", {})
    slug_chunks = props.get("Slug", {}).get("title", [])
    return "".join(c.get("plain_text", "") for c in slug_chunks)


def _rich_text_val(prop: dict) -> str:
    return "".join(c.get("plain_text", "") for c in prop.get("rich_text", []))


def _extract_status_from_plan(md: str) -> str | None:
    """Return canonical Notion status string extracted from plan markdown.

    Returns None when no on-disk ground truth exists. Callers MUST skip
    rows with None — never overwrite Notion based on a default.

    RCA NOTION_PLANS_STATUS_RCA_2026-05-10 (Cause A): the previous default
    of "Not Started" caused a bulk overwrite of 89+ rows because most plan
    markdowns lack frontmatter status. The only safe default is to skip.
    """
    # 1. Frontmatter: status: <value>
    m = re.search(r"^status:\s*(.+)$", md, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        val = m.group(1).strip().strip('"').strip("'").lower()
        for k, v in _STATUS_MAP.items():
            if k in val:
                return v

    # 2. Bold metadata line: **Status**: <value>
    m = re.search(r"\*\*Status\*\*:?\s*(.+)", md, flags=re.IGNORECASE)
    if m:
        val = m.group(1).strip().lower().split("(")[0].strip()
        for k, v in _STATUS_MAP.items():
            if k in val:
                return v

    # 3. Plain "Status: <value>" line (not in a table)
    m = re.search(r"^Status:\s*(.+)$", md, flags=re.MULTILINE)
    if m:
        val = m.group(1).strip().lower().split("(")[0].strip()
        for k, v in _STATUS_MAP.items():
            if k in val:
                return v

    # 4. Contains SUPERSEDED anywhere prominent
    if "SUPERSEDED" in md:
        return "Retired"

    # 5. No on-disk ground truth -> signal "do not overwrite Notion".
    return None


def _resolve_plan_file(slug: str, file_path_val: str | None) -> Path | None:
    """Resolve the plan file path from slug and/or file_path property."""
    if file_path_val:
        p = REPO_ROOT / file_path_val.lstrip("/")
        if p.exists():
            return p
    # Fallback: construct from slug
    p = PLANS_DIR / f"{slug}.md"
    if p.exists():
        return p
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Comprehensive historical plan status backfill"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Report drift without patching")
    parser.add_argument("--patch", action="store_true",
                        help="Apply patches to Notion to match on-disk status")
    parser.add_argument("--ci", action="store_true",
                        help="CI mode: exit 2 if drift detected")
    args = parser.parse_args()

    if not args.dry_run and not args.patch and not args.ci:
        print("ERROR: specify --dry-run, --patch, or --ci")
        return 1

    print("Fetching all plans from Notion Plans DB…")
    pages = _query_all_plans()
    print(f"  {len(pages)} total plans found\n")

    drift_items: list[dict] = []
    skipped = 0
    no_ground_truth_skipped = 0

    for page in pages:
        slug = _extract_slug(page)
        if not slug:
            continue

        notion_status = _extract_notion_status(page)
        props = page.get("properties", {})
        file_path_val = _rich_text_val(props.get("Plan File Path", {}))

        plan_file = _resolve_plan_file(slug, file_path_val)
        if not plan_file:
            print(f"  SKIP {slug} — no plan file on disk")
            skipped += 1
            continue

        md = plan_file.read_text(encoding="utf-8", errors="replace")
        disk_status = _extract_status_from_plan(md)

        # RCA Cause A: when on-disk has no ground-truth status declaration,
        # SKIP — never overwrite Notion based on an inferred default.
        # Tracked separately from file-missing skips so CI drift count
        # reflects only true (known-disk ≠ notion) divergences.
        if disk_status is None:
            no_ground_truth_skipped += 1
            continue

        if notion_status != disk_status:
            drift_items.append({
                "page_id": page["id"],
                "slug": slug,
                "notion_status": notion_status,
                "disk_status": disk_status,
            })

    print(f"\n{len(drift_items)} drift items found (Notion ≠ on-disk):\n")
    by_status_change: dict[str, list[dict]] = {}
    for item in drift_items:
        key = f"{item['notion_status']} → {item['disk_status']}"
        by_status_change.setdefault(key, []).append(item)

    for key, items in sorted(by_status_change.items()):
        print(f"  → {key} ({len(items)})")
        for item in items:
            print(f"      {item['slug']}")

    if skipped:
        print(f"\n  ({skipped} skipped — no on-disk file)")
    if no_ground_truth_skipped:
        print(
            f"  ({no_ground_truth_skipped} skipped — on-disk file present but no "
            "ground-truth status; excluded from drift count per RCA Cause A fix)"
        )

    if not drift_items:
        print("\n✓ No drift detected. Notion and on-disk are in sync.")
        return 0

    if args.dry_run or args.ci:
        print(f"\n--dry-run: no patches applied.")
        if args.ci:
            return 2  # CI mode: signal drift detected
        return 0

    # --patch mode
    print(f"\nPatching {len(drift_items)} items…")
    patched = 0
    errors = 0

    for item in drift_items:
        patch_url = f"{NOTION_BASE}/pages/{item['page_id']}"
        payload = {"properties": {"Status": {"select": {"name": item['disk_status']}}}}
        try:
            _req("PATCH", patch_url, payload)
            print(f"  ✓ {item['slug']}: {item['notion_status']} → {item['disk_status']}")
            log_plans_db_write(  # DS-1
                event="patch_status",
                slug=item["slug"],
                writer="backfill_historical_plan_statuses",
                detail=f"status→{item['disk_status']}",
            )
            patched += 1
            time.sleep(THROTTLE_S)
        except urllib.error.HTTPError as e:
            print(f"  ✗ {item['slug']}: {e.code} {e.read().decode()[:120]}")
            errors += 1

    print(f"\nDone. patched={patched} errors={errors}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
