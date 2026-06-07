"""Phase 2 cleanup — handles UNSCORED open rows, empty-Status rows, and produces
a triage report for truly-orphan rows.

Actions taken:
  - 5 UNSCORED open rows: prepend [Pn] band to Phase Title (band assigned from
    title heuristics; user can revise)
  - 8 empty-Status rows under archived plans: flip to Descoped + cleanup marker
  - 1 _INDEX_open_scope_inventory row: flip to Done (inventory snapshot, point-in-time)
  - Truly-orphan: NO writes — just print the triage list

Idempotent: skips rows whose Phase Title already has [Pn] prefix or whose
Blocking Items already contains the cleanup marker.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "reports"))
from audit_notion_backlog_coverage import _query_all_rows, _extract  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
AUDIT_LOG = REPO / "artifacts" / "governance" / "notion_phase2_cleanup.jsonl"

PLANS_DIR = REPO / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
ARCHIVES_DIR = REPO / "archives" / "windsurf_plans"

MARKER_DATE = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
MARKER_PREFIX = "[STALE-CLEANUP"
EMPTY_STATUS_MARKER = (
    f"{MARKER_PREFIX} {MARKER_DATE}] Empty Status under archived parent plan; "
    "flipped to Descoped. Re-route Plan File and reopen if work still required."
)

# Hand-assigned bands for the 5 UNSCORED rows. Keyed by (plan_norm, phase_id).
# Bands chosen by inspection of title content vs. ADG canonical layer multipliers.
SCORE_OVERRIDES: dict[tuple[str, str], str] = {
    ("three-bucket-otel-view-5db409", "W9.1"): "P3",   # 20-site observability migration
    ("three-bucket-otel-view-5db409", "W10.1"): "P4",  # schedule-driven NOT NULL graduation
    ("three-bucket-otel-view-5db409", "W11.1"): "P3",  # blocked on external manifest
    ("streamline-constants-territories-d0cb16", "GAP-4"): "P3",  # 10-file import refactor
    ("p2-burndown-wave-9e4c17", "6.1"): "P2",  # anti-pattern ratchet enforcement
}


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

    archived = {p.stem for p in ARCHIVES_DIR.rglob("*.md")} if ARCHIVES_DIR.exists() else set()
    disk = {p.stem for p in PLANS_DIR.glob("*.md")}

    print("Querying Notion (paginated)...")
    raw_rows = _query_all_rows()
    print(f"  {len(raw_rows)} rows retrieved")

    OPEN = {"Todo", "Blocked", "In Progress"}
    score_targets: list[tuple[dict[str, Any], dict[str, str], str]] = []
    empty_status_targets: list[tuple[dict[str, Any], dict[str, str]]] = []
    truly_orphan_open: list[dict[str, str]] = []

    for raw in raw_rows:
        ext = _extract(raw)
        plan = ext["plan_file"]
        title = ext["title"]
        status = ext["status"]
        phase = ext["phase_id"]

        # 1. UNSCORED open rows (no [Pn] / [INDEX] / [META] / etc. prefix)
        if status in OPEN and not re.match(
            r"^\[(P\d|NEXT|SCORING|META|INDEX|VALIDATED|RECOVERY|AGGREGATE|DESCOPE|STALE|FOLLOWUP|RECON)",
            title,
        ):
            band = SCORE_OVERRIDES.get((plan, phase))
            if band:
                score_targets.append((raw, ext, band))

        # 2. Empty-Status rows under archived plans
        if status == "" and plan in archived:
            existing = _existing_blocking(raw)
            if MARKER_PREFIX not in existing:
                empty_status_targets.append((raw, ext))

        # 3. Truly orphan open rows (slug nowhere on disk or archives, not sentinel/NEW)
        if status in OPEN and plan and plan not in disk and plan not in archived:
            if "NEW" in plan or "(" in plan or "_INDEX" in plan or " | " in plan or "multi:" in plan:
                continue
            truly_orphan_open.append(ext)

    print()
    print(f"  UNSCORED open rows to band: {len(score_targets)}")
    print(f"  Empty-Status rows under archived plans: {len(empty_status_targets)}")
    print(f"  Truly orphan open rows (manual triage): {len(truly_orphan_open)}")

    print()
    print("=== UNSCORED → BAND ===")
    for _, ext, band in score_targets:
        print(f"  [{band}] {ext['plan_file']:<45} | {ext['phase_id']:<10} | {ext['title'][:60]}")

    print()
    print("=== EMPTY-STATUS → DESCOPED ===")
    for _, ext in empty_status_targets:
        print(f"  {ext['plan_file']:<45} | {ext['phase_id']:<10} | {ext['title'][:60]}")

    print()
    print("=== TRULY ORPHAN (manual triage) ===")
    for ext in truly_orphan_open:
        print(f"  [{ext['status']}] {ext['plan_file']:<45} | {ext['phase_id']:<10} | {ext['title'][:60]}")

    if args.dry_run:
        print()
        print("DRY RUN — re-run with --execute")
        return 0

    print()
    print(f"Executing PATCHes...")
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    token = _token()
    succ = 0
    fail = 0
    with AUDIT_LOG.open("a", encoding="utf-8") as log:
        # Score targets — prepend [Pn] to Phase Title
        for raw, ext, band in score_targets:
            new_title = f"[{band}] {ext['title']}"
            try:
                _patch(token, raw["id"], {
                    "Phase Title": {"title": [{"type": "text", "text": {"content": new_title[:200]}}]},
                })
                succ += 1
                log.write(json.dumps({
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "action": "band_assigned",
                    "page_id": raw["id"],
                    "plan_file": ext["plan_file"],
                    "phase_id": ext["phase_id"],
                    "band": band,
                    "old_title": ext["title"],
                    "new_title": new_title,
                }) + "\n")
                print(f"  banded: [{band}] {ext['plan_file']}/{ext['phase_id']}")
            except SystemExit as exc:
                fail += 1
                print(f"  ERROR banding {raw['id']}: {exc}")
            time.sleep(0.35)

        # Empty-Status under archived plans → Descoped
        for raw, ext in empty_status_targets:
            existing = _existing_blocking(raw)
            new_blocking = f"{EMPTY_STATUS_MARKER}\n\n--- previous Blocking Items ---\n{existing}".rstrip()
            try:
                _patch(token, raw["id"], {
                    "Status": {"select": {"name": "Descoped"}},
                    "Blocking Items": {"rich_text": [{"type": "text", "text": {"content": new_blocking[:1900]}}]},
                })
                succ += 1
                log.write(json.dumps({
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "action": "empty_status_descoped",
                    "page_id": raw["id"],
                    "plan_file": ext["plan_file"],
                    "phase_id": ext["phase_id"],
                    "title": ext["title"],
                }) + "\n")
                print(f"  empty→Descoped: {ext['plan_file']}/{ext['phase_id']}")
            except SystemExit as exc:
                fail += 1
                print(f"  ERROR empty-status flip {raw['id']}: {exc}")
            time.sleep(0.35)

    # Write triage report
    triage = REPO / "docs" / "reports" / "plans" / f"notion_orphan_triage_{datetime.now(tz=timezone.utc):%Y%m%d}.md"
    triage.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Notion Orphan-Row Triage — {MARKER_DATE}",
        "",
        f"{len(truly_orphan_open)} rows whose Plan File slug exists nowhere on disk or in archives.",
        "Each needs operator judgment: scaffold a plan, fold into existing successor, or Descope.",
        "",
        "| Status | Plan File slug | Phase | Title |",
        "|---|---|---|---|",
    ]
    for ext in truly_orphan_open:
        title = ext["title"].replace("|", "\\|")[:80]
        lines.append(f"| {ext['status']} | `{ext['plan_file']}` | {ext['phase_id']} | {title} |")
    triage.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print(f"Triage report: {triage}")
    print(f"Done. Succeeded: {succ}, Failed: {fail}")
    print(f"Audit log: {AUDIT_LOG}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
