"""Batch-update ADG Gap Remediation Wave Plan rows to Status=Done.

W0-W13 of plan `adg-gap-remediation-wave-plan-ae5b42` are all complete on disk
(see plan header). This script flips matching Notion rows to Done in one pass,
bypassing per-row MCP serialization.

Usage:
    python tools/_oneshot/notion_mark_adg_gap_remediation_done.py
    python tools/_oneshot/notion_mark_adg_gap_remediation_done.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

NOTION_VERSION = "2025-09-03"
DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
PLAN_FILE_MARKER = "adg-gap-remediation-wave-plan-ae5b42"


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = REPO_ROOT / ".env"
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


def _post(url: str, payload: dict, headers: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _patch(url: str, payload: dict, headers: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _query_all(headers: dict) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
    while True:
        payload = {
            "filter": {
                "property": "Plan File",
                "rich_text": {"contains": PLAN_FILE_MARKER},
            },
            "page_size": 100,
        }
        if cursor:
            payload["start_cursor"] = cursor
        data = _post(url, payload, headers)
        rows.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    headers = _headers(_token())
    rows = _query_all(headers)
    print(f"Found {len(rows)} rows on plan '{PLAN_FILE_MARKER}'")

    target_status = "Done"
    skip_statuses = {"Done", "Descoped", "Complete"}

    flipped = 0
    skipped = 0
    descoped_meta = 0
    for row in rows:
        page_id = row["id"]
        props = row.get("properties", {})
        status_prop = props.get("Status", {}).get("select") or {}
        cur_status = status_prop.get("name", "")
        title_blocks = props.get("Phase Title", {}).get("title", [])
        title = "".join(b.get("plain_text", "") for b in title_blocks)
        wave_blocks = props.get("Wave ID", {}).get("rich_text", [])
        wave_id = "".join(b.get("plain_text", "") for b in wave_blocks)

        # Skip aggregator/meta rows (already Descoped)
        if "AGGREGATE" in title or wave_id == "AGG":
            descoped_meta += 1
            print(f"  SKIP META   {wave_id:6} {title[:70]}")
            continue

        if cur_status in skip_statuses:
            skipped += 1
            print(f"  SKIP DONE   {wave_id:6} [{cur_status}] {title[:70]}")
            continue

        if args.dry_run:
            print(f"  WOULD FLIP  {wave_id:6} [{cur_status}->{target_status}] {title[:70]}")
            flipped += 1
            continue

        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {
            "properties": {
                "Status": {"select": {"name": target_status}},
                "Evidence": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": (
                                    "W0-W13 complete (commit db78fa5aac, 2026-04-30). "
                                    "All 9 active wave exit conditions PASS — "
                                    "P2 ratchet 10->8, M1-M3 enforce, writes ratio 0.815, "
                                    "calls 1228, runtime_trace+covers+reads_secret+hitl_decision+profiler "
                                    "edges populated via tools/adg/integration/*."
                                )
                            },
                        }
                    ]
                },
            }
        }
        try:
            _patch(url, payload, headers)
            flipped += 1
            print(f"  FLIPPED     {wave_id:6} [{cur_status}->{target_status}] {title[:70]}")
        except urllib.error.HTTPError as exc:  # noqa: PERF203
            body = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
            print(f"  ERROR       {wave_id:6} {exc.code} {body[:200]}")

    print()
    print(f"Summary: flipped={flipped}, skipped={skipped}, meta_skipped={descoped_meta}, total={len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
