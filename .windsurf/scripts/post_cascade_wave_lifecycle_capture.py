#!/usr/bin/env python3
"""
post_cascade_wave_lifecycle_capture.py — Capture wave-lifecycle markers.

Hook: post_cascade_response (show_output=false).

Scans the Cascade response for ``WAVE_START:`` / ``WAVE_COMPLETE:`` /
``PHASE_COMPLETE:`` / ``PLAN_COMPLETE:`` markers and applies each as a
direct-HTTP Notion patch via ``tools.notion.wave_lifecycle_writer``. The
writer bypasses the MCP layer entirely — no ``<invoke name="mcp*_API-*">``
tags emitted, so this hook does NOT trip §25 serialization or
``notion-plan-wave-deferral.md``.

Marker grammar (one per line)::

    WAVE_START: plan=<slug-6hex> wave=<N> [note="<short high-signal one-liner>"]
    WAVE_COMPLETE: plan=<slug-6hex> wave=<N> [note="..."]
    PHASE_COMPLETE: plan=<slug-6hex> phase=<id> [note="..."]
    PLAN_COMPLETE: plan=<slug-6hex> [note="..."]

The optional ``note="..."`` field carries a succinct (~240-char cap)
one-liner appended to the Notion Summary column, e.g.::

    WAVE_COMPLETE: plan=foo-abc123 wave=3 note="4 files, +12 tests, scope=summary-signal"

renders as ``[Wave-Log <ts>] W3 DONE — 4 files, +12 tests, scope=summary-signal``
on the Plans DB row's Summary. Without ``note=`` the line stays terse.

Markers MUST start at the beginning of a line (regex anchor ``^``) so
quoted prose mentions are excluded.

Fail policy: OPEN (exit 0 always). Never blocks. Never raises.

Bypass: WAVE_LIFECYCLE_CAPTURE_BYPASS=1.
       WAVE_LIFECYCLE_NOTION_BYPASS=1 (writer-side; logs but doesn't PATCH).

Constitutional ties: §25 (preserved), §35 (preserved), §36 (extended).

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W3.P3.1).
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = REPO_ROOT / "artifacts" / "windsurf" / "wave_lifecycle_capture.jsonl"
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB


def _log(event: dict[str, Any]) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **event,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
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


def _load_writer():
    """Lazy-import the writer so a missing module never breaks the hook."""
    sys.path.insert(0, str(REPO_ROOT))
    try:
        return importlib.import_module("tools.notion.wave_lifecycle_writer")
    except ImportError as exc:
        _log({"event": "writer_import_failed", "error": repr(exc)})
        return None


def main() -> int:
    if os.environ.get("WAVE_LIFECYCLE_CAPTURE_BYPASS") == "1":
        _log({"event": "capture_bypass"})
        return 0

    if sys.stdin.isatty():
        # Standalone-invocation guard: avoid hanging on inherited stdin.
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

    writer = _load_writer()
    if writer is None:
        return 0

    try:
        rows = writer.emit_from_markers(text, dry_run=False)
    except (OSError, ValueError) as exc:
        _log({"event": "emit_from_markers_failed", "error": repr(exc)})
        return 0

    if not rows:
        return 0

    captured = sum(1 for _slug, ok, _msg in rows if ok)
    failed = sum(1 for _slug, ok, _msg in rows if not ok)

    _log(
        {
            "event": "capture_summary",
            "captured": captured,
            "failed": failed,
            "rows": [{"slug": s, "ok": ok, "msg": m} for s, ok, m in rows],
        }
    )

    if captured or failed:
        print(
            f"[wave_lifecycle_capture] applied {captured} marker(s); "
            f"{failed} failed (see artifacts/windsurf/wave_lifecycle_capture.jsonl)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
