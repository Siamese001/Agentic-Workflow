#!/usr/bin/env python3
"""ADG MCP Server launcher with proper path setup."""

import os
import sys

# Ensure proper path
os.chdir(r"C:\Git\Agentic-Workflow")
sys.path.insert(0, r"C:\Git\Agentic-Workflow")

# Import and run server
from tools.adg.mcp.server import _init_service, _log, mcp

if __name__ == "__main__":
    _log.info("Starting adg_mcp server (stdio transport)...")
    try:
        _init_service()
    except Exception as e:
        _log.error("FATAL: Could not initialize ADGService: %s", e)
        sys.exit(1)
    mcp.run(transport="stdio")
    _log.info("Server exited")
