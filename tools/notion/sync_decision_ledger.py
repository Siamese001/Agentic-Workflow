#!/usr/bin/env python3
"""sync_decision_ledger.py — RETIRED 2026-05-02 (no-op stub).

The Notion "HITL / Author-Gate Decision Ledger" mirror DB was retired on
2026-05-02 because SQLite at
``.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`` is the
canonical SSOT (constitutional §30) and the Notion projection added no unique
data — every mirror row carried ``decision_id=dec_xxxxx`` derived from the
SQLite chain. The Notion DB was deleted from the workspace; running this
script would error against a now-missing data source.

This file is preserved as a no-op stub so older docs / cron entries / muscle-
memory invocations exit cleanly with a deprecation message. Delete entirely
in a future cleanup wave once no callers remain.

If decision-history search is needed: query the SQLite FTS index directly,
e.g. ``SELECT decision_id, selected_option_id FROM decisions_fts
WHERE decisions_fts MATCH 'shell=True'``.

Original docstring follows for historical reference:

One-way SQLite -> Notion mirror for the Author-Gate Decision Ledger.

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

from tools.refactor_decisions.ledger_paths import (
    REFACTOR_DECISION_LEDGER_DB,
    REFACTOR_DECISIONS_DIR_SSO,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SQLITE_PATH = REFACTOR_DECISION_LEDGER_DB
WATERMARK_PATH = REFACTOR_DECISIONS_DIR_SSO / "notion_sync_watermark.txt"
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


_RETIRED_MSG = (
    "[sync_decision_ledger] RETIRED 2026-05-02 — Notion HITL/Author-Gate "
    "Decision Ledger mirror DB was deleted. SQLite at "
    ".windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite is the "
    "SSOT (constitutional §30). This script is now a no-op. "
    "See config/notion_databases.yaml retirement comment for context."
)


def main(argv: list[str] | None = None) -> int:  # noqa: ARG001 — preserved signature
    print(_RETIRED_MSG, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
