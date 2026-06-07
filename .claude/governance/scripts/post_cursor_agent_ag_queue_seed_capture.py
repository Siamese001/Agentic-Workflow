#!/usr/bin/env python3
"""
post_cursor_agent_ag_queue_seed_capture.py — Capture AG_QUEUE_SEED markers.

Hook: post_cursor_agent_response (show_output=false).

Scans the Cursor Agent response for `AG_QUEUE_SEED:` markers and writes each
into the corresponding plan's queue JSONL. Idempotent — re-running on
the same response does not create duplicates (enqueue is id-keyed).

Marker grammar (one per line)::

    AG_QUEUE_SEED: plan=<slug> id=<packet_id> depends_on=<id1,id2> title=<short>

`depends_on` optional (default empty). `title` may contain spaces — it
runs to end-of-line. Unknown fields ignored.

Fail policy: OPEN (exit 0). Never blocks. Bypass: AG_QUEUE_SEED_BYPASS=1.

Constitutional tie-in: §35.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "_author_gate_queue.py"
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB

# Capture marker — accepts both raw AG_QUEUE_SEED and leading whitespace
_SEED_RE = re.compile(
    r"^\s*AG_QUEUE_SEED\s*:\s*(?P<body>.+?)\s*$",
    re.MULTILINE,
)

# Field extractors within the body. Splits on lookahead-of-next-key so that
# empty values (e.g. "depends_on= title=foo") yield a clean empty string.
_KV_RE = re.compile(
    r"\b(?P<key>plan|id|depends_on|title)="
    r"(?P<val>.*?)"
    r"(?=\s+(?:plan|id|depends_on|title)=|\s*$)",
    re.DOTALL,
)


def _load_helper():
    if not HELPER_PATH.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("_ag_queue", HELPER_PATH)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except (OSError, ImportError):
        return None


def _parse_marker(body: str) -> dict[str, Any] | None:
    """Parse a marker body. Returns None if required fields missing."""
    fields: dict[str, str] = {}
    for m in _KV_RE.finditer(body):
        fields[m.group("key")] = m.group("val").strip()
    if "plan" not in fields or "id" not in fields or "title" not in fields:
        return None
    depends_on_raw = fields.get("depends_on", "").strip()
    if depends_on_raw in ("", "(none)", "none", "-"):
        depends_on: list[str] = []
    else:
        depends_on = [d.strip() for d in depends_on_raw.split(",") if d.strip()]
    return {
        "plan": fields["plan"],
        "id": fields["id"],
        "depends_on": depends_on,
        "title": fields["title"],
    }


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
    if os.environ.get("AG_QUEUE_SEED_BYPASS") == "1":
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

    markers = _SEED_RE.findall(text)
    if not markers:
        return 0

    helper = _load_helper()
    if helper is None:
        return 0

    seeded = 0
    for body in markers:
        parsed = _parse_marker(body)
        if parsed is None:
            continue
        try:
            helper.enqueue(
                parsed["plan"],
                {
                    "id": parsed["id"],
                    "title": parsed["title"],
                    "depends_on": parsed["depends_on"],
                },
            )
            seeded += 1
        except (OSError, ValueError):
            continue

    if seeded:
        print(
            f"[ag_queue_seed_capture] seeded {seeded} packet(s) from markers",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
