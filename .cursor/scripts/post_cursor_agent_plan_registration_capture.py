#!/usr/bin/env python3
"""
post_cursor_agent_plan_registration_capture.py — Capture PLAN_CREATED markers.

Hook: post_cursor_agent_response (show_output=false).

Scans the Cursor Agent response for ``PLAN_CREATED:`` markers and appends each
to ``.cursor/state/plan_registration_queue.jsonl``. Idempotent — re-running
on the same response does not create duplicates (enqueue is slug-keyed).

Marker grammar (one per line)::

    PLAN_CREATED: slug=<slug-6hex> path=<repo-relative-path> status=Not Started|In Progress

``path`` defaults to ``.cursor/plans/<slug>.md``. ``status`` defaults to
``Not Started``.

Fail policy: OPEN (exit 0). Never blocks. Bypass: PLAN_REGISTRATION_CAPTURE_BYPASS=1.

Constitutional tie-in: §36.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf" / "_plan_registration.py"
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB


def _load_helper():
    if not HELPER_PATH.exists():
        return None
    mod_name = "_plan_registration"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    try:
        spec = importlib.util.spec_from_file_location(mod_name, HELPER_PATH)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(mod_name, None)
            raise
        return mod
    except (OSError, ImportError):
        return None


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
    if os.environ.get("PLAN_REGISTRATION_CAPTURE_BYPASS") == "1":
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

    helper = _load_helper()
    if helper is None:
        return 0

    try:
        markers = helper.parse_plan_created_markers(text)
    except (AttributeError, TypeError):
        return 0

    if not markers:
        return 0

    captured = 0
    for m in markers:
        try:
            if helper.enqueue_plan(m["slug"], m["path"], m.get("status", "Not Started")):
                captured += 1
        except (OSError, ValueError):
            continue

    if captured:
        print(
            f"[plan_registration_capture] queued {captured} PLAN_CREATED marker(s); "
            f"register via API-post-page to Plans DB before wave execution.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
