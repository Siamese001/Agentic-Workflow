#!/usr/bin/env python3
"""check_notion_backlog_no_duplicates.py — DS-6: dedup gate for Backlog Items DB.

Queries the Backlog Items DB (live, requires NOTION_TOKEN) and reports any
title that appears in ≥2 non-archived rows. Advisory by default; fail-closed
via BACKLOG_DUP_FAIL_CLOSED=1.

Skips gracefully when NOTION_API_KEY / NOTION_TOKEN is unset (offline CI safe).

Exit codes:
    0 — no duplicates (or token absent → advisory pass)
    1 — duplicates detected
    2 — API error in fail-closed mode

Bypass: BACKLOG_DUP_BYPASS=1 (logged to artifacts/cursor/notion_backlog_dup_violations.jsonl).

DS-6 (notion-plans-db-hygiene-deferred-scope-d4f7c1).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
_WINDSURF_SCRIPTS = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"
if str(_WINDSURF_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_WINDSURF_SCRIPTS))

try:
    from _notion_constants import (  # type: ignore
        NOTION_API_VERSION,
        NOTION_BASE,
        WAVE_PHASE_DATA_SOURCE_ID as BACKLOG_DATA_SOURCE_ID,
    )
except ImportError:
    NOTION_API_VERSION = "2025-09-03"
    NOTION_BASE = "https://api.notion.com/v1"
    BACKLOG_DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"

VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "windsurf" / "notion_backlog_dup_violations.jsonl"
)
TIMEOUT_S = 30.0
_QUERY_URL = f"{NOTION_BASE}/data_sources/{BACKLOG_DATA_SOURCE_ID}/query"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _env_token() -> str | None:
    for key in ("NOTION_TOKEN", "NOTION_API_KEY"):
        v = os.environ.get(key)
        if v:
            return v
    return None


def _is_bypass() -> bool:
    return os.environ.get("BACKLOG_DUP_BYPASS", "").strip() == "1"


def _fail_closed() -> bool:
    return os.environ.get("BACKLOG_DUP_FAIL_CLOSED", "").strip() in {"1", "true", "TRUE", "yes"}


def _log_violation(rec: dict[str, Any]) -> None:
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _title(row: dict[str, Any]) -> str:
    """Extract the display title from a Backlog row (tries common property names)."""
    props = row.get("properties") or {}
    for name in ("Phase Title", "Title", "Name"):
        prop = props.get(name) or {}
        t = prop.get("type")
        if t == "title":
            parts = prop.get("title") or []
        elif t == "rich_text":
            parts = prop.get("rich_text") or []
        else:
            continue
        text = "".join((p.get("plain_text") or "") for p in parts).strip()
        if text:
            return text
    return (row.get("id") or "")[:8]


def _query_all(token: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cursor: str | None = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            _QUERY_URL,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        for row in payload.get("results") or []:
            if row.get("in_trash") or row.get("archived"):
                continue
            rows.append(row)
        if not payload.get("has_more"):
            break
        cursor = payload.get("next_cursor") or None
        if not cursor:
            break
    return rows


def find_duplicate_titles(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Return title → [page_id, ...] for titles with ≥2 rows."""
    by_title: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        title = _title(row)
        page_id = row.get("id", "")
        by_title[title].append(page_id)
    return {t: pids for t, pids in by_title.items() if len(pids) >= 2}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    _ = argv

    if _is_bypass():
        _log_violation({
            "timestamp": _now_iso(),
            "severity": "info",
            "violation_type": "ci_bypass",
            "reason": "BACKLOG_DUP_BYPASS=1",
            "gate": "check_notion_backlog_no_duplicates",
        })
        print("[backlog_dup] BACKLOG_DUP_BYPASS=1 — passing without checking")
        return 0

    token = _env_token()
    if not token:
        print(
            "[backlog_dup] SKIP — NOTION_TOKEN / NOTION_API_KEY not set "
            "(offline CI safe)"
        )
        return 0

    try:
        rows = _query_all(token)
    except urllib.error.HTTPError as exc:
        msg = f"[backlog_dup] ERROR — Notion API HTTP {exc.code}: {exc.reason}"
        print(msg, file=sys.stderr)
        return 2 if _fail_closed() else 0
    except (urllib.error.URLError, OSError) as exc:
        msg = f"[backlog_dup] ERROR — network: {exc!r}"
        print(msg, file=sys.stderr)
        return 2 if _fail_closed() else 0

    dups = find_duplicate_titles(rows)
    if not dups:
        print(
            f"[backlog_dup] OK — no duplicate Backlog Items titles "
            f"({len(rows)} rows checked)"
        )
        return 0

    print(
        f"[backlog_dup] FOUND {len(dups)} duplicate title groups "
        f"({len(rows)} rows checked):\n",
        file=sys.stderr,
    )
    for title, pids in sorted(dups.items()):
        print(f"  {title!r}: {len(pids)} rows", file=sys.stderr)
        for pid in pids:
            print(f"    - {pid}", file=sys.stderr)
        _log_violation({
            "timestamp": _now_iso(),
            "severity": "error",
            "violation_type": "ci_duplicate_group",
            "title": title,
            "page_ids": pids,
            "gate": "check_notion_backlog_no_duplicates",
            "plan": "notion-plans-db-hygiene-deferred-scope-d4f7c1",
        })

    if _fail_closed():
        return 1
    print(
        "\n[backlog_dup] advisory — set BACKLOG_DUP_FAIL_CLOSED=1 to fail-closed",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
