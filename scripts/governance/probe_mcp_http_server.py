"""Probe a Streamable HTTP MCP server using the MCP client SDK."""

from __future__ import annotations

import argparse
from functools import partial
import json
from typing import Any

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


async def probe_http_mcp(url: str, *, tool: str | None = None, timeout_s: float = 30.0) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "codex-mcp-http-probe/v1",
        "url": url,
        "initialize": {"ok": False},
        "tools_list": {"ok": False},
        "tool_call": {"ok": None, "tool": tool},
    }
    try:
        async with streamablehttp_client(url, timeout=timeout_s, sse_read_timeout=timeout_s) as (
            read_stream,
            write_stream,
            _get_session_id,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                initialize_result = await session.initialize()
                payload["initialize"] = {"ok": True, "result": _jsonable(initialize_result)}
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                payload["tools_list"] = {
                    "ok": True,
                    "tool_count": len(tool_names),
                    "tools": tool_names,
                }
                if tool:
                    if tool not in tool_names:
                        payload["tool_call"] = {
                            "ok": False,
                            "tool": tool,
                            "error": f"tool {tool!r} not in tools/list",
                        }
                    else:
                        result = await session.call_tool(tool, {})
                        payload["tool_call"] = {
                            "ok": True,
                            "tool": tool,
                            "result": _jsonable(result),
                        }
    except Exception as exc:  # guardian: allow-broad-exception -- probe returns structured failure
        payload["error"] = f"{type(exc).__name__}: {exc}"
        payload["status"] = "fail"
        return payload

    required_ok = payload["initialize"]["ok"] and payload["tools_list"]["ok"]
    if tool:
        required_ok = required_ok and bool(payload["tool_call"]["ok"])
    payload["status"] = "ok" if required_ok else "fail"
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe a Streamable HTTP MCP endpoint.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--tool", help="optional zero-argument tool to call after tools/list")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = anyio.run(partial(probe_http_mcp, args.url, tool=args.tool, timeout_s=args.timeout))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        print(f"initialize: {result['initialize']['ok']}")
        print(f"tools/list: {result['tools_list']['ok']}")
        if args.tool:
            print(f"{args.tool}: {result['tool_call']['ok']}")
        if result.get("error"):
            print(f"error: {result['error']}")
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
