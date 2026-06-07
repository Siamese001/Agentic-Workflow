#!/usr/bin/env python3
"""
migrate_to_unified_plan_c4f8e2.py — one-shot supersession migration.

Performs:
  (a) POST a Plans-DB row for adg-three-bucket-unified-c4f8e2 (idempotent).
  (b) PATCH every open Wave/Phase Convergence row whose Plan File matches one
      of the 5 superseded source plans, setting:
        - Plan File = "adg-three-bucket-unified-c4f8e2.md"
        - Parent Plan Summary appended with supersession note (preserve prior).

Idempotent: re-running is safe. Uses urllib only. NOTION_TOKEN resolved from
env or .env per snapshot_renderer.py pattern.

Usage:
    python tools/notion/migrate_to_unified_plan_c4f8e2.py --dry-run
    python tools/notion/migrate_to_unified_plan_c4f8e2.py --execute

Audit log: artifacts/governance/migrate_unified_plan_c4f8e2_audit.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"

WAVE_PHASE_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
PLANS_DS_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
PLANS_DB_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"

NEW_PLAN_SLUG = "adg-three-bucket-unified-c4f8e2"
NEW_PLAN_FILE = f"{NEW_PLAN_SLUG}.md"

SOURCE_PLAN_SLUGS = (
    "adg-three-bucket-authority-model-7e2a91",
    "three-bucket-gap-remediation-069806",
    "three-bucket-otel-view-5db409",
    "adg-ci-spine-delegation-gate-438b16",
    "adg-ci-gate-hardening-deferred-b4e3c9",
)

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = REPO_ROOT / "artifacts" / "governance" / "migrate_unified_plan_c4f8e2_audit.jsonl"


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set (env or .env)")


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, tok: str, body: dict | None = None, timeout: int = 30) -> dict[str, Any]:
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
            body_txt = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {err.code} {method} {url}: {body_txt}") from err
        except urllib.error.URLError as err:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"URL error: {err}") from err
    raise RuntimeError(f"Exhausted retries: {method} {url}")


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _query_ds(ds_id: str, tok: str, filter_: dict | None = None) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if filter_:
            body["filter"] = filter_
        if cursor:
            body["start_cursor"] = cursor
        resp = _http("POST", f"{NOTION_API}/data_sources/{ds_id}/query", tok, body)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return rows


def _rt_text(props: dict, name: str) -> str:
    items = props.get(name, {}).get("rich_text", [])
    return "".join(it.get("plain_text", "") for it in items)


def _title_text(props: dict, name: str) -> str:
    items = props.get(name, {}).get("title", [])
    return "".join(it.get("plain_text", "") for it in items)


def step_a_post_plans_row(tok: str, dry_run: bool) -> dict:
    """Idempotent POST of Plans-DB row for the unified plan."""
    existing = _query_ds(
        PLANS_DS_ID,
        tok,
        filter_={"property": "Plan File Path", "rich_text": {"contains": NEW_PLAN_SLUG}},
    )
    if existing:
        page_id = existing[0]["id"]
        print(f"[A] Plans row already exists: {page_id} — skipping POST")
        _audit({"step": "A", "action": "skip_existing", "page_id": page_id})
        return {"action": "skip", "page_id": page_id}

    plan_file_path = f"docs/archive/windsurf/legacy-tree/plans/{NEW_PLAN_FILE}"
    slug = NEW_PLAN_SLUG
    summary = (
        "Unified plan superseding adg-three-bucket-authority-model-7e2a91, "
        "three-bucket-gap-remediation-069806, three-bucket-otel-view-5db409, "
        "adg-ci-spine-delegation-gate-438b16, and adg-ci-gate-hardening-deferred-b4e3c9. "
        "6 waves, 35 phases, ~165k tokens. Drives ADG to ADG_CERTIFIED green in strict mode."
    )
    body = {
        "parent": {"type": "database_id", "database_id": PLANS_DB_ID},
        "properties": {
            "Slug": {"title": [{"type": "text", "text": {"content": slug}}]},
            "Plan File Path": {
                "rich_text": [{"type": "text", "text": {"content": plan_file_path}}]
            },
            "Summary": {"rich_text": [{"type": "text", "text": {"content": summary}}]},
            "Status": {"select": {"name": "Not Started"}},
            "Exists On Disk": {"checkbox": True},
        },
    }
    if dry_run:
        print(f"[A] DRY-RUN would POST Plans row: {slug} ({plan_file_path})")
        _audit({"step": "A", "action": "dry_run_post", "slug": slug})
        return {"action": "dry_run", "slug": slug}

    resp = _http("POST", f"{NOTION_API}/pages", tok, body)
    page_id = resp["id"]
    print(f"[A] Plans row created: {page_id}")
    _audit({"step": "A", "action": "created", "page_id": page_id, "slug": slug})
    return {"action": "created", "page_id": page_id}


def step_b_migrate_wave_phase_rows(tok: str, dry_run: bool) -> dict:
    """PATCH all Wave/Phase rows whose Plan File matches a source plan."""
    or_clauses = [
        {"property": "Plan File", "rich_text": {"contains": slug}}
        for slug in SOURCE_PLAN_SLUGS
    ]
    rows = _query_ds(WAVE_PHASE_DS_ID, tok, filter_={"or": or_clauses})
    print(f"[B] Found {len(rows)} candidate rows across {len(SOURCE_PLAN_SLUGS)} source plans")

    migrated = 0
    skipped = 0
    failed = 0
    for row in rows:
        page_id = row["id"]
        props = row["properties"]
        current_plan = _rt_text(props, "Plan File")
        title = _title_text(props, "Phase Title")

        # Skip if already migrated.
        if NEW_PLAN_SLUG in current_plan:
            skipped += 1
            continue

        prior_summary = _rt_text(props, "Parent Plan Summary")
        new_summary = (
            (prior_summary + "\n\n" if prior_summary else "")
            + f"[SUPERSEDED 2026-04-30] Migrated from {current_plan or '(unknown source)'} "
            f"to {NEW_PLAN_FILE} per consolidated unified plan."
        )
        # Notion rich_text content limit 2000 chars per text block.
        if len(new_summary) > 1900:
            new_summary = new_summary[:1900] + "…"

        patch_body = {
            "properties": {
                "Plan File": {
                    "rich_text": [{"type": "text", "text": {"content": NEW_PLAN_FILE}}]
                },
                "Parent Plan Summary": {
                    "rich_text": [{"type": "text", "text": {"content": new_summary}}]
                },
            }
        }

        if dry_run:
            print(f"[B] DRY-RUN would PATCH {page_id} | {current_plan} -> {NEW_PLAN_FILE} | {title[:60]}")
            _audit({"step": "B", "action": "dry_run", "page_id": page_id, "from": current_plan, "title": title})
            migrated += 1
            continue

        try:
            _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, patch_body)
            migrated += 1
            print(f"[B] Migrated {page_id} | {current_plan[:40]:40s} -> {NEW_PLAN_FILE} | {title[:50]}")
            _audit({"step": "B", "action": "migrated", "page_id": page_id, "from": current_plan, "title": title})
        except RuntimeError as err:
            failed += 1
            print(f"[B] FAILED {page_id}: {err}", file=sys.stderr)
            _audit({"step": "B", "action": "failed", "page_id": page_id, "error": str(err)[:500]})
        # Be polite to the Notion API.
        time.sleep(0.34)  # ~3 req/s

    print(f"[B] Summary: migrated={migrated} skipped={skipped} failed={failed}")
    return {"migrated": migrated, "skipped": skipped, "failed": failed}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    grp.add_argument("--execute", action="store_true", help="Apply changes to Notion")
    args = parser.parse_args(argv)
    dry_run = args.dry_run

    tok = _token()
    print(f"=== Migration to {NEW_PLAN_FILE} ({'DRY-RUN' if dry_run else 'EXECUTE'}) ===")

    a_result = step_a_post_plans_row(tok, dry_run)
    b_result = step_b_migrate_wave_phase_rows(tok, dry_run)

    print()
    print("=== Summary ===")
    print(f"  Plans row: {a_result}")
    print(f"  Wave/Phase rows: {b_result}")
    print(f"  Audit log: {AUDIT_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
