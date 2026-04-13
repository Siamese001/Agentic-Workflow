#!/usr/bin/env python3
"""
Test script for OpenTelemetry MCP Server
Verifies that the server imports correctly and tools are registered.
"""

import asyncio
import importlib.util
import os
import sys
from pathlib import Path

# Enable mock traces for testing before importing server
os.environ["OTEL_MCP_ALLOW_MOCK_TRACES"] = "1"


class _DummyTracer:
    """Stub tracer so the server never reaches real OTel."""

    def is_enabled(self):
        return False


class _DummyStore:
    """Stub runtime ADG store."""

    def get_version_id_for_trace(self, _tid: str):
        return None


async def test_mcp_server():
    """Test that the OpenTelemetry MCP server loads correctly."""
    print("Testing OpenTelemetry MCP Server...")

    # Import the server
    server_path = Path("tools/otel/otel_mcp_server.py")
    if not server_path.exists():
        print("\u274c Server file not found")
        return False

    spec = importlib.util.spec_from_file_location("otel_mcp_server", server_path)
    server_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(server_module)
        print("\u2705 Server module imported successfully")
    except (
        Exception
    ) as e:  # guardian: allow-broad-exception -- test harness must catch any import failure and report it
        print(f"\u274c Failed to import server module: {e}")
        return False

    # Stub heavy loaders so tests don't need real OTel / runtime ADG
    server_module._tracer_loader.get = lambda: _DummyTracer()
    server_module._store_loader.get = lambda: _DummyStore()

    # Check that FastMCP instance exists
    if not hasattr(server_module, "mcp"):
        print("\u274c FastMCP instance 'mcp' not found")
        return False

    mcp_instance = server_module.mcp
    print(f"\u2705 FastMCP instance found: {type(mcp_instance).__name__}")

    # Check that tools are registered (async call)
    try:
        tools = await mcp_instance.list_tools()
        tool_names = [tool.name for tool in tools]
        print(f"\u2705 Found {len(tool_names)} tools: {', '.join(tool_names)}")
    except Exception as e:  # guardian: allow-broad-exception -- test harness must catch any tool-listing failure and report it
        print(f"\u274c Failed to list tools: {e}")
        # Fallback: check the mcp._tools attribute directly
        if hasattr(mcp_instance, "_tools"):
            tool_names = list(mcp_instance._tools.keys())
            print(f"\u2705 Found {len(tool_names)} tools (via _tools): {', '.join(tool_names)}")
        else:
            print("\u274c Cannot access tools list")
            return False

    expected_tools = [
        "otel_status",
        "otel_trace",
        "otel_spans_by_agent",
        "otel_healing_chain",
        "otel_policy_decisions",
        "otel_metrics_summary",
        "otel_anomalies",
        "otel_ingest_to_runtime_adg",
        "otel_server_info",
    ]

    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
    if missing_tools:
        print(f"\u274c Missing tools: {', '.join(missing_tools)}")
        return False

    print("\u2705 All expected tools are registered")

    # Test a simple tool function (without actually calling it via MCP protocol)
    try:
        # Test otel_status function directly
        status_result = server_module.otel_status()
        print(f"\u2705 otel_status() returned: {type(status_result).__name__}")

        # Check required fields (including new tracer_error / store_error)
        required_fields = [
            "collector_available",
            "runtime_adg_store_available",
            "last_trace_timestamp",
            "tracer_error",
            "store_error",
        ]
        for field in required_fields:
            if field not in status_result:
                print(f"\u274c Missing field in otel_status result: {field}")
                return False

        print("\u2705 otel_status() has all required fields")

    except (
        Exception
    ) as e:  # guardian: allow-broad-exception -- test harness must catch any tool call failure and report it
        print(f"\u274c Error testing otel_status(): {e}")
        return False

    # Test otel_server_info
    try:
        info = server_module.otel_server_info()
        for key in ("pid", "start_time_utc", "source_file", "source_mtime_utc"):
            if key not in info:
                print(f"\u274c Missing field in otel_server_info: {key}")
                return False
        print("\u2705 otel_server_info() has all required fields")
    except (
        Exception
    ) as e:  # guardian: allow-broad-exception -- test harness must catch any tool call failure and report it
        print(f"\u274c Error testing otel_server_info(): {e}")
        return False

    # Test otel_trace with mock fallback
    try:
        trace_result = server_module.otel_trace("mock_test_trace_123456")
        if not isinstance(trace_result, dict):
            print("\u274c otel_trace did not return a dict")
            return False
        print(f"\u2705 otel_trace() returned: success={trace_result.get('success', 'n/a')}")
    except (
        Exception
    ) as e:  # guardian: allow-broad-exception -- test harness must catch any tool call failure and report it
        print(f"\u274c Error testing otel_trace(): {e}")
        return False

    print("\u2705 OpenTelemetry MCP Server test passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
