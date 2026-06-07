#!/usr/bin/env python3
"""
post_cascade_plan_complete_audit.py — Warn when Cursor Agent closes a plan without
emitting a PLAN_COMPLETE: marker.

Hook: post_cascade_response (show_output=true).

Heuristic: if the response contains a ``todo_list`` tool call where every item
has ``"status": "completed"``, AND no ``PLAN_COMPLETE:`` marker appears at a
line start in the response text, emit a WARNING to stderr and log to
``artifacts/windsurf/plan_complete_audit.jsonl``.

This is advisory-only — the hook ALWAYS exits 0 regardless of findings. It
never blocks Cursor Agent or the user. Its purpose is visibility: making the
omission obvious so the next response can include the marker.

Bypass: ``PLAN_COMPLETE_AUDIT_BYPASS=1``

Plan: plan-complete-marker-enforcement-d2e9f1 W1.1
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = REPO_ROOT / "artifacts" / "windsurf" / "plan_complete_audit.jsonl"

MAX_RESPONSE_BYTES = 512 * 1024

_PLAN_COMPLETE_LINE_RE = re.compile(r"^\s*PLAN_COMPLETE\s*:", re.MULTILINE)

_TODO_LIST_RE = re.compile(
    r'"todos"\s*:\s*\[(?P<body>[^\]]*)\]',
    re.DOTALL,
)
_STATUS_RE = re.compile(r'"status"\s*:\s*"(?P<val>[^"]+)"')


def _log(event: dict) -> None:
    event.setdefault("ts", datetime.now(timezone.utc).isoformat())
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, dict):
        return ""
    for key in ("response_text", "text", "content"):
        val = payload.get(key)
        if isinstance(val, str) and val:
            return val
    tool_info = payload.get("tool_info")
    if isinstance(tool_info, dict):
        val = tool_info.get("response_text")
        if isinstance(val, str):
            return val
    return ""


def _all_todos_completed(text: str) -> bool:
    """Return True if the response contains a todo_list with all items completed.

    Looks for the ``"todos": [...]`` array inside any ``todo_list`` tool-call
    JSON embedded in the response text. Returns False when no such array is
    found or when any item's status is not ``"completed"``.
    """
    m = _TODO_LIST_RE.search(text)
    if not m:
        return False
    body = m.group("body")
    statuses = _STATUS_RE.findall(body)
    if not statuses:
        return False
    return all(s == "completed" for s in statuses)


def _has_plan_complete_marker(text: str) -> bool:
    """Return True if a PLAN_COMPLETE: marker appears at a line start."""
    return bool(_PLAN_COMPLETE_LINE_RE.search(text))


def main() -> int:
    if os.environ.get("PLAN_COMPLETE_AUDIT_BYPASS") == "1":
        _log({"event": "audit_bypass"})
        return 0

    if sys.stdin.isatty():
        return 0

    try:
        raw = sys.stdin.read(MAX_RESPONSE_BYTES + 1)
    except OSError:
        return 0
    if not raw.strip():
        return 0
    if len(raw) > MAX_RESPONSE_BYTES:
        raw = raw[:MAX_RESPONSE_BYTES]

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"response_text": raw}

    text = _extract_response_text(payload)
    if not text:
        return 0

    if not _all_todos_completed(text):
        return 0

    if _has_plan_complete_marker(text):
        _log({"event": "marker_present_ok"})
        return 0

    msg = (
        "[plan_complete_audit] WARNING: todo list is all-completed but no "
        "PLAN_COMPLETE: marker was emitted in this response. "
        "Add 'PLAN_COMPLETE: plan=<slug-6hex>' as a bare line before closing. "
        "(Bypass: PLAN_COMPLETE_AUDIT_BYPASS=1)"
    )
    print(msg, file=sys.stderr)
    _log({"event": "missing_plan_complete_marker", "warning": msg})

    return 0


if __name__ == "__main__":
    sys.exit(main())
