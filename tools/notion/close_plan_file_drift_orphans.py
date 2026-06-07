#!/usr/bin/env python3
"""Close Wave/Phase rows that reference missing top-level plan files.

Targets rows still open (Status not in drift CLOSED_STATUSES) whose Plan File
does not resolve under ``.claude/plans/`` (including archive). Sets Status to
Done so nightly drift stops flagging completed legacy scope.

Usage:
  python tools/notion/close_plan_file_drift_orphans.py --dry-run
  python tools/notion/close_plan_file_drift_orphans.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci import check_notion_plan_file_drift as drift  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
THROTTLE_S = 0.35
AUDIT = REPO_ROOT / "artifacts" / "cursor" / "close_plan_file_drift_orphans.jsonl"


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not tok:
        raise RuntimeError("NOTION_TOKEN not set")
    return tok


def _patch_status(page_id: str, token: str, status: str = "Done") -> None:
    body = {"properties": {"Status": {"select": {"name": status}}}}
    req = urllib.request.Request(
        f"{NOTION_API}/pages/{page_id}",
        data=json.dumps(body).encode("utf-8"),
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--status",
        default="Done",
        help="Notion Status to set (default Done)",
    )
    args = parser.parse_args()

    token = _token()
    rows = drift._query_open_rows(token)
    orphans: list[dict[str, str]] = []
    for row in rows:
        if row.get("archived") or row.get("in_trash"):
            continue
        status = drift._extract_status(row)
        if status in drift.CLOSED_STATUSES:
            continue
        plan_file = drift._extract_plan_file(row)
        if not plan_file:
            continue
        if drift._plan_file_exists(plan_file):
            continue
        orphans.append(
            {
                "row_id": row.get("id", ""),
                "plan_file": plan_file,
                "status": status,
                "phase_title": drift._extract_phase_title(row),
            }
        )

    print(f"orphans to close: {len(orphans)}", file=sys.stderr)
    if args.dry_run:
        for o in orphans[:20]:
            print(f"  {o['status']:<12} {o['plan_file']:<50} {o['phase_title'][:40]}", file=sys.stderr)
        if len(orphans) > 20:
            print(f"  ... and {len(orphans) - 20} more", file=sys.stderr)
        return 0

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    ok = 0
    for o in orphans:
        try:
            _patch_status(o["row_id"], token, args.status)
            ok += 1
            AUDIT.write_text(
                (AUDIT.read_text(encoding="utf-8") if AUDIT.exists() else "")
                + json.dumps({**o, "new_status": args.status}, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            print(f"Done: {o['row_id']} {o['plan_file']}", file=sys.stderr)
        except OSError as exc:
            print(f"FAIL: {o['row_id']} {exc}", file=sys.stderr)
        time.sleep(THROTTLE_S)

    print(f"closed {ok}/{len(orphans)}", file=sys.stderr)
    return 0 if ok == len(orphans) or not orphans else 1


if __name__ == "__main__":
    raise SystemExit(main())
