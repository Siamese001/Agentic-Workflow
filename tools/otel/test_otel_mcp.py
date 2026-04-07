#!/usr/bin/env python3
"""
Test script for OpenTelemetry MCP Server
Verifies that the server imports correctly and tools are registered.
"""

import asyncio
import importlib.util
import sys
from pathlib import Path


async def test_mcp_server():
    """Test that the OpenTelemetry MCP server loads correctly."""
    print("Testing OpenTelemetry MCP Server...")

    # Import the server
    server_path = Path("tools/otel/otel_mcp_server.py")
    if not server_path.exists():
        print("❌ Server file not found")
        return False

    spec = importlib.util.spec_from_file_location("otel_mcp_server", server_path)
    server_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(server_module)
        print("✅ Server module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import server module: {e}")
        return False

    # Check that FastMCP instance exists
    if not hasattr(server_module, 'mcp'):
        print("❌ FastMCP instance 'mcp' not found")
        return False

    mcp_instance = server_module.mcp
    print(f"✅ FastMCP instance found: {type(mcp_instance).__name__}")

    # Check that tools are registered (async call)
    try:
        tools = await mcp_instance.list_tools()
        tool_names = [tool.name for tool in tools]
        print(f"✅ Found {len(tool_names)} tools: {', '.join(tool_names)}")
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        # Fallback: check the mcp._tools attribute directly
        if hasattr(mcp_instance, '_tools'):
            tool_names = list(mcp_instance._tools.keys())
            print(f"✅ Found {len(tool_names)} tools (via _tools): {', '.join(tool_names)}")
        else:
            print("❌ Cannot access tools list")
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
    ]

    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        return False

    print("✅ All expected tools are registered")

    # Test a simple tool function (without actually calling it via MCP protocol)
    try:
        # Test otel_status function directly
        status_result = server_module.otel_status()
        print(f"✅ otel_status() returned: {type(status_result).__name__}")

        # Check required fields
        required_fields = ["collector_available", "runtime_adg_store_available", "last_trace_timestamp"]
        for field in required_fields:
            if field not in status_result:
                print(f"❌ Missing field in otel_status result: {field}")
                return False

        print("✅ otel_status() has all required fields")

    except Exception as e:
        print(f"❌ Error testing otel_status(): {e}")
        return False

    print("✅ OpenTelemetry MCP Server test passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
