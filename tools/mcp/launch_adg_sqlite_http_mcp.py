"""Persistent Streamable HTTP launcher for the ADG SQLite MCP server."""

from __future__ import annotations

from pathlib import Path

from tools.adg.mcp import supervisor as adg_supervisor
from tools.mcp.http_service_supervisor import HttpMcpServiceSpec, main_http_launcher


SPEC = HttpMcpServiceSpec(
    server_id="adg_sqlite",
    module="tools.adg.mcp.server",
    mcp_attr="mcp",
    default_host="127.0.0.1",
    default_port=8765,
    default_path="/mcp",
    state_relative_path=Path("artifacts/mcp_heartbeat/adg_sqlite_http_launcher.json"),
    service_log_relative_path=Path("artifacts/mcp/adg_sqlite_http_service.jsonl"),
    required_tools=("adg_health", "adg_process_identity", "adg_runtime_info"),
    preflight=adg_supervisor.preflight_status,
)


def main() -> int:
    return main_http_launcher(SPEC)


if __name__ == "__main__":
    raise SystemExit(main())
