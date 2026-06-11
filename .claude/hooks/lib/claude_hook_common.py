"""Small shared helper layer for live `.claude/hooks` entrypoints.

The hooks are fail-open governance adapters: helpers here avoid raising on
malformed payloads and keep durable receipts best-effort.
"""

from __future__ import annotations

import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REPO_ROOT_FOR_MCP = _REPO_ROOT
_RECEIPT_LOG = _REPO_ROOT / "artifacts" / "governance" / "claude_hook_receipts.jsonl"

STATUS_WORDS: tuple[str, ...] = ("STATUS: PASS", "STATUS: PARTIAL", "STATUS: FAIL", "STATUS: BLOCKED")
PROOF_WORDS: tuple[str, ...] = ("FILES_CHANGED", "COMMANDS_RUN", "TESTS_GATES", "ARTIFACTS")

_TEXT_KEYS: tuple[str, ...] = (
    "prompt",
    "command",
    "response",
    "response_text",
    "text",
    "content",
    "message",
    "tool_input",
)

_PATH_KEYS: tuple[str, ...] = ("file_path", "path", "uri", "target_path")

LEGACY_EXECUTION_TOKENS: tuple[str, ...] = (
    ".windsurf",
    "docs/archive/windsurf/legacy-tree",
    ".claude/governance/scripts/_legacy_windsurf",
)


def allow(reason: str = "") -> int:
    return 0


def block(reason: str = "") -> int:
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}), flush=True)
    return block_exit_code()


def warn(reason: str = "") -> int:
    if reason:
        print(f"[hook-warn] {reason}", file=sys.stderr)
    return 0


def block_exit_code() -> int:
    return 2


def read_payload() -> dict[str, Any]:
    try:
        raw = "" if sys.stdin.isatty() else sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)) or value is None:
        return "" if value is None else str(value)
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        return str(value)


def _collect_text(value: Any, out: list[str], *, depth: int = 0) -> None:
    if depth > 4:
        return
    if isinstance(value, dict):
        for key in _TEXT_KEYS:
            if key in value:
                out.append(_stringify(value.get(key)))
        tool_info = value.get("tool_info")
        if isinstance(tool_info, dict):
            _collect_text(tool_info, out, depth=depth + 1)
    elif isinstance(value, list):
        for item in value[:20]:
            _collect_text(item, out, depth=depth + 1)
    elif isinstance(value, str):
        out.append(value)


def text_from_payload(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    _collect_text(payload, parts)
    return "\n".join(part for part in parts if part)


def payload_path(payload: dict[str, Any]) -> str:
    def find(value: Any, depth: int = 0) -> str:
        if depth > 4:
            return ""
        if isinstance(value, dict):
            for key in _PATH_KEYS:
                hit = value.get(key)
                if isinstance(hit, str) and hit.strip():
                    return hit.replace("\\", "/")
            for nested_key in ("tool_input", "tool_info"):
                nested = value.get(nested_key)
                hit = find(nested, depth + 1)
                if hit:
                    return hit
        return ""

    return find(payload)


def contains_legacy_execution_token(text: str) -> list[str]:
    if not text:
        return []
    normalized = text.replace("\\", "/")
    hits: list[str] = []
    for token in LEGACY_EXECUTION_TOKENS:
        if token in normalized and token not in hits:
            hits.append(token)
    if re.search(r"\bWindsurf\b", text):
        hits.append("Windsurf")
    return hits


def write_receipt(hook: str, payload: dict[str, Any], decision: str, reason: str) -> None:
    row = {
        "hook": hook,
        "decision": decision,
        "reason": reason,
        "session_id": str(payload.get("session_id") or ""),
        "tool_name": str(payload.get("tool_name") or payload.get("toolName") or ""),
    }
    try:
        _RECEIPT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _RECEIPT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        return


def strip_mcp_tool_prefix(tool_name: str) -> str:
    raw = str(tool_name or "")
    if "_" not in raw:
        return raw
    return raw.split("_", 1)[1] if raw.startswith("mcp") else raw


def parse_mcp_tool_input(payload: dict[str, Any]) -> dict[str, Any] | None:
    value = payload.get("tool_input")
    if value is None and isinstance(payload.get("toolInfo"), dict):
        value = payload["toolInfo"].get("arguments")
    if value is None and isinstance(payload.get("tool_info"), dict):
        value = payload["tool_info"].get("arguments")
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


@lru_cache(maxsize=1)
def mcp_config_server_keys() -> frozenset[str]:
    path = _REPO_ROOT_FOR_MCP / ".mcp.json"
    if not path.is_file():
        return frozenset()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return frozenset()
    servers = data.get("mcpServers")
    if isinstance(servers, dict):
        return frozenset(str(key) for key in servers)
    return frozenset()


def _infer_server_name(payload: dict[str, Any]) -> str:
    candidates = (
        payload.get("mcp_server_name"),
        payload.get("server_name"),
        payload.get("server"),
        payload.get("command"),
    )
    server_keys = {key.lower(): key for key in mcp_config_server_keys()}
    for candidate in candidates:
        if not isinstance(candidate, str) or not candidate.strip():
            continue
        raw = candidate.strip()
        if raw.lower() in server_keys:
            return server_keys[raw.lower()]
    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "")
    if tool_name.startswith("mcp__"):
        parts = tool_name.split("__")
        if len(parts) >= 3:
            return parts[1]
    return ""


def normalize_mcp_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    tool_info = normalized.get("tool_info")
    if not isinstance(tool_info, dict):
        tool_info = {}
    tool_info = dict(tool_info)
    tool_info.setdefault("mcp_server_name", _infer_server_name(payload))
    tool_info.setdefault("mcp_tool_name", str(payload.get("tool_name") or payload.get("toolName") or ""))
    normalized["tool_info"] = tool_info
    return normalized


def resolve_mcp_server_name(payload: dict[str, Any], normalized: dict[str, Any] | None = None) -> str:
    norm = normalized or normalize_mcp_payload(payload)
    info = norm.get("tool_info")
    if isinstance(info, dict):
        server = info.get("mcp_server_name")
        if isinstance(server, str):
            return server
    return _infer_server_name(payload)


def cursor_response_payload(payload: dict[str, Any]) -> str:
    text = str(
        payload.get("response")
        or payload.get("response_text")
        or payload.get("text")
        or payload.get("content")
        or text_from_payload(payload)
        or ""
    )
    if not text.strip():
        return ""
    return json.dumps({"agent_action_name": "post_agent_response", "tool_info": {"response": text}})
