#!/usr/bin/env python3
"""
Pytest MCP Server - Test discovery, execution, and analysis.

Provides pytest integration for Windsurf with comprehensive test management.
Uses the canonical mcp_bootstrap pattern (FastMCP + @mcp.tool() + run_server)
to avoid the Windows stdio transport hangs caused by low-level Server + anyio.run.
Subprocess calls use safe_run() to enforce stdin=DEVNULL / stdout=PIPE / stderr=PIPE.
"""

from __future__ import annotations

from tools.mcp.mcp_bootstrap import create_mcp_server, run_server
from tools.mcp.pytest_support.services import (
    analyze_test_coverage,
    discover_tests,
    get_test_details,
    list_pytest_config,
    run_tests,
)

mcp = create_mcp_server(
    "pytest-mcp",
    "Test discovery, execution, coverage analysis, and pytest config inspection.",
)

# ── Tools ────────────────────────────────────────────────────────────────────
mcp.tool()(discover_tests)
mcp.tool()(run_tests)
mcp.tool()(get_test_details)
mcp.tool()(analyze_test_coverage)
mcp.tool()(list_pytest_config)


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_server(mcp)
