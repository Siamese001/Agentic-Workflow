#!/usr/bin/env python3
"""
post_agent_wave_completion_audit.py — Audit wave marker presence.

Hook: post_agent_response (show_output=true).

Heuristic check: if substantial file writes (≥3 files) occurred in
agentic_core/, apps_*/, or tests/ AND no WAVE_COMPLETE / WAVE_START
marker is present in the response, emit advisory warning.

Fires unconditionally — does NOT require wave_execution_state.py start
to have been called first. This closes GAP-1 (RCA rca-wave-marker-
emission-gap-c7d3f1): the _has_active_plan() guard was the reason the
auditor silenced itself when wave_execution_state.py start was skipped.

Fail policy: OPEN (exit 0 always). Advisory only.

Bypass: WAVE_COMPLETION_AUDIT_BYPASS=1.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
LOG_PATH = REPO_ROOT / "artifacts" / "governance" / "wave_completion_audit.jsonl"
MAX_RESPONSE_BYTES = 1_048_576

# Paths that indicate "wave-like work"
WAVE_WORK_PATHS = ["agentic_core/", "apps_", "tests/"]

# Pattern for substantial file-write evidence (edit/write_file/write_to_file calls).
# Widened in rca-wave-marker-emission-gap-c7d3f1 W1.P3 (GAP-3) to catch the
# actual tool-call shapes Windsurf emits in the response text.
EDIT_PATTERNS = [
    # Native edit tool: <file_path>...</file_path> XML shape
    re.compile(r"<file_path>[^<]+</file_path>"),
    # write_to_file: TargetFile parameter
    re.compile(r'"TargetFile"\s*:\s*"[^"]+"'),
    # multi_edit / edit: file_path parameter key
    re.compile(r'"file_path"\s*:\s*"[^"]+"'),
    # Fallback: any invocation of edit/write_to_file tool names
    re.compile(r'<invoke name="(?:edit|write_to_file|multi_edit)">'),
]


def _log(event: dict[str, Any]) -> None:
    event = {
        "timestamp": datetime_now(),
        **event,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def datetime_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_response_text(payload: Any) -> str:
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


def _count_file_writes(text: str) -> int:
    """Count likely file-write operations in the response."""
    count = 0
    for pattern in EDIT_PATTERNS:
        count += len(pattern.findall(text))
    return count


def _has_wave_markers(text: str) -> bool:
    """Check for WAVE_COMPLETE or WAVE_START markers."""
    return bool(re.search(r"^WAVE_(COMPLETE|START):", text, re.MULTILINE))


def main() -> int:
    if os.environ.get("WAVE_COMPLETION_AUDIT_BYPASS") == "1":
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

    write_count = _count_file_writes(text)
    has_markers = _has_wave_markers(text)

    _log({
        "event": "audit_scan",
        "write_count": write_count,
        "has_markers": has_markers,
    })

    # Advisory: substantial work without markers
    if write_count >= 3 and not has_markers:
        msg = (
            f"[wave_completion_audit] ADVISORY: {write_count} file operations detected "
            f"without WAVE_COMPLETE/WAVE_START marker. "
            f"Emit marker at wave boundaries to keep plan .md and Notion in sync. "
            f"Bypass: WAVE_COMPLETION_AUDIT_BYPASS=1"
        )
        print(msg, file=sys.stderr)
        _log({"event": "advisory_issued", "write_count": write_count})

    return 0


if __name__ == "__main__":
    sys.exit(main())
