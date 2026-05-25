#!/usr/bin/env python3
"""
unified_notion_status_auditor.py — Consolidated Notion Plans DB status auditor (W2.P1).

SSOT implementation. Thin entrypoints live at:

- ``.cursor/scripts/unified_notion_status_auditor.py`` (sets vendor ``cursor``)
- ``.windsurf/scripts/unified_notion_status_auditor.py`` (sets vendor ``windsurf``)

Violations log path: ``artifacts/<vendor>/notion_plans_status_violations.jsonl`` where
``vendor`` is ``NOTION_STATUS_VIOLATIONS_VENDOR`` (``cursor`` or ``windsurf``, default ``cursor``).

Merges legacy post-flight status drift detection + SHADOW_REQUIRED shim behavior.

Behavior preservation:
- Detects non-canonical Status writes to Plans/Backlog DBs
- Auto-patches stale statuses when possible
- Adds Waiting For reminders for "Waiting" status
- Advisory only — always exits 0, never blocks

Bypass: ``NOTION_PLANS_STATUS_BYPASS=1``
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.notion.notion_bearer_token import get_notion_bearer_token

REPO_ROOT = Path(__file__).resolve().parents[2]
_CURSOR_SCRIPTS = REPO_ROOT / ".cursor" / "scripts"
if str(_CURSOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CURSOR_SCRIPTS))

from _notion_plans_status_check import (  # noqa: E402
    BACKLOG_DATA_SOURCE_ID,
    BACKLOG_DB_ID,
    CANONICAL_STATUSES,
    PLANS_DATA_SOURCE_ID,
    PLANS_DB_ID,
    STALE_EQUIVALENTS,
)

# Notion API constants
_NOTION_API = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"
_TIMEOUT = 15.0


def _violations_log_path() -> Path:
    vendor = (os.environ.get("NOTION_STATUS_VIOLATIONS_VENDOR") or "cursor").strip().lower()
    if vendor not in {"cursor", "windsurf"}:
        vendor = "cursor"
    return REPO_ROOT / "artifacts" / vendor / "notion_plans_status_violations.jsonl"


# Regex patterns
_INVOKE_BLOCK_RE = re.compile(
    r'<invoke\s+name="(?:mcp\d+_)?(API-(?:post|patch)-page)">(.*?)</invoke>',
    re.DOTALL,
)
_STATUS_SELECT_RE = re.compile(
    r'["\']Status["\']\s*:\s*\{\s*["\']select["\']\s*:\s*\{\s*["\']name["\']\s*:'
    r'\s*["\']([^"\']+)["\']',
    re.DOTALL,
)
_DB_ID_RE = re.compile(
    r'["\'](?:database_id|data_source_id)["\']\s*:\s*["\']([0-9a-fA-F\-]+)["\']'
)
_SLUG_RE = re.compile(
    r'["\'](?:Slug|title)["\']\s*:\s*\{[^}]*["\']content["\']\s*:\s*["\']([^"\']+)["\']',
    re.DOTALL,
)
_WAITING_FOR_RE = re.compile(
    r'["\']Waiting\s+For["\']\s*:\s*\{[^}]*["\']rich_text["\']\s*:\s*\[.*?'
    r'["\']content["\']\s*:\s*["\']([^"\']*)["\']',
    re.DOTALL,
)


def _notion_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_notion_bearer_token()}",
        "Content-Type": "application/json",
        "Notion-Version": _NOTION_VERSION,
    }


def _is_plans_or_backlog_id(candidate: str) -> bool:
    """Return True when candidate targets Plans or Backlog DB."""
    norm = candidate.replace("-", "").lower()
    return norm in {
        PLANS_DB_ID.replace("-", "").lower(),
        PLANS_DATA_SOURCE_ID.replace("-", "").lower(),
        BACKLOG_DB_ID.replace("-", "").lower(),
        BACKLOG_DATA_SOURCE_ID.replace("-", "").lower(),
    }


def _canonical_for(status: str) -> str | None:
    """Return canonical status for stale status, or None if already canonical."""
    if status in CANONICAL_STATUSES:
        return None
    return STALE_EQUIVALENTS.get(status)


def _log_violation(violation: dict[str, Any]) -> None:
    """Append violation to log file."""
    path = _violations_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(violation, default=str) + "\n")


def _find_page_id_by_slug(slug: str) -> str:
    """Query Plans DB for page_id by slug."""
    tok = get_notion_bearer_token()
    if not tok:
        return ""
    url = f"{_NOTION_API}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
    body = json.dumps({
        "filter": {"property": "Slug", "title": {"equals": slug}},
        "page_size": 1,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers=_notion_headers())
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results", [])
        return results[0]["id"] if results else ""
    except Exception:
        return ""


def _patch_status(page_id: str, canonical_status: str) -> bool:
    """PATCH page to canonical status."""
    tok = get_notion_bearer_token()
    if not tok or not page_id:
        return False
    url = f"{_NOTION_API}/pages/{page_id}"
    body = json.dumps({
        "properties": {"Status": {"select": {"name": canonical_status}}}
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH", headers=_notion_headers())
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.status < 300
    except Exception:
        return False


def _append_waiting_reminder(page_id: str) -> bool:
    """Append Waiting For reminder block to page."""
    tok = get_notion_bearer_token()
    if not tok or not page_id:
        return False
    url = f"{_NOTION_API}/blocks/{page_id}/children"
    body = json.dumps({
        "children": [{
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": (
                            "⚠️ This plan is Waiting. Please populate the "
                            "'Waiting For' property above with the specific "
                            "blocker before leaving this page."
                        )
                    },
                    "annotations": {"bold": True, "color": "orange"},
                }]
            },
        }]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH", headers=_notion_headers())
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.status < 300
    except Exception:
        return False


def _auto_patch_violation(violation: dict[str, Any], invoke_body: str) -> dict[str, Any]:
    """Attempt to auto-heal stale status violation."""
    canonical = violation.get("suggested")
    if not canonical:
        return {"auto_patch": "skipped", "reason": "no_suggested_canonical"}

    slug_match = _SLUG_RE.search(invoke_body)
    if not slug_match:
        return {"auto_patch": "skipped", "reason": "slug_not_found"}

    slug = slug_match.group(1)
    page_id = _find_page_id_by_slug(slug)

    if not page_id:
        return {"auto_patch": "skipped", "reason": "page_id_not_found", "slug": slug}

    patched = _patch_status(page_id, canonical)
    result = {
        "auto_patch": "patched" if patched else "failed",
        "slug": slug,
        "page_id": page_id,
        "canonical": canonical,
    }

    if patched and canonical == "Waiting":
        reminder_ok = _append_waiting_reminder(page_id)
        result["reminder_appended"] = reminder_ok

    return result


def _detect_violations(response_text: str) -> list[dict[str, Any]]:
    """Detect all status violations in agent response text."""
    violations = []
    now = datetime.now(timezone.utc).isoformat()

    for invoke_match in _INVOKE_BLOCK_RE.finditer(response_text):
        invoke_type = invoke_match.group(1)
        invoke_body = invoke_match.group(2)

        db_match = _DB_ID_RE.search(invoke_body)
        if not db_match:
            continue

        db_id = db_match.group(1)
        if not _is_plans_or_backlog_id(db_id):
            continue

        status_match = _STATUS_SELECT_RE.search(invoke_body)
        if not status_match:
            continue

        status_value = status_match.group(1)

        suggested = _canonical_for(status_value)
        if suggested is None:
            continue

        waiting_for_populated = False
        if status_value == "Waiting" or suggested == "Waiting":
            wf_match = _WAITING_FOR_RE.search(invoke_body)
            if wf_match:
                wf_content = wf_match.group(1).strip()
                waiting_for_populated = bool(wf_content)

        violation = {
            "timestamp": now,
            "detected_in": invoke_type,
            "status_written": status_value,
            "suggested": suggested,
            "db_target": db_id[:8] + "...",
            "waiting_for_populated": waiting_for_populated,
        }

        patch_result = _auto_patch_violation(violation, invoke_body)
        violation["auto_patch"] = patch_result

        violations.append(violation)

    return violations


def main() -> int:
    """Read agent response JSON from stdin; advisory; always exits 0 unless bypass early."""
    if os.environ.get("NOTION_PLANS_STATUS_BYPASS") == "1":
        print("[unified-status-auditor] BYPASS: NOTION_PLANS_STATUS_BYPASS=1", file=sys.stderr)
        return 0

    try:
        data = sys.stdin.read()
    except Exception:
        return 0

    if not data:
        return 0

    try:
        payload = json.loads(data)
        response_text = payload.get("response_text", "")
    except json.JSONDecodeError:
        response_text = data

    if not response_text:
        return 0

    violations = _detect_violations(response_text)

    for v in violations:
        _log_violation(v)
        print(
            f"[STATUS_VIOLATION] {v['status_written']} -> {v['suggested']} "
            f"(auto_patch: {v['auto_patch']['auto_patch']})",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
