#!/usr/bin/env python3
"""ADG MCP Server launcher - clean stdio version."""

import logging
import os
import sys

# Redirect logs to file instead of stderr
log_file = os.path.expanduser("~/adg_mcp.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

os.chdir(r"C:\Git\Agentic-Workflow")
sys.path.insert(0, r"C:\Git\Agentic-Workflow")

from tools.adg.mcp.server import _init_service, mcp

if __name__ == "__main__":
    try:
        _init_service()
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"FATAL: {e}\n")
        sys.exit(1)
    mcp.run(transport="stdio")
