"""MCP preflight hygiene stage for live Claude Code hooks."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .codex_hook_common import contains_legacy_execution_token

_ROOT = Path(__file__).resolve().parents[3]
_HYGIENE_LOG = _ROOT / "artifacts" / "cursor" / "mcp_before_hygiene.jsonl"
_TOOL_INPUT_MAX_BYTES = 512 * 1024


def _log(outcome: str, code: str, reason: str, payload: dict[str, Any]) -> None:
    row = {
        "outcome": outcome,
        "code": code,
        "reason": reason,
        "tool_name": str(payload.get("tool_info", {}).get("mcp_tool_name", "")),
    }
    try:
        _HYGIENE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _HYGIENE_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        return


def _serialized_tool_input(value: Any) -> tuple[str | None, str | None]:
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True), None
    if isinstance(value, str):
        if len(value.encode("utf-8")) > _TOOL_INPUT_MAX_BYTES:
            return None, "TOOL_INPUT_OVERSIZED"
        if value.strip():
            try:
                json.loads(value)
            except json.JSONDecodeError:
                return None, "TOOL_INPUT_JSON_INVALID"
        return value, None
    return None, "TOOL_INPUT_TYPE"


def run_mcp_before_hygiene_stage(payload: dict[str, Any]) -> int:
    tool_input = payload.get("tool_input")
    if tool_input is None:
        return 0

    if os.environ.get("MCP_BEFORE_HYGIENE_BYPASS") == "1":
        _log("NOT_APPLICABLE", "BYPASS", "MCP_BEFORE_HYGIENE_BYPASS=1", payload)
        return 0

    serialized, error = _serialized_tool_input(tool_input)
    if error:
        print(f"[MCP_HYGIENE_BLOCK] code={error}", file=sys.stderr)
        _log("BLOCK", error, "invalid tool_input", payload)
        return 2
    assert serialized is not None

    if len(serialized.encode("utf-8")) > _TOOL_INPUT_MAX_BYTES:
        print("[MCP_HYGIENE_BLOCK] code=TOOL_INPUT_OVERSIZED", file=sys.stderr)
        _log("BLOCK", "TOOL_INPUT_OVERSIZED", "tool_input exceeds size limit", payload)
        return 2

    legacy = contains_legacy_execution_token(serialized)
    if legacy:
        print("[MCP_HYGIENE_BLOCK] code=LEGACY_SURFACE_IN_TOOL_INPUT", file=sys.stderr)
        _log("BLOCK", "LEGACY_SURFACE_IN_TOOL_INPUT", ", ".join(legacy), payload)
        return 2

    _log("ALLOW", "OK", "tool_input accepted", payload)
    return 0
