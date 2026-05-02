#!/usr/bin/env python3
"""sync_decision_ledger.py — One-way SQLite -> Notion mirror for the Author-Gate Decision Ledger.

SQLite (.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite) is the
canonical SSOT. The Notion "Author-Gate Decision Ledger" data source is a read-only
human-readable mirror. This script reads new SQLite rows and creates/updates the
corresponding Notion pages.

Idempotency: every Notion page Notes field begins with ``decision_id=<dec_xxxxx>``
on a dedicated first line. The sync queries Notion for existing pages and matches
by decision_id; if a page exists, it is patched (not duplicated).

Watermark: stored at ``.windsurf/state/refactor_decisions/notion_sync_watermark.txt``
as the most recent ``created_at`` ISO timestamp successfully synced. The next run
processes only rows with ``created_at > watermark``.

Usage:
    python tools/notion/sync_decision_ledger.py --dry-run
    python tools/notion/sync_decision_ledger.py --apply
    python tools/notion/sync_decision_ledger.py --apply --since 2026-05-01

Auth: NOTION_TOKEN from environment (or NOTION_API_KEY fallback).
Audit: artifacts/maintenance/decision_ledger_sync.jsonl
Fail policy: SOFT — prints WARN on per-row failures, continues; exit 1 only if any failures.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SQLITE_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
WATERMARK_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "notion_sync_watermark.txt"
AUDIT_LOG = REPO_ROOT / "artifacts" / "maintenance" / "decision_ledger_sync.jsonl"

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
DECISION_LEDGER_DSID = "5b60fdde-7259-491e-9f2d-e088f1f741ef"
DECISION_LEDGER_DBID = "18bb9145-1320-4191-8b14-6c309776bcf5"

RATE_SLEEP = 0.35

# SQLite decision_type -> Notion select option name.
TYPE_MAP = {
    "architecture_choice": "Architecture",
    "refactor_scope": "Refactor",
    "dependency_addition": "Dependency Addition",
    "rule_change": "Rule Change",
    "exception_approval": "Exception Approval",
    "scope_change": "Scope Change",
    "anti_pattern": "Exception Approval",
    "deletion": "Refactor",
    "test_strategy": "Refactor",
    "error_handling": "Refactor",
}


def _headers() -> dict[str, str]:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not tok:
        raise RuntimeError("NOTION_TOKEN not set")
    return {
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _http(method: str, url: str, payload: dict | None = None, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            time.sleep(2 ** attempt)
    raise last_exc if last_exc else RuntimeError("HTTP request failed")


def _read_watermark() -> str | None:
    if not WATERMARK_PATH.exists():
        return None
    try:
        return WATERMARK_PATH.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def _write_watermark(iso_ts: str) -> None:
    WATERMARK_PATH.parent.mkdir(parents=True, exist_ok=True)
    WATERMARK_PATH.write_text(iso_ts + "\n", encoding="utf-8")


def _query_sqlite(since_iso: str | None) -> list[dict]:
    if not SQLITE_PATH.exists():
        return []
    con = sqlite3.connect(str(SQLITE_PATH), timeout=10)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if since_iso:
        cur.execute(
            "SELECT * FROM decisions WHERE created_at > ? ORDER BY created_at ASC",
            (since_iso,),
        )
    else:
        cur.execute("SELECT * FROM decisions ORDER BY created_at ASC")
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows


def _find_existing_notion_page(decision_id: str) -> str | None:
    """Return Notion page_id if a page with this decision_id exists in Notes, else None."""
    payload = {
        "filter": {
            "property": "Notes",
            "rich_text": {"contains": f"decision_id={decision_id}"},
        },
        "page_size": 1,
    }
    resp = _http("POST", f"{NOTION_API}/data_sources/{DECISION_LEDGER_DSID}/query", payload)
    results = resp.get("results", [])
    return results[0]["id"] if results else None


def _build_properties(row: dict, *, for_create: bool) -> dict:
    """Map a SQLite decisions row to Notion page properties."""
    decision_id = row.get("decision_id", "")
    decision_type = row.get("decision_type", "") or "unknown"
    selected = row.get("selected_option_id", "") or ""
    rationale = row.get("selection_rationale", "") or ""
    confidence = row.get("confidence_top")
    created_at = row.get("created_at", "")
    request_summary = row.get("request_summary", "") or ""

    # Title: first line of selected, truncated.
    title_text = selected[:90] if selected else f"Decision {decision_id}"
    if not title_text.strip():
        title_text = f"Decision {decision_id}"

    notion_type = TYPE_MAP.get(decision_type, "Architecture")

    notes_lines = [
        f"decision_id={decision_id}",
        f"sqlite_decision_type={decision_type}",
    ]
    if request_summary:
        notes_lines.append(f"request: {request_summary[:300]}")
    if rationale:
        notes_lines.append(f"rationale: {rationale[:600]}")
    notes_text = "\n".join(notes_lines)[:1900]

    # Decision Date — extract date portion of created_at.
    date_iso = created_at[:10] if created_at and len(created_at) >= 10 else None

    props: dict = {
        "Decision Title": {"title": [{"type": "text", "text": {"content": title_text}}]},
        "Decision Type": {"select": {"name": notion_type}},
        "Option Chosen": {"rich_text": [{"type": "text", "text": {"content": selected[:1900] or "(unrecorded)"}}]},
        "Outcome": {"select": {"name": "Pending Validation"}},
        "Notes": {"rich_text": [{"type": "text", "text": {"content": notes_text or "(no rationale captured)"}}]},
    }
    if confidence is not None:
        try:
            props["Confidence Score"] = {"number": float(confidence)}
        except (TypeError, ValueError):
            pass
    if date_iso:
        props["Decision Date"] = {"date": {"start": date_iso}}

    return props


def sync_one(row: dict, *, apply: bool) -> dict:
    """Sync one SQLite row to Notion. Returns a result dict for the audit log."""
    decision_id = row.get("decision_id", "")
    result: dict = {
        "decision_id": decision_id,
        "action": "skip",
        "notion_page_id": None,
        "error": None,
    }
    try:
        existing_id = _find_existing_notion_page(decision_id)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        result["error"] = f"lookup_failed: {exc}"
        return result

    if existing_id and apply:
        try:
            props = _build_properties(row, for_create=False)
            _http("PATCH", f"{NOTION_API}/pages/{existing_id}", {"properties": props})
            result["action"] = "updated"
            result["notion_page_id"] = existing_id
            time.sleep(RATE_SLEEP)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            result["error"] = f"patch_failed: {exc}"
        return result
    if existing_id:
        result["action"] = "would_update"
        result["notion_page_id"] = existing_id
        return result

    if apply:
        try:
            props = _build_properties(row, for_create=True)
            payload = {"parent": {"type": "database_id", "database_id": DECISION_LEDGER_DBID}, "properties": props}
            resp = _http("POST", f"{NOTION_API}/pages", payload)
            result["action"] = "created"
            result["notion_page_id"] = resp.get("id")
            time.sleep(RATE_SLEEP)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            result["error"] = f"create_failed: {exc}"
    else:
        result["action"] = "would_create"
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--apply", action="store_true", help="Apply changes to Notion (default: dry-run)")
    ap.add_argument("--since", help="Override watermark with explicit ISO timestamp")
    ap.add_argument("--no-watermark-update", action="store_true",
                    help="Don't advance the watermark file even on success")
    args = ap.parse_args(argv)

    since = args.since or _read_watermark()
    print(f"[sync] sqlite={SQLITE_PATH.relative_to(REPO_ROOT)}")
    print(f"[sync] since watermark: {since or '(none — full sync)'}")

    rows = _query_sqlite(since)
    print(f"[sync] {len(rows)} rows to consider")
    if not rows:
        return 0

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    audit_lines: list[str] = []
    counts = {"created": 0, "updated": 0, "would_create": 0, "would_update": 0, "skip": 0, "error": 0}
    last_synced: str | None = since

    for i, row in enumerate(rows, start=1):
        res = sync_one(row, apply=args.apply)
        audit_lines.append(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **res}))
        action = res["action"]
        if res["error"]:
            counts["error"] += 1
            print(f"[sync] {i}/{len(rows)}  ERROR  {res['decision_id']}: {res['error']}", file=sys.stderr)
        else:
            counts[action] = counts.get(action, 0) + 1
            print(f"[sync] {i}/{len(rows)}  {action}  {res['decision_id']}")
            # Advance watermark candidate only on actual success.
            if args.apply and action in ("created", "updated"):
                last_synced = row.get("created_at") or last_synced

    AUDIT_LOG.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    if args.apply and last_synced and not args.no_watermark_update:
        _write_watermark(last_synced)
        print(f"[sync] watermark advanced to: {last_synced}")

    print(f"[sync] summary: {counts}")
    print(f"[sync] audit: {AUDIT_LOG.relative_to(REPO_ROOT)}")
    return 0 if counts["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
