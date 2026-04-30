"""Notion stale-row cleanup — flips orphan rows under archived plans to Descoped.

Rules:
  - Only acts on rows whose plan_file points to a slug that exists ONLY in
    archives/windsurf_plans/ (not in .windsurf/plans/).
  - Status Todo or Blocked  -> Descoped (with audit marker in Blocking Items)
  - Status In Progress      -> SKIPPED (work may be active)
  - Other statuses          -> SKIPPED
  - Idempotent: checks Blocking Items for the audit marker before patching.

Usage:
  python tools/reports/cleanup_archived_stale_rows.py --dry-run   # preview
  python tools/reports/cleanup_archived_stale_rows.py --execute   # apply patches
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

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "reports"))
from audit_notion_backlog_coverage import _query_all_rows, _extract  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
AUDIT_LOG = REPO / "artifacts" / "windsurf" / "notion_stale_cleanup.jsonl"

MARKER_PREFIX = "[STALE-CLEANUP"
MARKER_DATE = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
MARKER_TEXT = (
    f"{MARKER_PREFIX} {MARKER_DATE}] Parent plan archived in archives/windsurf_plans/. "
    "Row orphaned from active scope; flipped to Descoped. Re-route Plan File and reopen "
    "if work is still required."
)

PLANS_DIR = REPO / ".windsurf" / "plans"
ARCHIVES_DIR = REPO / "archives" / "windsurf_plans"


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = REPO / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("NOTION_TOKEN not set")


def _patch_row(token: str, page_id: str, blocking_items_new: str) -> dict[str, Any]:
    body = {
        "properties": {
            "Status": {"select": {"name": "Descoped"}},
            "Blocking Items": {
                "rich_text": [{"type": "text", "text": {"content": blocking_items_new[:1900]}}]
            },
        }
    }
    req = urllib.request.Request(
        f"{NOTION_API}/pages/{page_id}",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if attempt == 2:
                raise SystemExit(f"PATCH failed for {page_id}: HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc
            time.sleep(1.5 * (attempt + 1))
        except urllib.error.URLError as exc:
            if attempt == 2:
                raise SystemExit(f"PATCH network error for {page_id}: {exc.reason}") from exc
            time.sleep(1.5 * (attempt + 1))
    return {}


def _existing_blocking_items(row: dict[str, Any]) -> str:
    rt = row.get("properties", {}).get("Blocking Items", {}).get("rich_text", [])
    return "".join(b.get("plain_text", "") for b in rt)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only — no Notion writes")
    parser.add_argument("--execute", action="store_true", help="Apply patches")
    args = parser.parse_args()
    if not args.dry_run and not args.execute:
        parser.error("specify --dry-run or --execute")

    disk_stems = {p.stem for p in PLANS_DIR.glob("*.md")}
    archived_stems = {p.stem for p in ARCHIVES_DIR.rglob("*.md")} if ARCHIVES_DIR.exists() else set()

    print("Querying Notion (paginated)...")
    raw_rows = _query_all_rows()
    print(f"  {len(raw_rows)} rows retrieved")

    OPEN_TARGET = {"Todo", "Blocked"}
    SKIP_INPROG = {"In Progress"}

    targets: list[tuple[dict[str, Any], dict[str, str]]] = []
    skip_inprog: list[dict[str, str]] = []
    skip_already_marked: list[dict[str, str]] = []

    for raw in raw_rows:
        ext = _extract(raw)
        plan = ext["plan_file"]
        if not plan:
            continue
        if plan in disk_stems:
            continue
        if plan not in archived_stems:
            continue  # truly orphan / sentinel — handled separately
        if ext["status"] in SKIP_INPROG:
            skip_inprog.append(ext)
            continue
        if ext["status"] not in OPEN_TARGET:
            continue
        existing = _existing_blocking_items(raw)
        if MARKER_PREFIX in existing:
            skip_already_marked.append(ext)
            continue
        new_blocking = f"{MARKER_TEXT}\n\n--- previous Blocking Items ---\n{existing}".rstrip()
        targets.append((raw, {**ext, "_new_blocking": new_blocking}))

    print()
    print(f"  Targets to flip Todo/Blocked -> Descoped: {len(targets)}")
    print(f"  Skipped (In Progress, not safe to auto-close): {len(skip_inprog)}")
    print(f"  Skipped (already marked from prior run): {len(skip_already_marked)}")
    print()
    print("=== TARGETS ===")
    for _, t in targets:
        print(f"  [{t['status']:>8}] {t['plan_file']:<55} | {t['phase_id']:<22} | {t['title'][:55]}")

    if skip_inprog:
        print()
        print("=== SKIPPED (In Progress) ===")
        for s in skip_inprog:
            print(f"  {s['plan_file']:<55} | {s['phase_id']:<22} | {s['title'][:55]}")

    if args.dry_run:
        print()
        print("DRY RUN — no patches sent. Re-run with --execute to apply.")
        return 0

    # EXECUTE
    print()
    print(f"Executing PATCH on {len(targets)} rows...")
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    token = _token()
    succeeded = 0
    failed = 0
    with AUDIT_LOG.open("a", encoding="utf-8") as log:
        for i, (raw, t) in enumerate(targets, start=1):
            page_id = raw["id"]
            try:
                _patch_row(token, page_id, t["_new_blocking"])
                succeeded += 1
                log.write(json.dumps({
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "page_id": page_id,
                    "plan_file": t["plan_file"],
                    "phase_id": t["phase_id"],
                    "old_status": t["status"],
                    "new_status": "Descoped",
                    "title": t["title"],
                    "result": "ok",
                }) + "\n")
                if i % 5 == 0 or i == len(targets):
                    print(f"  {i}/{len(targets)} patched")
            except SystemExit as exc:
                failed += 1
                log.write(json.dumps({
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "page_id": page_id,
                    "plan_file": t["plan_file"],
                    "phase_id": t["phase_id"],
                    "result": "error",
                    "error": str(exc),
                }) + "\n")
                print(f"  ERROR on {page_id}: {exc}")
            time.sleep(0.35)  # gentle on Notion's rate limit

    print()
    print(f"Done. Succeeded: {succeeded}, Failed: {failed}")
    print(f"Audit log: {AUDIT_LOG}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
