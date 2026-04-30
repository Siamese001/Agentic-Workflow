"""Phase 3 cleanup — Descope the 6 NEW: placeholder rows.

These rows reference plan slugs that were never scaffolded; 3 of 4 distinct
keys have archive-equivalent plans (work was done under a different name).

Idempotent + reversible (audit log preserves old state).
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
AUDIT_LOG = REPO / "artifacts" / "windsurf" / "notion_phase3_cleanup.jsonl"

MARKER_PREFIX = "[STALE-CLEANUP"
MARKER_DATE = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
MARKER_TEXT = (
    f"{MARKER_PREFIX} {MARKER_DATE}] NEW: placeholder never scaffolded as a real "
    "plan; flipped to Descoped. Reopen and reassign Plan File if work is still required."
)


def _is_placeholder(plan: str) -> bool:
    pl = plan.strip()
    if not pl:
        return False
    if pl.startswith("NEW:"):
        return True
    if "(NEW" in pl or "to be created" in pl.lower() or "to be scaffolded" in pl.lower():
        return True
    if pl.startswith("(no dedicated plan"):
        return True
    return False


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


def _patch(token: str, page_id: str, props: dict[str, Any]) -> dict[str, Any]:
    body = {"properties": props}
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


def _existing_blocking(row: dict[str, Any]) -> str:
    rt = row.get("properties", {}).get("Blocking Items", {}).get("rich_text", [])
    return "".join(b.get("plain_text", "") for b in rt)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.execute:
        parser.error("specify --dry-run or --execute")

    OPEN = {"Todo", "Blocked", "In Progress", "Ready"}
    print("Querying Notion (paginated)...")
    raw_rows = _query_all_rows()
    print(f"  {len(raw_rows)} rows retrieved")

    targets: list[tuple[dict[str, Any], dict[str, str]]] = []
    for raw in raw_rows:
        ext = _extract(raw)
        if not _is_placeholder(ext["plan_file"]):
            continue
        if ext["status"] not in OPEN:
            continue
        existing = _existing_blocking(raw)
        if MARKER_PREFIX in existing:
            continue
        targets.append((raw, ext))

    print(f"  Targets: {len(targets)}")
    print()
    print("=== TARGETS ===")
    for _, t in targets:
        print(f"  [{t['status']:>10}] {t['plan_file']:<70} | {t['phase_id']:<15} | {t['title'][:55]}")

    if args.dry_run:
        print()
        print("DRY RUN — re-run with --execute")
        return 0

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    token = _token()
    succ = 0
    fail = 0
    print()
    print("Executing PATCHes...")
    with AUDIT_LOG.open("a", encoding="utf-8") as log:
        for raw, t in targets:
            existing = _existing_blocking(raw)
            new_blocking = f"{MARKER_TEXT}\n\n--- previous Blocking Items ---\n{existing}".rstrip()
            try:
                _patch(token, raw["id"], {
                    "Status": {"select": {"name": "Descoped"}},
                    "Blocking Items": {"rich_text": [{"type": "text", "text": {"content": new_blocking[:1900]}}]},
                })
                succ += 1
                log.write(json.dumps({
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "action": "new_placeholder_descoped",
                    "page_id": raw["id"],
                    "plan_file": t["plan_file"],
                    "phase_id": t["phase_id"],
                    "old_status": t["status"],
                    "title": t["title"],
                }) + "\n")
                print(f"  descoped: {t['plan_file']} / {t['phase_id']}")
            except SystemExit as exc:
                fail += 1
                print(f"  ERROR {raw['id']}: {exc}")
            time.sleep(0.35)

    print()
    print(f"Done. Succeeded: {succ}, Failed: {fail}")
    print(f"Audit log: {AUDIT_LOG}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
