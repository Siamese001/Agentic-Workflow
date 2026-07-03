#!/usr/bin/env python3
"""Record active-session ADG MCP callability proof after successful tool use.

PostToolUse is the only native hook point that sees a completed MCP call and its
response. This script records a short-lived proof file for the ADG supervisor
only after a successful ADG SQLite MCP health/runtime/process-identity call. It
never blocks: an error here must not wedge the Codex hook host.
"""

from __future__ import annotations

from collections.abc import Iterable
import json
import os
from pathlib import Path
import sys
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_PROOF_TOOLS = {"adg_health", "adg_runtime_info", "adg_process_identity"}
_FAILURE_MARKERS = (
    "transport closed",
    "tool call error",
    "connection closed",
    "mcp error",
    "mcperror",
)


def _load_payload(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _split_mcp_tool_name(raw: str) -> tuple[str, str]:
    name = raw.strip()
    if not name.startswith("mcp__"):
        return "", name
    remainder = name[len("mcp__") :]
    if "." in remainder:
        server, tool = remainder.split(".", 1)
        return server, tool
    if "__" in remainder:
        server, tool = remainder.split("__", 1)
        return server, tool
    return "", name


def _tool_identity(payload: dict[str, Any]) -> tuple[str, str]:
    info = payload.get("tool_info")
    if not isinstance(info, dict):
        info = {}

    server = str(
        info.get("mcp_server_name")
        or payload.get("mcp_server_name")
        or payload.get("server_name")
        or ""
    )
    tool = str(
        info.get("mcp_tool_name")
        or payload.get("mcp_tool_name")
        or payload.get("tool")
        or ""
    )
    raw_tool = str(
        payload.get("tool_name")
        or payload.get("toolName")
        or info.get("tool_name")
        or info.get("toolName")
        or ""
    )
    inferred_server, inferred_tool = _split_mcp_tool_name(raw_tool)
    return server or inferred_server, tool or inferred_tool


def _tool_response(payload: dict[str, Any]) -> Any:
    for key in ("tool_response", "tool_result", "response", "result", "output"):
        if key in payload:
            return payload[key]
    info = payload.get("tool_info")
    if isinstance(info, dict):
        for key in ("tool_response", "tool_result", "response", "result", "output"):
            if key in info:
                return info[key]
    return None


def _session_id(payload: dict[str, Any]) -> str:
    info = payload.get("tool_info")
    for source in (payload, info):
        if isinstance(source, dict):
            value = source.get("session_id") or source.get("sessionId")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _response_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return str(value)


def _contains_transport_failure(payload: dict[str, Any], response: Any) -> bool:
    if payload.get("is_error") is True or payload.get("error") is not None:
        return True
    text = _response_text(response).lower()
    return any(marker in text for marker in _FAILURE_MARKERS)


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("{", "[")):
            try:
                parsed = json.loads(stripped)
            except (json.JSONDecodeError, TypeError):
                return
            yield from _walk(parsed)


def _pid_from_response(response: Any) -> int | None:
    for value in _walk(response):
        if not isinstance(value, dict):
            continue
        pid = value.get("pid")
        if isinstance(pid, int) and pid > 0:
            return pid
        if isinstance(pid, str) and pid.isdigit() and int(pid) > 0:
            return int(pid)
    return None


def _pid_from_heartbeat() -> int | None:
    try:
        from tools.adg.mcp import supervisor
    except Exception:  # noqa: BLE001
        # guardian: PostToolUse proof capture is fail-soft.
        return None
    pids = {
        int(row["pid"])
        for row in supervisor.heartbeat_status()
        if row.get("authoritative") and isinstance(row.get("pid"), int)
    }
    if len(pids) == 1:
        return next(iter(pids))
    return None


def maybe_record_proof(payload: dict[str, Any]) -> Path | None:
    server, tool = _tool_identity(payload)
    if server != "adg_sqlite" or tool not in _PROOF_TOOLS:
        return None

    response = _tool_response(payload)
    if response is None or _contains_transport_failure(payload, response):
        return None

    pid = _pid_from_response(response)
    if pid is None:
        pid = _pid_from_heartbeat()
    if pid is None:
        return None

    evidence = _response_text(response)
    from tools.adg.mcp import supervisor

    return supervisor.write_callable_proof(
        tool=tool,
        pid=pid,
        evidence=evidence,
        session_id=_session_id(payload),
        repo_root=_REPO_ROOT,
    )


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    payload = _load_payload(raw)
    if not payload:
        return 0
    try:
        path = maybe_record_proof(payload)
    except Exception as exc:  # noqa: BLE001
        # guardian: PostToolUse must never block or wedge the host.
        sys.stderr.write(f"post_adg_mcp_callable_proof: capture skipped ({type(exc).__name__}: {exc})\n")
        return 0
    if os.getenv("ADG_CALLABLE_PROOF_DEBUG") == "1" and path is not None:
        sys.stderr.write(f"post_adg_mcp_callable_proof: wrote {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
