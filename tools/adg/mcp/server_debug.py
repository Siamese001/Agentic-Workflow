#!/usr/bin/env python3
"""ADG MCP Server with clean stdio - NO stdout redirection."""

import logging
import os
import sys

# CRITICAL: Log to file only, never stdout/stderr
log_path = os.path.expanduser("~/adg_server.log")
logging.basicConfig(filename=log_path, level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
_log = logging.getLogger("adg_mcp")

os.chdir(r"C:\Git\Agentic-Workflow")
sys.path.insert(0, r"C:\Git\Agentic-Workflow")

from tools.adg.mcp.server import _init_service, mcp

if __name__ == "__main__":
    try:
        _init_service()
    except Exception as e:
        _log.error(f"FATAL: {e}")
        sys.exit(1)
    mcp.run(transport="stdio")
