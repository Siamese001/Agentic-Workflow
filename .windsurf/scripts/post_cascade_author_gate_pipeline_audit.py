#!/usr/bin/env python3
"""
post_cascade_author_gate_pipeline_audit.py — Pipeline-completion audit.

Plan: author-gate-ui-renderer-hardening-a7f3c2 W2.P2.1.

Detects ``AUTHOR_GATE_PACKET:`` (or legacy ``HITL_PACKET:``) emitted in a
Cascade response WITHOUT a same-response ``ask_user_question`` tool call.
This is the **packet-without-ask** direction — the reverse of the sibling
``post_cascade_ask_user_question_packet_audit.py`` (ask-without-packet).

Together they close the enforcement square:
    1. UI shape        → post_cascade_author_gate_ui_audit.py
    2. Hook wiring     → check_ag_hook_wiring.py (CI)
    3. Ask-without-pkt → post_cascade_ask_user_question_packet_audit.py
    4. Pkt-without-ask → THIS FILE

Output: ``artifacts/windsurf/author_gate_pipeline_violations.jsonl``
Bypass: ``AG_PIPELINE_AUDIT_BYPASS=1`` (logs row with reason=bypass).
Fail policy: OPEN (advisory, exits 0).

CONSTITUTIONAL
    - No subprocess / shell.
    - Specific exceptions only.
    - Bounded: response capped at 1 MB before scan.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "windsurf" / "author_gate_pipeline_violations.jsonl"
)
MAX_RESPONSE_BYTES = 1_048_576

# Import the pure helper (same directory).
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))
from _author_gate_pipeline_check import Violation, decide  # noqa: E402


def _append(row: dict[str, Any]) -> None:
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log is non-fatal
        pass


def _read_stdin_text() -> str:
    try:
        raw = sys.stdin.read(MAX_RESPONSE_BYTES + 1)
    except OSError:
        return ""
    if not raw.strip():
        return ""
    if len(raw) > MAX_RESPONSE_BYTES:
        raw = raw[:MAX_RESPONSE_BYTES]
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(payload, dict):
        for key in ("response", "response_text", "text", "assistant_text", "content"):
            val = payload.get(key)
            if isinstance(val, str):
                return val
        return json.dumps(payload, ensure_ascii=False)
    return raw


def main() -> int:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if os.environ.get("AG_PIPELINE_AUDIT_BYPASS") == "1":
        _append({"ts": ts, "reason": "bypass"})
        return 0

    text = _read_stdin_text()
    if not text:
        return 0

    violation: Violation | None = decide(text)
    if violation is not None:
        row: dict[str, Any] = asdict(violation)
        row["ts"] = ts
        _append(row)

    # Advisory: always exit 0 regardless of findings.
    return 0


if __name__ == "__main__":
    sys.exit(main())
