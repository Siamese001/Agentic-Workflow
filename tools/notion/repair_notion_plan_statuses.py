#!/usr/bin/env python3
"""Repair Plans DB rows whose Status was bulk-set to Draft by the batch uploader.

For each row created on 2026-05-03 with Status=Draft, reads the on-disk plan
file and extracts the real Status from the frontmatter or header, then patches
Notion only if the status differs.

Status extraction priority:
1. Frontmatter line: `status: <value>` (case-insensitive)
2. Bold metadata: `**Status**: <value>`
3. Inline marker: `Status: <value>`
4. If the plan file contains "SUPERSEDED" → Retired
5. If the plan file contains "AUTO-SCAFFOLD" → Draft (keep)
6. Default: Draft (keep, no patch)

Canonical Notion status values: Live, Draft, Waiting, Completed, Retired, Archived

Usage:
    python tools/notion/repair_notion_plan_statuses.py [--dry-run]
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
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
)

PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
TIMEOUT = 30.0

CANONICAL = {"live", "draft", "waiting", "completed", "retired", "archived"}

# Map words found in plan files to canonical Notion status names
_STATUS_MAP = {
    "live": "Live",
    "draft": "Draft",
    "waiting": "Waiting",
    "completed": "Completed",
    "done": "Completed",
    "retired": "Retired",
    "superseded": "Retired",
    "archived": "Archived",
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


def _query_all_draft_pages() -> list[dict]:
    url = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
    pages: list[dict] = []
    cursor = None
    while True:
        body: dict = {
            "page_size": 100,
            "filter": {"property": "Status", "select": {"equals": "Draft"}},
        }
        if cursor:
            body["start_cursor"] = cursor
        result = _req("POST", url, body)
        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
        time.sleep(0.3)
    return pages


def _extract_status_from_plan(md: str) -> str:
    """Return canonical Notion status string extracted from plan markdown."""
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
        val = m.group(1).strip().lower()
        # strip markdown like "Draft (no code changes yet)"
        val = val.split("(")[0].strip()
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

    # 5. AUTO-SCAFFOLD = keep as Draft
    return "Draft"


def _rich_text_val(prop: dict) -> str:
    return "".join(c.get("plain_text", "") for c in prop.get("rich_text", []))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Fetching Draft rows…")
    pages = _query_all_draft_pages()
    print(f"  {len(pages)} Draft rows found\n")

    needs_patch: list[dict] = []
    for page in pages:
        props = page.get("properties", {})
        slug_chunks = props.get("Slug", {}).get("title", [])
        slug = "".join(c.get("plain_text", "") for c in slug_chunks)
        file_path_val = _rich_text_val(props.get("Plan File Path", {}))

        plan_file = REPO_ROOT / file_path_val.lstrip("/") if file_path_val else None
        if not plan_file or not plan_file.exists():
            plan_file = PLANS_DIR / f"{slug}.md"
        if not plan_file.exists():
            print(f"  SKIP {slug} — no plan file on disk")
            continue

        md = plan_file.read_text(encoding="utf-8", errors="replace")
        correct_status = _extract_status_from_plan(md)

        if correct_status != "Draft":
            needs_patch.append({
                "page_id": page["id"],
                "slug": slug,
                "correct_status": correct_status,
            })

    print(f"\n{len(needs_patch)} rows need status correction:\n")
    by_status: dict[str, list[str]] = {}
    for r in needs_patch:
        by_status.setdefault(r["correct_status"], []).append(r["slug"])

    for status, slugs in sorted(by_status.items()):
        print(f"  → {status} ({len(slugs)})")
        for s in slugs:
            print(f"      {s}")

    if not needs_patch:
        print("Nothing to fix.")
        return

    if args.dry_run:
        print("\n--dry-run: no patches applied.")
        return

    print("\nPatching…")
    patched = 0
    errors = 0
    for r in needs_patch:
        patch_url = f"{NOTION_BASE}/pages/{r['page_id']}"
        payload = {"properties": {"Status": {"select": {"name": r["correct_status"]}}}}
        try:
            _req("PATCH", patch_url, payload)
            print(f"  ✓ {r['slug']} → {r['correct_status']}")
            patched += 1
            time.sleep(0.35)
        except urllib.error.HTTPError as e:
            print(f"  ✗ {r['slug']}: {e.code} {e.read().decode()[:120]}")
            errors += 1

    print(f"\nDone. patched={patched} errors={errors}")


if __name__ == "__main__":
    main()
