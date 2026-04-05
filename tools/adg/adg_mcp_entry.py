#!/usr/bin/env python3
"""ADG MCP Server — direct entry point."""

import os
import sys

# Ensure tools is in path
sys.path.insert(0, r"C:\Git\Agentic-Workflow")
os.chdir(r"C:\Git\Agentic-Workflow")

# Import and run the actual server
from tools.adg.mcp.server import _init_service, mcp

if __name__ == "__main__":
    try:
        _init_service()
    except Exception as e:
        # Log to file since stderr breaks stdio transport
        with open(os.path.expanduser("~/adg_fatal.log"), "w") as f:
            f.write(f"FATAL: {e}\n")
        sys.exit(1)

    mcp.run(transport="stdio")
