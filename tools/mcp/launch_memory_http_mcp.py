"""Persistent Streamable HTTP launcher for the memory MCP server."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from tools.mcp.http_service_supervisor import HttpMcpServiceSpec, main_http_launcher
from tools.mcp.mcp_bootstrap import REPO_ROOT


def memory_preflight_status() -> dict[str, Any]:
    issues: list[str] = []
    redis_url = (os.environ.get("ADG_REDIS_URL") or "").strip()
    if not redis_url or "$" in redis_url:
        issues.append("ADG_REDIS_URL is required for memory MCP startup")
    db_path = Path(os.environ.get("MEMORY_DB") or "artifacts/memory/knowledge_graph.sqlite")
    if not db_path.is_absolute():
        db_path = REPO_ROOT / db_path
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        issues.append(f"memory db parent is not writable: {type(exc).__name__}: {exc}")
    return {
        "status": "ok" if not issues else "critical",
        "repo_root": str(REPO_ROOT),
        "memory_db": str(db_path),
        "redis": {"configured": bool(redis_url), "status": "configured" if redis_url else "missing"},
        "issues": issues,
    }


SPEC = HttpMcpServiceSpec(
    server_id="memory",
    module="tools.memory.adg_memory_server",
    mcp_attr="mcp",
    default_host="127.0.0.1",
    default_port=8766,
    default_path="/mcp",
    state_relative_path=Path("artifacts/mcp_heartbeat/memory_http_launcher.json"),
    service_log_relative_path=Path("artifacts/mcp/memory_http_service.jsonl"),
    required_tools=("memory_health", "mem_process_identity"),
    preflight=memory_preflight_status,
)


def main() -> int:
    return main_http_launcher(SPEC)


if __name__ == "__main__":
    raise SystemExit(main())

