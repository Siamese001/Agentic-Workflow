"""Shared payload extractor for post_agent_response hooks.

legacy editor delivers the cursor agent response text to hook stdin in this shape:

    {
      "agent_action_name": "post_agent_response",
      "tool_info": {
        "response": "<full assistant response text>"
      }
    }

Hooks that only checked top-level keys (`response`, `text`, `content`)
silently failed on the real payload — json.dumps fallback escapes newlines,
breaking multiline regex anchors (DEFERRED_SCOPE:, WRITEBACK:, etc.).

This helper is the SSOT extractor. All post_agent_*.py hooks MUST call
``extract_response_text(sys.stdin.read())`` rather than rolling their own
parser. A CI gate (`ops_scripts/ci/check_post_agent_payload.py`) blocks
any post_agent_*.py that reimplements the logic.
"""

from __future__ import annotations

import json
from typing import Any

# Keys checked, in priority order, at both the top level and inside tool_info.
_RESPONSE_KEYS: tuple[str, ...] = (
    "response",
    "text",
    "content",
    "message",
    "cascade_response",
    "response_text",
)


def _pick_from(obj: dict[str, Any]) -> str | None:
    for key in _RESPONSE_KEYS:
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return None


def extract_response_text(raw: str) -> str:
    """Return the assistant response text from a hook stdin payload.

    Accepts:
      * The documented shape: ``{"tool_info": {"response": "..."}}``
      * Plain-text stdin (returned as-is)
      * Flat JSON with a response key at top level
      * Other hook-test shapes used by internal tests

    Never raises. Returns "" on empty or unparseable input.
    """

    if not raw or not raw.strip():
        return ""

    try:
        payload: Any = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw  # plain-text stdin (manual test / legacy)

    if isinstance(payload, str):
        return payload

    if not isinstance(payload, dict):
        return raw

    # 1. Prefer the documented location: tool_info.response
    tool_info = payload.get("tool_info")
    if isinstance(tool_info, dict):
        hit = _pick_from(tool_info)
        if hit is not None:
            return hit

    # 2. Fallback: top-level keys for legacy / test shapes
    hit = _pick_from(payload)
    if hit is not None:
        return hit

    # 3. Last resort: stringify the whole envelope. NOTE: newlines will be
    #    escaped — multiline anchors will not match. This is a signal of a
    #    malformed payload shape, not a normal legacy editor payload.
    try:
        return json.dumps(payload)
    except (TypeError, ValueError):
        return raw


__all__ = ["extract_response_text"]
