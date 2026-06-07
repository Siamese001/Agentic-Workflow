"""Token-telemetry handler - per-turn token-cost telemetry.

In-process equivalent of `.claude/governance/scripts/post_cursor_agent_token_telemetry.py`.
Logs a row to `artifacts/cursor/turn_budget.jsonl` for every Cursor Agent response.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import ParsedResponse

_INVOKE_PAT = re.compile(r'<invoke\s+name="([^"]+)"', re.IGNORECASE)

_MARKER_PATS = {
    "DECISION_CAPTURED": re.compile(r'DECISION_CAPTURED:', re.IGNORECASE),
    "DEFERRED_SCOPE": re.compile(r'DEFERRED_SCOPE:', re.IGNORECASE),
    "NEXT_STEP": re.compile(r'NEXT_STEP:', re.IGNORECASE),
    "SCOPE_RESET": re.compile(r'SCOPE_RESET:', re.IGNORECASE),
    "ROUTER_DECISION": re.compile(r'ROUTER_DECISION:', re.IGNORECASE),
    "DEGRADED_FALLBACK": re.compile(r'DEGRADED_FALLBACK:', re.IGNORECASE),
}


def _approx_tokens(s: str) -> int:
    return max(0, len(s) // 4)


def _count_tool_calls(text: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for match in _INVOKE_PAT.finditer(text):
        counts[match.group(1)] += 1
    return dict(counts)


def _count_markers(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for name, pat in _MARKER_PATS.items():
        n = len(pat.findall(text))
        if n > 0:
            out[name] = n
    return out


def _append(path: Path, row: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError as err:
        print(f"[token-telemetry] write failed: {err}", file=sys.stderr)


def run(parsed: ParsedResponse, repo_root: Path) -> None:
    if os.environ.get("TOKEN_TELEMETRY_DISABLED", "").strip() == "1":
        return

    raw = parsed.raw or ""
    response_text = parsed.response_text or raw
    if not raw:
        return

    tool_counts = _count_tool_calls(response_text)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "approx_response_tokens": _approx_tokens(response_text),
        "approx_payload_tokens": _approx_tokens(raw),
        "response_bytes": len(response_text),
        "payload_bytes": len(raw),
        "tool_call_counts": tool_counts,
        "tool_call_total": sum(tool_counts.values()),
        "marker_counts": _count_markers(response_text),
        "approximation_note": "tokens = bytes/4 (Claude tokenizer ratio varies 3-5x)",
        "via": "dispatcher",
    }
    log_path = repo_root / "artifacts" / "cursor" / "turn_budget.jsonl"
    _append(log_path, row)
