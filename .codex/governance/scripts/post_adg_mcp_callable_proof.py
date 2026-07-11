#!/usr/bin/env python3
"""Record endpoint-matched proof from successful structured MCP events only."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
for candidate in (_REPO_ROOT, _REPO_ROOT / ".codex" / "governance" / "scripts"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from mcp_callability_epoch import canonical_server_id, read_epoch, write_callability_proof

_DEFERRED_SCHEMA = "codex-deferred-mcp-result/v1"
_MAX_EVENT_AGE_SECONDS = 300.0
_PROOF_TOOLS = {
    "adg_sqlite": {"adg_health", "adg_runtime_info", "adg_process_identity"},
    "memory": {"memory_health", "mem_health_check", "mem_process_identity"},
}
_ADG_SUPERVISOR_PROOF_TOOLS = _PROOF_TOOLS["adg_sqlite"]
_HTTP_STATE_PATHS = {
    "adg_sqlite": Path("artifacts/mcp_heartbeat/adg_sqlite_http_launcher.json"),
    "memory": Path("artifacts/mcp_heartbeat/memory_http_launcher.json"),
}
_DIRECT_NAME = re.compile(r"^mcp__(?P<server>[A-Za-z0-9_]+)(?:__|\.)(?P<tool>[A-Za-z0-9_]+)$")
_EXEC_CALL = re.compile(r"await\s+tools\.mcp__(?P<server>[A-Za-z0-9_]+)__(?P<tool>[A-Za-z0-9_]+)\s*\(")


@dataclass(frozen=True)
class EventDecision:
    accepted: bool
    reason: str
    server: str = ""
    tool: str = ""
    endpoint: str = ""
    response: Any = None
    session_id: str = ""


def _load_payload(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _tool_name(payload: dict[str, Any]) -> str:
    return _string(payload.get("tool_name") or payload.get("toolName") or payload.get("name"))


def _tool_response(payload: dict[str, Any]) -> Any:
    for key in ("tool_response", "toolResponse", "tool_result", "response", "result"):
        if key in payload:
            return payload[key]
    return None


def _session_id(payload: dict[str, Any]) -> str:
    return _string(payload.get("session_id") or payload.get("sessionId"))


def _configured_route(server: str) -> tuple[str, str]:
    try:
        data = json.loads((_REPO_ROOT / ".mcp.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return "", ""
    servers = data.get("mcpServers")
    config = servers.get(server) if isinstance(servers, dict) else None
    if not isinstance(config, dict):
        return "", ""
    endpoint = _string(config.get("url") or config.get("serverUrl"))
    if endpoint:
        return "http", endpoint
    return ("stdio", "") if config.get("command") else ("", "")


def _configured_http_pid(server: str, endpoint: str) -> int | None:
    relative = _HTTP_STATE_PATHS.get(server)
    if relative is None:
        return None
    try:
        state = json.loads((_REPO_ROOT / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None
    if not isinstance(state, dict):
        return None
    pid = state.get("pid")
    if state.get("status") != "running" or state.get("url") != endpoint:
        return None
    return pid if isinstance(pid, int) and pid > 0 else None


def _parse_time(value: Any) -> datetime | None:
    text = _string(value)
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _structured_success(response: Any) -> bool:
    if not isinstance(response, dict) or response.get("isError") is True or response.get("is_error") is True:
        return False
    structured = response.get("structuredContent") or response.get("structured_content") or response
    if not isinstance(structured, dict):
        return False
    status = _string(structured.get("status")).lower()
    if status in {"error", "fail", "failed", "blocked", "unhealthy"}:
        return False
    return status in {"ok", "healthy", "degraded"}


def _json_objects(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _json_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _json_objects(child)
    elif isinstance(value, str):
        stripped = value.strip()
        candidates = [stripped]
        if "\n" in stripped:
            candidates.extend(line.strip() for line in stripped.splitlines())
        for candidate in candidates:
            if not candidate.startswith("{"):
                continue
            try:
                parsed = json.loads(candidate)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(parsed, dict):
                yield parsed


def _deferred_receipt(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    tool_input = payload.get("tool_input") or payload.get("toolInput")
    source = _string(tool_input.get("source")) if isinstance(tool_input, dict) else _string(tool_input)
    if not source:
        return None, "deferred_source_missing"
    calls = list(_EXEC_CALL.finditer(source))
    if len(calls) != 1:
        return None, "deferred_source_call_count"
    if _DEFERRED_SCHEMA not in source or "JSON.stringify" not in source:
        return None, "deferred_source_contract_missing"
    receipts = [
        item for item in _json_objects(_tool_response(payload)) if item.get("schema") == _DEFERRED_SCHEMA
    ]
    if len(receipts) != 1:
        return None, "deferred_structured_receipt_missing"
    receipt = receipts[0]
    match = calls[0]
    source_server = canonical_server_id(match.group("server"))
    source_tool = match.group("tool")
    if (
        canonical_server_id(receipt.get("server_id", "")) != source_server
        or receipt.get("tool_name") != source_tool
    ):
        return None, "deferred_identity_mismatch"
    return receipt, "accepted"


def classify_event(payload: dict[str, Any], *, now: datetime | None = None) -> EventDecision:
    outer = _tool_name(payload)
    response: Any
    endpoint = ""
    completed_at: datetime | None = None
    deferred = outer in {"functions.exec", "exec"}
    if deferred:
        receipt, reason = _deferred_receipt(payload)
        if receipt is None:
            return EventDecision(False, reason)
        server = canonical_server_id(receipt.get("server_id", ""))
        tool = _string(receipt.get("tool_name"))
        endpoint = _string(receipt.get("endpoint"))
        response = receipt.get("result")
        completed_at = _parse_time(receipt.get("completed_at"))
        if completed_at is None:
            return EventDecision(False, "deferred_timestamp_missing")
    else:
        direct = _DIRECT_NAME.fullmatch(outer)
        if not direct:
            return EventDecision(False, "outer_tool_not_mcp")
        server = canonical_server_id(direct.group("server"))
        tool = direct.group("tool")
        response = _tool_response(payload)

    if server not in _PROOF_TOOLS:
        return EventDecision(False, "server_not_proof_managed")
    if tool not in _PROOF_TOOLS[server]:
        return EventDecision(False, "tool_not_proof_authorized", server=server, tool=tool)
    route_kind, configured_endpoint = _configured_route(server)
    if route_kind != "http" or not configured_endpoint:
        return EventDecision(False, "configured_http_route_missing", server=server, tool=tool)
    if endpoint and endpoint != configured_endpoint:
        return EventDecision(False, "endpoint_mismatch", server=server, tool=tool, endpoint=endpoint)
    if not _structured_success(response):
        return EventDecision(False, "structured_success_missing", server=server, tool=tool)
    if not deferred:
        response_pid = _pid_from_response(response)
        if response_pid is None or response_pid != _configured_http_pid(server, configured_endpoint):
            return EventDecision(False, "direct_http_process_mismatch", server=server, tool=tool)
    if completed_at is not None:
        current = now or datetime.now(UTC)
        if current.tzinfo is None:
            current = current.replace(tzinfo=UTC)
        epoch_at = _parse_time(read_epoch(_REPO_ROOT).get("generated_at"))
        age = (current.astimezone(UTC) - completed_at).total_seconds()
        if age < -5 or age > _MAX_EVENT_AGE_SECONDS or (epoch_at and completed_at < epoch_at):
            return EventDecision(False, "stale_deferred_receipt", server=server, tool=tool)
    return EventDecision(
        True,
        "accepted",
        server=server,
        tool=tool,
        endpoint=configured_endpoint,
        response=response,
        session_id=_session_id(payload),
    )


def _response_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _pid_from_response(response: Any) -> int | None:
    for item in _json_objects(response):
        pid = item.get("pid")
        if isinstance(pid, int) and pid > 0:
            return pid
    return None


def _pid_from_heartbeat() -> int | None:
    try:
        from tools.adg.mcp import supervisor
    except (ImportError, OSError):
        return None
    pids = {
        int(row["pid"])
        for row in supervisor.heartbeat_status()
        if row.get("authoritative") and isinstance(row.get("pid"), int)
    }
    return next(iter(pids)) if len(pids) == 1 else None


def maybe_record_proof(payload: dict[str, Any], *, now: datetime | None = None) -> Path | None:
    decision = classify_event(payload, now=now)
    if not decision.accepted:
        if os.getenv("ADG_CALLABLE_PROOF_DEBUG") == "1":
            sys.stderr.write(f"post_adg_mcp_callable_proof: rejected={decision.reason}\n")
        return None
    pid = _pid_from_response(decision.response)
    route_path = write_callability_proof(
        server_id=decision.server,
        tool=decision.tool,
        evidence=_response_text(decision.response),
        repo_root=_REPO_ROOT,
        session_id=decision.session_id,
        pid=pid,
        route_kind="http",
        endpoint=decision.endpoint,
        now=now,
    )
    if decision.server != "adg_sqlite" or decision.tool not in _ADG_SUPERVISOR_PROOF_TOOLS:
        return route_path
    resolved_pid = pid or _pid_from_heartbeat()
    if resolved_pid is None:
        return route_path
    from tools.adg.mcp import supervisor

    adg_path = supervisor.write_callable_proof(
        tool=decision.tool,
        pid=resolved_pid,
        evidence=_response_text(decision.response),
        session_id=decision.session_id,
        repo_root=_REPO_ROOT,
    )
    return adg_path or route_path


def main() -> int:
    try:
        payload = _load_payload(sys.stdin.read())
        path = maybe_record_proof(payload) if payload else None
    except (OSError, RuntimeError, ValueError, TypeError, ImportError) as exc:
        sys.stderr.write(f"post_adg_mcp_callable_proof: capture skipped ({type(exc).__name__}: {exc})\n")
        return 0
    if os.getenv("ADG_CALLABLE_PROOF_DEBUG") == "1" and path is not None:
        sys.stderr.write(f"post_adg_mcp_callable_proof: wrote {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
