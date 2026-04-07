#!/usr/bin/env python3
"""
Test script for Phase 3 MCP Server
Tests System Learning Meta-Learning MCP server.
"""

import asyncio
import importlib.util
import sys
from pathlib import Path


async def test_meta_learning_mcp():
    """Test System Learning Meta-Learning MCP server."""
    print("Testing System Learning Meta-Learning MCP Server...")

    server_path = Path("tools/learning/meta_learning_mcp_server.py")
    if not server_path.exists():
        print("❌ Meta-learning server file not found")
        return False

    spec = importlib.util.spec_from_file_location("meta_learning_mcp_server", server_path)
    server_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(server_module)
        print("✅ Meta-learning server module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Meta-learning server module: {e}")
        return False

    # Check FastMCP instance
    if not hasattr(server_module, 'mcp'):
        print("❌ FastMCP instance 'mcp' not found")
        return False

    mcp_instance = server_module.mcp
    print(f"✅ FastMCP instance found: {type(mcp_instance).__name__}")

    # Check tools
    try:
        tools = await mcp_instance.list_tools()
        tool_names = [tool.name for tool in tools]
        print(f"✅ Found {len(tool_names)} tools: {', '.join(tool_names)}")
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        if hasattr(mcp_instance, '_tools'):
            tool_names = list(mcp_instance._tools.keys())
            print(f"✅ Found {len(tool_names)} tools (via _tools): {', '.join(tool_names)}")
        else:
            print("❌ Cannot access tools list")
            return False

    expected_tools = [
        "runtime_adg_status",
        "runtime_adg_query",
        "runtime_adg_compare",
        "meta_learning_insights",
        "learning_pipeline_status",
        "cross_repo_import",
        "learning_state_management",
    ]

    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        return False

    print("✅ All expected Meta-learning tools are registered")

    # Test runtime_adg_query parameter validation
    invalid_result = server_module.runtime_adg_query(time_window_hours=0)
    if "must be between" not in invalid_result.get("error", ""):
        print("❌ runtime_adg_query() time_window validation failed")
        return False

    # Test runtime_adg_status function
    status_result = server_module.runtime_adg_status()
    if not isinstance(status_result.get("total_snapshots"), int):
        print("❌ runtime_adg_status() total_snapshots not integer")
        return False

    try:
        status_result = server_module.runtime_adg_status()
        print(f"✅ runtime_adg_status() returned: {type(status_result).__name__}")

        required_fields = ["timestamp", "total_snapshots", "health_status", "freshness"]
        for field in required_fields:
            if field not in status_result:
                print(f"❌ Missing field in runtime_adg_status result: {field}")
                return False

        print("✅ runtime_adg_status() has all required fields")

    except Exception as e:
        print(f"❌ Error testing runtime_adg_status(): {e}")
        return False

    # Test learning_pipeline_status function
    try:
        pipeline_result = server_module.learning_pipeline_status()
        print(f"✅ learning_pipeline_status() returned: {type(pipeline_result).__name__}")

        required_fields = ["timestamp", "pipeline_status", "component_health", "components"]
        for field in required_fields:
            if field not in pipeline_result:
                print(f"❌ Missing field in learning_pipeline_status result: {field}")
                return False

        print("✅ learning_pipeline_status() has all required fields")

    except Exception as e:
        print(f"❌ Error testing learning_pipeline_status(): {e}")
        return False

    print("✅ System Learning Meta-Learning MCP Server test passed!")
    return True

async def test_phase3_mcp_server():
    """Test Phase 3 MCP server."""
    print("=== Phase 3 MCP Server Test Suite ===\n")

    success = await test_meta_learning_mcp()

    print("\n=== Test Results ===")
    print(f"System Learning Meta-Learning MCP: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"Overall Phase 3 MCP Status: {'✅ TEST PASSED' if success else '❌ TEST FAILED'}")

    return success

if __name__ == "__main__":
    success = asyncio.run(test_phase3_mcp_server())
    sys.exit(0 if success else 1)
