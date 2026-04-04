#!/usr/bin/env python3
"""
Test script for Phase 2 MCP Servers
Tests Guardian Governance and Pytest Test Orchestration MCP servers.
"""

import asyncio
import importlib.util
import sys
from pathlib import Path


async def test_guardian_mcp():
    """Test Guardian Governance MCP server."""
    print("Testing Guardian Governance MCP Server...")

    server_path = Path("tools/governance/guardian_mcp_server.py")
    if not server_path.exists():
        print("❌ Guardian server file not found")
        return False

    spec = importlib.util.spec_from_file_location("guardian_mcp_server", server_path)
    server_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(server_module)
        print("✅ Guardian server module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Guardian server module: {e}")
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
        "guardian_status",
        "guardian_run",
        "guardian_report",
        "guardian_manifest",
        "guardian_healing",
        "guardian_audit",
        "guardian_impact_analysis",
        "guardian_registry"
    ]

    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        return False

    print("✅ All expected Guardian tools are registered")

    # Test guardian_run parameter validation
    invalid_result = server_module.guardian_run("", timeout=300)
    if "cannot be empty" not in invalid_result.get("error", ""):
        print("❌ guardian_run() empty name validation failed")
        return False

    # Test guardian_status function
    status_result = server_module.guardian_status()
    if not isinstance(status_result.get("overall_health"), (int, float)):
        print("❌ guardian_status() overall_health not numeric")
        return False

    try:
        status_result = server_module.guardian_status()
        print(f"✅ guardian_status() returned: {type(status_result).__name__}")

        required_fields = ["timestamp", "total_guardians", "status_counts", "overall_health"]
        for field in required_fields:
            if field not in status_result:
                print(f"❌ Missing field in guardian_status result: {field}")
                return False

        print("✅ guardian_status() has all required fields")

    except Exception as e:
        print(f"❌ Error testing guardian_status(): {e}")
        return False

    print("✅ Guardian Governance MCP Server test passed!")
    return True

async def test_pytest_mcp():
    """Test Pytest Test Orchestration MCP server."""
    print("\nTesting Pytest Test Orchestration MCP Server...")

    server_path = Path("tools/testing/pytest_mcp_server.py")
    if not server_path.exists():
        print("❌ Pytest server file not found")
        return False

    spec = importlib.util.spec_from_file_location("pytest_mcp_server", server_path)
    server_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(server_module)
        print("✅ Pytest server module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Pytest server module: {e}")
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
        "pytest_status",
        "pytest_run_adg_impact",
        "pytest_run_guardians",
        "pytest_run_smoke",
        "pytest_coverage_analysis",
        "pytest_failure_analysis"
    ]

    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        return False

    print("✅ All expected Pytest tools are registered")

    # Test pytest_status function
    try:
        status_result = server_module.pytest_status()
        print(f"✅ pytest_status() returned: {type(status_result).__name__}")

        required_fields = ["timestamp", "cache_available", "coverage_available", "total_test_files"]
        for field in required_fields:
            if field not in status_result:
                print(f"❌ Missing field in pytest_status result: {field}")
                return False

        print("✅ pytest_status() has all required fields")

    except Exception as e:
        print(f"❌ Error testing pytest_status(): {e}")
        return False

    print("✅ Pytest Test Orchestration MCP Server test passed!")
    return True

async def test_phase2_mcp_servers():
    """Test both Phase 2 MCP servers."""
    print("=== Phase 2 MCP Servers Test Suite ===\n")

    guardian_success = await test_guardian_mcp()
    pytest_success = await test_pytest_mcp()

    print("\n=== Test Results ===")
    print(f"Guardian Governance MCP: {'✅ PASS' if guardian_success else '❌ FAIL'}")
    print(f"Pytest Test Orchestration MCP: {'✅ PASS' if pytest_success else '❌ FAIL'}")

    overall_success = guardian_success and pytest_success
    print(f"Overall Phase 2 MCP Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")

    return overall_success

if __name__ == "__main__":
    success = asyncio.run(test_phase2_mcp_servers())
    sys.exit(0 if success else 1)
