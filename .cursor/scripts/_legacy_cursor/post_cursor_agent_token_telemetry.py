"""post_cursor_agent_token_telemetry.py - per-turn token-burn telemetry.

Records an approximate per-turn token-cost row to
`artifacts/cursor/turn_budget.jsonl`. This is the measurement layer that
informs P2 (trim always-on footprint) and P1 threshold calibration.

Approximation: token count = bytes / 4 (Claude tokenizer ratio is 3-5x;
documented as approximate in the row schema). Refine if anyone needs exact
counts via tiktoken or an Anthropic-specific tokenizer.

Schema per row:
  {
    "timestamp": "...",
    "approx_response_tokens": int,        # response_text bytes / 4
    "approx_payload_tokens": int,         # raw stdin bytes / 4
    "tool_call_counts": {tool_name: int}, # by tool, all <invoke>s found
    "tool_call_total": int,
    "marker_counts": {marker: int}        # DECISION_CAPTURED, NEXT_STEP, etc.
  }

Fail-open: any internal error -> exit 0 and diagnostic to stderr.
Bypass: TOKEN_TELEMETRY_DISABLED=1 disables logging entirely.
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

REPO_ROOT = Path(__file__).resolve().parents[2]
TELEMETRY_LOG = REPO_ROOT / "artifacts" / "windsurf" / "turn_budget.jsonl"

# Generic tool-invocation marker - captures tool name regardless of MCP prefix.
_INVOKE_PAT = re.compile(r'<invoke\s+name="([^"]+)"', re.IGNORECASE)

# Markers tracked elsewhere - count occurrences for cross-correlation.
_MARKER_PATS = {
    "DECISION_CAPTURED": re.compile(r'DECISION_CAPTURED:', re.IGNORECASE),
    "DEFERRED_SCOPE": re.compile(r'DEFERRED_SCOPE:', re.IGNORECASE),
    "NEXT_STEP": re.compile(r'NEXT_STEP:', re.IGNORECASE),
    "SCOPE_RESET": re.compile(r'SCOPE_RESET:', re.IGNORECASE),
    "ROUTER_DECISION": re.compile(r'ROUTER_DECISION:', re.IGNORECASE),
    "DEGRADED_FALLBACK": re.compile(r'DEGRADED_FALLBACK:', re.IGNORECASE),
}


def _read_stdin() -> tuple[str, str]:
    """Returns (raw_payload, response_text). Fail-soft on any input error."""
    try:
        raw = sys.stdin.read() or ""
    except (OSError, ValueError):
        return ("", "")
    if not raw.strip():
        return ("", "")
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            for key in ("response_text", "response", "text", "content"):
                val = payload.get(key)
                if isinstance(val, str):
                    return (raw, val)
            return (raw, json.dumps(payload))
        return (raw, raw)
    except (ValueError, TypeError):
        return (raw, raw)


def _approx_tokens(s: str) -> int:
    """Bytes / 4 approximation. Documented as approximate."""
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


def _append(row: dict[str, Any]) -> None:
    TELEMETRY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with TELEMETRY_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    try:
        if os.environ.get("TOKEN_TELEMETRY_DISABLED", "").strip() == "1":
            return 0

        raw, response_text = _read_stdin()
        if not raw:
            return 0

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
        }
        _append(row)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        sys.stderr.write(f"[token-telemetry] fail-open: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
