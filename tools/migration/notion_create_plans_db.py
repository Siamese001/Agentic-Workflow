#!/usr/bin/env python3
"""
notion_create_plans_db.py — W3 of notion-backlog-schema-refactor-7c3d9e.

Creates a Plans Notion database, backfills one row per unique plan slug
extracted from existing Backlog Items (Wave/Phase Convergence), adds a
`Plan` relation property to Backlog Items, and points every row at its
matching Plans entry.

Idempotent:
  - Reuses existing Plans DB if slug-set already mapped (via ID written to
    tools/migration/.notion_plans_db_id)
  - Skips Plans page creation for slugs already present
  - Skips Backlog row patches when `Plan` relation already set

Usage:
    python tools/migration/notion_create_plans_db.py --dry-run
    python tools/migration/notion_create_plans_db.py --execute
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
BACKLOG_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
# Parent page that already holds Wave/Phase Convergence
PARENT_PAGE_ID = "33f27693-f55c-8134-9041-d34b6dc11425"

PLANS_DB_ID_FILE = Path("tools/migration/.notion_plans_db_id")
AUDIT_LOG = Path("artifacts/windsurf/notion_plans_migration_audit.jsonl")


def _load_token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = Path(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set")


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, tok: str, body: dict | None = None,
          timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < 2:
                time.sleep(int(err.headers.get("Retry-After", "2")))
                continue
            raise RuntimeError(
                f"HTTP {err.code} {method} {url}: "
                f"{err.read().decode('utf-8', errors='replace')}"
            ) from err
        except urllib.error.URLError as err:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"URL error: {err}") from err
    raise RuntimeError(f"Exhausted retries: {method} {url}")


def _rt(prop: dict | None) -> str:
    if not prop:
        return ""
    return "".join(x.get("plain_text", "") for x in prop.get("rich_text", []))


def audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def normalize_slug(raw: str) -> str:
    """Strip .md, NEW: prefix, parenthetical annotations."""
    s = raw.strip()
    if s.startswith("NEW:"):
        s = s[4:]
    # Remove trailing annotations like " (to be created)"
    if " (" in s:
        s = s.split(" (", 1)[0]
    if s.endswith(".md"):
        s = s[:-3]
    return s.strip()


def fetch_backlog_rows(tok: str) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = _http("POST",
                     f"{NOTION_API}/data_sources/{BACKLOG_DS_ID}/query",
                     tok, body)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return rows


def create_plans_database(tok: str) -> str:
    """Create the Plans database under PARENT_PAGE_ID and add schema
    properties to its auto-created data source. Return database_id."""
    body = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
        "title": [{"type": "text", "text": {"content": "Plans"}}],
        "properties": {"Name": {"title": {}}},
    }
    resp = _http("POST", f"{NOTION_API}/databases", tok, body)
    db_id = resp["id"]
    # The new DB auto-creates a data source with only the title. Add our schema.
    ds_id = resp["data_sources"][0]["id"]
    schema = {
        "properties": {
            "Name": {"name": "Slug"},  # rename title column
            "Status": {
                "select": {
                    "options": [
                        {"name": "Active", "color": "green"},
                        {"name": "Proposed", "color": "yellow"},
                        {"name": "Complete", "color": "blue"},
                        {"name": "Archived", "color": "gray"},
                    ]
                }
            },
            "Summary": {"rich_text": {}},
            "Plan File Path": {"rich_text": {}},
            "Exists On Disk": {"checkbox": {}},
        }
    }
    _http("PATCH", f"{NOTION_API}/data_sources/{ds_id}", tok, schema)
    return db_id


def _plans_data_source_id(tok: str, plans_db_id: str) -> str:
    """Resolve the (single) data_source_id for the Plans database."""
    db = _http("GET", f"{NOTION_API}/databases/{plans_db_id}", tok)
    sources = db.get("data_sources", [])
    if not sources:
        raise RuntimeError(f"No data sources on DB {plans_db_id}")
    return sources[0]["id"]


def add_relation_to_backlog(tok: str, plans_db_id: str) -> None:
    """Add a `Plan` relation property on Wave/Phase Convergence -> Plans."""
    ds_id = _plans_data_source_id(tok, plans_db_id)
    body = {
        "properties": {
            "Plan": {
                "relation": {
                    "data_source_id": ds_id,
                    "type": "single_property",
                    "single_property": {},
                }
            }
        }
    }
    _http("PATCH", f"{NOTION_API}/data_sources/{BACKLOG_DS_ID}", tok, body)


def list_existing_plans(tok: str, plans_db_id: str) -> dict[str, str]:
    """Map slug -> page_id for existing Plans rows."""
    # First resolve the data_source_id for this database
    db = _http("GET", f"{NOTION_API}/databases/{plans_db_id}", tok)
    data_sources = db.get("data_sources", [])
    if not data_sources:
        return {}
    ds_id = data_sources[0]["id"]
    mapping: dict[str, str] = {}
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = _http("POST", f"{NOTION_API}/data_sources/{ds_id}/query", tok, body)
        for page in resp.get("results", []):
            slug = "".join(x.get("plain_text", "")
                           for x in page["properties"]["Slug"]["title"])
            if slug:
                mapping[slug] = page["id"]
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return mapping


def create_plan_page(tok: str, plans_db_id: str, slug: str,
                     exists_on_disk: bool) -> str:
    file_path = f".windsurf/plans/{slug}.md" if exists_on_disk else ""
    status = "Active" if exists_on_disk else "Proposed"
    ds_id = _plans_data_source_id(tok, plans_db_id)
    body = {
        "parent": {"type": "data_source_id", "data_source_id": ds_id},
        "properties": {
            "Slug": {"title": [{"type": "text", "text": {"content": slug}}]},
            "Status": {"select": {"name": status}},
            "Plan File Path": {
                "rich_text": [{"type": "text", "text": {"content": file_path}}]
                if file_path else []
            },
            "Exists On Disk": {"checkbox": exists_on_disk},
        },
    }
    resp = _http("POST", f"{NOTION_API}/pages", tok, body)
    return resp["id"]


def patch_backlog_relation(tok: str, page_id: str, plan_page_id: str) -> None:
    _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, {
        "properties": {
            "Plan": {"relation": [{"id": plan_page_id}]}
        }
    })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)

    tok = _load_token()

    # Step 1: fetch backlog + extract unique slugs
    rows = fetch_backlog_rows(tok)
    print(f"[1/5] Fetched {len(rows)} backlog rows")

    slug_map: dict[str, str] = {}  # slug -> sample-raw value (for audit)
    page_to_slug: dict[str, str] = {}
    disk_plans = {p.stem for p in Path(".windsurf/plans").glob("*.md")}
    for row in rows:
        raw = _rt(row["properties"].get("Plan File"))
        if not raw:
            continue
        slug = normalize_slug(raw)
        if slug:
            slug_map.setdefault(slug, raw)
            page_to_slug[row["id"]] = slug

    unique_slugs = sorted(slug_map.keys())
    on_disk = [s for s in unique_slugs if s in disk_plans]
    off_disk = [s for s in unique_slugs if s not in disk_plans]
    print(f"[2/5] Extracted {len(unique_slugs)} unique slugs "
          f"({len(on_disk)} on disk, {len(off_disk)} proposed)")

    if args.dry_run:
        print()
        print("On-disk slugs:")
        for s in on_disk:
            print(f"  [Active]   {s}")
        print("Off-disk (proposed) slugs:")
        for s in off_disk:
            print(f"  [Proposed] {s}  (raw: {slug_map[s][:60]})")
        print()
        print(f"Would create: 1 Plans DB, {len(unique_slugs)} plan rows, "
              f"{len(page_to_slug)} relation patches")
        return 0

    # Step 3: create Plans DB (or reuse)
    if PLANS_DB_ID_FILE.exists():
        plans_db_id = PLANS_DB_ID_FILE.read_text(encoding="utf-8").strip()
        print(f"[3/5] Reusing Plans DB {plans_db_id}")
    else:
        plans_db_id = create_plans_database(tok)
        PLANS_DB_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PLANS_DB_ID_FILE.write_text(plans_db_id, encoding="utf-8")
        print(f"[3/5] Created Plans DB: {plans_db_id}")
        audit({"op": "create_db", "id": plans_db_id})
        # Add the Plan relation column to backlog DS (only on fresh create)
        add_relation_to_backlog(tok, plans_db_id)
        print("      Added 'Plan' relation to Backlog Items")
        audit({"op": "add_relation_property", "backlog_ds": BACKLOG_DS_ID,
               "target_db": plans_db_id})

    # Step 4: backfill Plans pages (idempotent)
    existing_plans = list_existing_plans(tok, plans_db_id)
    print(f"[4/5] Plans DB has {len(existing_plans)} existing rows")
    created = 0
    for slug in unique_slugs:
        if slug in existing_plans:
            continue
        exists = slug in disk_plans
        page_id = create_plan_page(tok, plans_db_id, slug, exists)
        existing_plans[slug] = page_id
        created += 1
        audit({"op": "create_plan", "slug": slug, "page_id": page_id,
               "exists_on_disk": exists})
        if created % 5 == 0:
            print(f"      Created {created} plan pages...")
            time.sleep(0.3)
    print(f"      Total plan pages created this run: {created}")

    # Step 5: link every backlog row -> its Plans page
    linked = 0
    skipped = 0
    errors = 0
    total = len(page_to_slug)
    for i, (row_id, slug) in enumerate(page_to_slug.items(), 1):
        plan_page_id = existing_plans.get(slug)
        if not plan_page_id:
            errors += 1
            continue
        # Check if relation already set
        row = next((r for r in rows if r["id"] == row_id), None)
        if row:
            rel = row["properties"].get("Plan")
            if rel and rel.get("relation"):
                skipped += 1
                continue
        try:
            patch_backlog_relation(tok, row_id, plan_page_id)
            linked += 1
            if i % 3 == 0:
                time.sleep(0.35)
        except RuntimeError as exc:
            errors += 1
            audit({"op": "link_error", "row_id": row_id, "slug": slug,
                   "error": str(exc)[:200]})
        if i % 20 == 0 or i == total:
            pct = i * 100 // total
            print(f"  [{i:>3}/{total}] {pct:>3}% linked={linked} "
                  f"skipped={skipped} errors={errors}")

    print()
    print("=== W3 migration complete ===")
    print(f"Plans DB:           {plans_db_id}")
    print(f"Plan pages created: {created}")
    print(f"Rows linked:        {linked}")
    print(f"Rows skipped:       {skipped}  (already linked)")
    print(f"Errors:             {errors}")
    print(f"Audit log:          {AUDIT_LOG}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
