"""Stress-test Codex MCP HTTP transport without mutating MCP process state."""

from __future__ import annotations

import argparse
from functools import partial
import json
from datetime import UTC, datetime
from pathlib import Path
import sys
import time
from typing import Any

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


ROOT = Path(__file__).resolve().parents[2]
CODEX_GOVERNANCE_SCRIPTS = ROOT / ".codex" / "governance" / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(CODEX_GOVERNANCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(CODEX_GOVERNANCE_SCRIPTS))

import audit_codex_mcp_transports  # noqa: E402
import mcp_callability_epoch  # noqa: E402


SCHEMA_VERSION = "codex-mcp-http-stress/v1"


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _load_service_state(server_id: str, root: Path = ROOT) -> dict[str, Any]:
    if not server_id:
        return {}
    path = root / "artifacts" / "mcp_heartbeat" / f"{server_id}_http_launcher.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {"available": False, "state_path": str(path)}
    if not isinstance(value, dict):
        return {"available": False, "state_path": str(path)}
    return {**value, "available": True, "state_path": str(path)}


async def _stress_http_calls(
    *,
    url: str,
    tool: str,
    count: int,
    timeout_s: float,
) -> dict[str, Any]:
    start = time.perf_counter()
    errors: list[dict[str, Any]] = []
    tool_names: list[str] = []
    first_result: Any = None
    last_result: Any = None
    transport_closed_count = 0

    try:
        async with streamablehttp_client(url, timeout=timeout_s, sse_read_timeout=timeout_s) as (
            read_stream,
            write_stream,
            _get_session_id,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                initialize_result = await session.initialize()
                tools_result = await session.list_tools()
                tool_names = [item.name for item in tools_result.tools]
                if tool not in tool_names:
                    return {
                        "status": "fail",
                        "initialize": {"ok": True, "result": _jsonable(initialize_result)},
                        "tools_list": {"ok": True, "tool_count": len(tool_names), "tools": tool_names},
                        "tool_call": {"ok": False, "tool": tool, "error": f"tool {tool!r} not in tools/list"},
                        "count": count,
                        "passed": 0,
                        "failed": count,
                        "errors": [{"index": 0, "error": f"tool {tool!r} not in tools/list"}],
                        "transport_closed_count": 0,
                        "elapsed_s": round(time.perf_counter() - start, 6),
                    }
                for index in range(count):
                    try:
                        result = await session.call_tool(tool, {})
                    except Exception as exc:  # guardian: collect per-call failure and continue
                        message = f"{type(exc).__name__}: {exc}"
                        if "transport closed" in message.lower() or "connection closed" in message.lower():
                            transport_closed_count += 1
                        if len(errors) < 20:
                            errors.append({"index": index, "error": message})
                        continue
                    jsonable = _jsonable(result)
                    if first_result is None:
                        first_result = jsonable
                    last_result = jsonable
    except Exception as exc:  # guardian: stress result must be structured
        message = f"{type(exc).__name__}: {exc}"
        if "transport closed" in message.lower() or "connection closed" in message.lower():
            transport_closed_count += 1
        return {
            "status": "fail",
            "initialize": {"ok": False},
            "tools_list": {"ok": False, "tools": tool_names},
            "tool_call": {"ok": False, "tool": tool, "error": message},
            "count": count,
            "passed": 0,
            "failed": count,
            "errors": [{"index": 0, "error": message}],
            "transport_closed_count": transport_closed_count,
            "elapsed_s": round(time.perf_counter() - start, 6),
        }

    failed = len(errors)
    passed = count - failed
    return {
        "status": "ok" if failed == 0 else "fail",
        "initialize": {"ok": True},
        "tools_list": {"ok": True, "tool_count": len(tool_names), "tools": tool_names},
        "tool_call": {"ok": failed == 0, "tool": tool},
        "count": count,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "transport_closed_count": transport_closed_count,
        "stdout_protocol_corruption_count": 0,
        "first_result": first_result,
        "last_result": last_result,
        "elapsed_s": round(time.perf_counter() - start, 6),
    }


def _active_proof_report(server_id: str, expected_url: str, root: Path = ROOT) -> dict[str, Any]:
    proof = mcp_callability_epoch.proof_status(server_id, repo_root=root)
    acceptance = audit_codex_mcp_transports.http_route_acceptance(server_id, expected_url, proof)
    return {
        "server_id": server_id,
        "expected_url": expected_url,
        "callability_proof": proof,
        "http_callability_acceptance": acceptance,
        "status": "ok" if acceptance.get("accepted") else "fail",
    }


def build_report(
    *,
    server_id: str,
    url: str,
    tool: str,
    count: int,
    timeout_s: float,
    require_active_proof: bool = False,
    root: Path = ROOT,
) -> dict[str, Any]:
    before = _load_service_state(server_id, root)
    direct = anyio.run(
        partial(
            _stress_http_calls,
            url=url,
            tool=tool,
            count=count,
            timeout_s=timeout_s,
        )
    )
    after = _load_service_state(server_id, root)
    service_pid_stable = (
        before.get("pid") == after.get("pid")
        if before.get("available") and after.get("available")
        else None
    )
    active = _active_proof_report(server_id, url, root) if require_active_proof else None
    status = "ok" if direct.get("status") == "ok" and (active is None or active.get("status") == "ok") else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "server_id": server_id,
        "url": url,
        "tool": tool,
        "count": count,
        "timeout_s": timeout_s,
        "status": status,
        "direct_http": direct,
        "active_session_proof": active,
        "service_state_before": before,
        "service_state_after": after,
        "service_pid_stable": service_pid_stable,
        "restarts_observed": 0 if service_pid_stable is True else None,
    }


def write_report(report: dict[str, Any], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--tool", required=True)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--require-active-proof", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.count <= 0:
        parser.error("--count must be positive")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    report = build_report(
        server_id=args.server_id,
        url=args.url,
        tool=args.tool,
        count=args.count,
        timeout_s=args.timeout,
        require_active_proof=args.require_active_proof,
    )
    if args.output:
        write_report(report, args.output)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        direct = report["direct_http"]
        print(f"status: {report['status']}")
        print(f"direct_http: {direct['passed']}/{direct['count']} passed")
        if report.get("active_session_proof") is not None:
            print(f"active_session_proof: {report['active_session_proof']['status']}")
    return 0 if report["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
