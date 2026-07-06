"""Shared supervisor for persistent Streamable HTTP MCP services."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib
import json
import os
from pathlib import Path
import sys
from typing import Any

from tools.mcp.mcp_bootstrap import REPO_ROOT


@dataclass(frozen=True)
class HttpMcpServiceSpec:
    server_id: str
    module: str
    mcp_attr: str
    default_host: str
    default_port: int
    default_path: str
    state_relative_path: Path
    service_log_relative_path: Path
    required_tools: tuple[str, ...]
    preflight: Callable[[], dict[str, Any]]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_path(path: str | Path | None, default_relative: Path) -> Path:
    if path is None:
        return REPO_ROOT / default_relative
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": utc_now(), **payload}, sort_keys=True) + "\n")


def load_mcp(spec: HttpMcpServiceSpec) -> Any:
    module = importlib.import_module(spec.module)
    return getattr(module, spec.mcp_attr)


def configure_http_mcp(mcp: Any, *, host: str, port: int, path: str) -> None:
    settings = getattr(mcp, "settings")
    settings.host = host
    settings.port = int(port)
    settings.streamable_http_path = path


def preflight_payload(spec: HttpMcpServiceSpec, *, host: str, port: int, path: str) -> dict[str, Any]:
    base = spec.preflight()
    issues = list(base.get("issues") or [])
    if not path.startswith("/"):
        issues.append("streamable HTTP path must start with '/'")
    status = "ok" if not issues and base.get("status") in {None, "ok", "degraded"} else "critical"
    if status == "ok" and base.get("status") == "degraded":
        status = "degraded"
    return {
        "schema_version": "codex-http-mcp-launcher-preflight/v1",
        "status": status,
        "checked_at": utc_now(),
        "server_id": spec.server_id,
        "transport": "streamable-http",
        "url": f"http://{host}:{port}{path}",
        "host": host,
        "port": port,
        "path": path,
        "required_tools": list(spec.required_tools),
        "backend": base,
        "issues": issues,
    }


def run_http_service(
    spec: HttpMcpServiceSpec,
    *,
    host: str,
    port: int,
    path: str,
    state_path: Path,
    service_log_path: Path,
) -> int:
    preflight = preflight_payload(spec, host=host, port=port, path=path)
    state_base = {
        "schema_version": "codex-http-mcp-launcher-state/v1",
        "server_id": spec.server_id,
        "pid": os.getpid(),
        "started_at": utc_now(),
        "transport": "streamable-http",
        "url": preflight["url"],
        "preflight": preflight,
    }
    if preflight["status"] == "critical":
        write_json_atomic(state_path, {**state_base, "status": "blocked"})
        append_jsonl(service_log_path, {"event": "blocked", "server_id": spec.server_id, "preflight": preflight})
        print(json.dumps(preflight, indent=2, sort_keys=True), file=sys.stderr)
        return 2

    write_json_atomic(state_path, {**state_base, "status": "starting"})
    append_jsonl(service_log_path, {"event": "starting", "server_id": spec.server_id, "url": preflight["url"]})
    try:
        mcp = load_mcp(spec)
        configure_http_mcp(mcp, host=host, port=port, path=path)
        write_json_atomic(state_path, {**state_base, "status": "running", "running_at": utc_now()})
        append_jsonl(service_log_path, {"event": "running", "server_id": spec.server_id, "url": preflight["url"]})
        mcp.run(transport="streamable-http")
        return 0
    finally:
        write_json_atomic(state_path, {**state_base, "status": "stopped", "stopped_at": utc_now()})
        append_jsonl(service_log_path, {"event": "stopped", "server_id": spec.server_id})


def main_http_launcher(spec: HttpMcpServiceSpec, argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Launch {spec.server_id} Streamable HTTP MCP service.")
    parser.add_argument("--preflight-only", action="store_true", help="validate startup inputs and exit")
    parser.add_argument("--json", action="store_true", help="emit JSON for preflight/status output")
    parser.add_argument("--host", default=spec.default_host)
    parser.add_argument("--port", type=int, default=spec.default_port)
    parser.add_argument("--path", default=spec.default_path)
    parser.add_argument("--state-path", help="launcher state path")
    parser.add_argument("--service-log-path", help="JSONL service log path")
    args = parser.parse_args(argv)

    state_path = resolve_path(args.state_path, spec.state_relative_path)
    service_log_path = resolve_path(args.service_log_path, spec.service_log_relative_path)
    preflight = preflight_payload(spec, host=args.host, port=args.port, path=args.path)
    if args.preflight_only:
        if args.json:
            print(json.dumps(preflight, indent=2, sort_keys=True))
        else:
            print(f"status: {preflight['status']}")
            print(f"url: {preflight['url']}")
            for issue in preflight["issues"]:
                print(f"- {issue}")
        return 0 if preflight["status"] in {"ok", "degraded"} else 2

    return run_http_service(
        spec,
        host=args.host,
        port=args.port,
        path=args.path,
        state_path=state_path,
        service_log_path=service_log_path,
    )

