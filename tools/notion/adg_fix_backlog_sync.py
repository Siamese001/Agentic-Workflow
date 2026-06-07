#!/usr/bin/env python3
"""Sync FIX-only rows from adg_action_queue JSON to Notion Backlog Items (Wave/Phase).

Optional, non-certification tooling (plan adg-action-dispatch-c9e4a2 W3).
Never wired into generate_full_adg required path.

Usage (repo root, PYTHONPATH=.):
  python tools/notion/adg_fix_backlog_sync.py --latest --dry-run
  python tools/notion/adg_fix_backlog_sync.py --queue artifacts/adg/adg_action_queue_<ts>.json --apply

Auth:
  NOTION_TOKEN missing → exit 0, stderr SKIP_NOTION_TOKEN_MISSING
  --apply + API failure → exit nonzero
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_HTTP_TIMEOUT_S,
    NOTION_POST_URL,
    PLANS_DATA_SOURCE_ID,
    WAVE_PHASE_DATA_SOURCE_ID,
    WAVE_PHASE_DB_ID,
)
from tools.notion.notion_bearer_token import get_notion_bearer_token
from tools.reports.adg_action_queue import extract_notion_fix_rows

PLAN_SLUG = "adg-action-dispatch-c9e4a2"
PLAN_FILE = ".claude/plans/adg-action-dispatch-c9e4a2.md"
WAVE_ID = "ADG-FIX"
AUDIT_LOG = REPO_ROOT / "artifacts" / "maintenance" / "adg_fix_backlog_sync.jsonl"
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
SKIP_MSG = "SKIP_NOTION_TOKEN_MISSING"

BAND_TO_P_BAND: dict[str, str] = {
    "P0": "P1",
    "P1": "P1",
    "P2": "P2",
    "P3": "P3",
    "P4": "P4",
    "P5": "P5",
}


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _resolve_latest_queue() -> Path:
    candidates = sorted(ARTIFACTS_ADG.glob("adg_action_queue_*.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise SystemExit("ERROR: no adg_action_queue_*.json under artifacts/adg")
    return candidates[-1]


def _load_queue(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _notion_query(data_source_id: str, body: dict[str, Any], token: str) -> dict[str, Any]:
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8") or "{}")


def _notion_post_page(payload: dict[str, Any], token: str) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        NOTION_POST_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8") or "{}")


def _resolve_plan_page_id(token: str) -> str | None:
    for filt in (
        {"property": "Slug", "rich_text": {"equals": PLAN_SLUG}},
        {"property": "Plan File Path", "rich_text": {"contains": PLAN_SLUG}},
        {"property": "Name", "title": {"contains": PLAN_SLUG}},
    ):
        try:
            data = _notion_query(PLANS_DATA_SOURCE_ID, {"filter": filt, "page_size": 1}, token)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
        ):
            return None
        results = data.get("results") or []
        if results:
            return results[0].get("id")
    return None


def _row_exists(idempotency_key: str, token: str) -> bool:
    """Fail-open duplicate check on Phase ID + Wave ID ADG-FIX."""
    query = {
        "filter": {
            "and": [
                {"property": "Phase ID", "rich_text": {"equals": idempotency_key}},
                {"property": "Wave ID", "rich_text": {"equals": WAVE_ID}},
            ]
        },
        "page_size": 3,
    }
    try:
        data = _notion_query(WAVE_PHASE_DATA_SOURCE_ID, query, token)
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
    ):
        return False
    closed = {"Done", "Closed", "Cancelled", "Archived", "Completed"}
    for page in data.get("results") or []:
        if page.get("archived") or page.get("in_trash"):
            continue
        status = (
            (page.get("properties") or {})
            .get("Status", {})
            .get("select", {})
            .get("name", "")
        )
        if status not in closed:
            return True
    return False


def build_backlog_page_payload(
    row: dict[str, Any],
    *,
    plan_page_id: str | None = None,
) -> dict[str, Any]:
    gate_id = row["gate_id"]
    signal = str(row.get("signal") or "")[:1800]
    band = BAND_TO_P_BAND.get(str(row.get("sort_band") or "P3"), "P3")
    evidence = (
        f"ADG FIX dispatch (adg-action-dispatch W3). "
        f"Rank={row.get('rank')} ordering={row.get('ordering_reason')} "
        f"violations={row.get('violation_count')}. "
        f"Idempotency={row['idempotency_key']}. "
        f"| Signal: {signal}"
    )
    properties: dict[str, Any] = {
        "Phase Title": {
            "title": [{"text": {"content": f"ADG FIX: {gate_id}"}}],
        },
        "Phase ID": {
            "rich_text": [{"text": {"content": row["idempotency_key"]}}],
        },
        "Wave ID": {"rich_text": [{"text": {"content": WAVE_ID}}]},
        "Plan File": {"rich_text": [{"text": {"content": PLAN_FILE}}]},
        "P-Band": {"select": {"name": band}},
        "Layer": {"select": {"name": "L_"}},
        "Surface": {"select": {"name": "Observability"}},
        "Status": {"select": {"name": "Not Started"}},
        "Est Tokens": {"number": 0},
        "Last Updated": {"date": {"start": _utc_today()}},
        "Evidence": {"rich_text": [{"text": {"content": evidence}}]},
    }
    if plan_page_id:
        properties["Plan"] = {"relation": [{"id": plan_page_id}]}
    return {"parent": {"database_id": WAVE_PHASE_DB_ID}, "properties": properties}


def sync_fix_rows(
    rows: list[dict[str, Any]],
    *,
    apply: bool,
    token: str | None,
) -> dict[str, Any]:
    """Dry-run or apply FIX backlog sync. Never includes TRACK."""
    assert all("TRACK" not in str(r.get("gate_id", "")) for r in rows)
    result: dict[str, Any] = {
        "mode": "apply" if apply else "dry_run",
        "fix_rows": len(rows),
        "skipped_existing": 0,
        "created": 0,
        "errors": [],
        "payloads": [],
    }
    if not token:
        result["skip"] = SKIP_MSG
        return result

    plan_page_id = _resolve_plan_page_id(token) if apply else None
    for row in rows:
        key = row["idempotency_key"]
        if apply and _row_exists(key, token):
            result["skipped_existing"] += 1
            continue
        payload = build_backlog_page_payload(row, plan_page_id=plan_page_id)
        result["payloads"].append(
            {
                "gate_id": row["gate_id"],
                "idempotency_key": key,
                "phase_title": payload["properties"]["Phase Title"]["title"][0]["text"]["content"],
            }
        )
        if not apply:
            continue
        try:
            resp = _notion_post_page(payload, token)
            result["created"] += 1
            _append_audit(
                {
                    "ok": True,
                    "gate_id": row["gate_id"],
                    "idempotency_key": key,
                    "page_id": resp.get("id"),
                }
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
        ) as exc:
            result["errors"].append({"gate_id": row["gate_id"], "error": str(exc)})
            _append_audit({"ok": False, "gate_id": row["gate_id"], "error": str(exc)})

    return result


def _append_audit(record: dict[str, Any]) -> None:
    record["ts"] = datetime.now(timezone.utc).isoformat()
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync ADG FIX queue rows to Notion Backlog Items.")
    parser.add_argument("--queue", type=Path, help="Path to adg_action_queue JSON")
    parser.add_argument("--latest", action="store_true", help="Use latest artifacts/adg/adg_action_queue_*.json")
    parser.add_argument("--dry-run", action="store_true", help="Build payloads only (default)")
    parser.add_argument("--apply", action="store_true", help="POST new rows to Notion")
    args = parser.parse_args(argv)

    if not args.queue and not args.latest:
        parser.error("specify --queue PATH or --latest")

    queue_path = args.queue.resolve() if args.queue else _resolve_latest_queue()
    doc = _load_queue(queue_path)
    rows = extract_notion_fix_rows(doc)

    token = get_notion_bearer_token() or None
    if not token:
        print(SKIP_MSG, file=sys.stderr)
        summary = sync_fix_rows(rows, apply=False, token=None)
        print(json.dumps(summary, indent=2))
        return 0

    if args.apply and args.dry_run:
        parser.error("use either --apply or --dry-run, not both")
    apply = bool(args.apply)

    summary = sync_fix_rows(rows, apply=apply, token=token)
    print(json.dumps(summary, indent=2))

    if summary.get("errors"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
