#!/usr/bin/env python3
"""
post_cursor_agent_ag_queue_drain_audit.py — Author-Gate queue drain audit.

Hooks post_cursor_agent_response. Detects the "completed a wave but did not
emit the next queued AUTHOR_GATE_PACKET" failure mode, which the
2026-05-03 session demonstrated is Cursor Agent's default behavioral gap.

Logic:
    1. Read response from stdin (JSON payload or raw text).
    2. Scan for wave/phase completion markers:
         - `WAVE_COMPLETE:`
         - `PHASE_COMPLETE:`
         - `wave_execution_state.py complete`
         - A wave-row line flipping to `✅ DONE` in a plan edit
    3. If completion marker present AND at least one plan has pending
       packets (via `_author_gate_queue.list_plans_with_pending()`)
       AND response does NOT contain `AUTHOR_GATE_PACKET:` or legacy
       `HITL_PACKET:` block → log violation.

Log: artifacts/cursor/ag_queue_drain_violations.jsonl (append-only).

Fail policy: OPEN (exit 0). AUDIT ONLY — never blocks the turn.
Bypass: AG_QUEUE_DRAIN_BYPASS=1 emits a row with reason="bypass" and
treats the response as compliant.

Constitutional tie-in: §35.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATION_LOG = REPO_ROOT / "artifacts" / "cursor" / "ag_queue_drain_violations.jsonl"
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB

# Completion-marker patterns — detect the response just flipped a wave/phase done.
_COMPLETION_PATTERNS = (
    re.compile(r"\bWAVE_COMPLETE\s*:", re.IGNORECASE),
    re.compile(r"\bPHASE_COMPLETE\s*:", re.IGNORECASE),
    re.compile(r"wave_execution_state\.py\s+complete", re.IGNORECASE),
    # Plan edit flipping a Wave Structure row to DONE
    re.compile(r"\|\s*Wave\s*\d+\s*\|[^\|]*\|[^\|]*\|[^\|]*\|\s*~?[\dK]+\s*✅"),
)

# Packet presence — any one proves the drain obligation is satisfied.
_PACKET_PRESENT = (
    re.compile(r"\bAUTHOR_GATE_PACKET\s*:", re.IGNORECASE),
    re.compile(r"\bHITL_PACKET\s*:", re.IGNORECASE),  # legacy alias
)


def _load_queue_helper():
    """Lazy-import the SSOT helper via importlib (avoids sys.path fiddling)."""
    helper_path = REPO_ROOT / ".claude" / "governance/scripts" / "_author_gate_queue.py"
    if not helper_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("_ag_queue", helper_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except (OSError, ImportError):
        return None


def _has_completion_marker(text: str) -> list[str]:
    hits: list[str] = []
    for pat in _COMPLETION_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


def _has_packet(text: str) -> bool:
    return any(p.search(text) for p in _PACKET_PRESENT)


def _append_violation(record: dict[str, Any]) -> None:
    try:
        VIOLATION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATION_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log write failure: fail-open
        pass


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


def main() -> int:
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

    completion_hits = _has_completion_marker(text)
    if not completion_hits:
        return 0

    helper = _load_queue_helper()
    if helper is None:
        return 0

    try:
        pending_plans = helper.list_plans_with_pending()
    except (OSError, ValueError):
        pending_plans = []

    if not pending_plans:
        return 0

    if _has_packet(text):
        return 0  # Drain obligation satisfied

    bypass = os.environ.get("AG_QUEUE_DRAIN_BYPASS") == "1"
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cascade_id": payload.get("cascade_id") or payload.get("session_id")
            if isinstance(payload, dict) else None,
        "completion_markers": completion_hits,
        "pending_plans": pending_plans,
        "severity": "high",
        "reason": "bypass" if bypass else "no_packet_after_completion",
        "response_excerpt": text[:500],
    }
    _append_violation(record)

    if not bypass:
        print(
            f"[ag_queue_drain_audit] ADVISORY violation: "
            f"completion marker present ({completion_hits[0]}) but no "
            f"AUTHOR_GATE_PACKET emitted; pending plans: {pending_plans}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
