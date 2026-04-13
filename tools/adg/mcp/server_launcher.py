#!/usr/bin/env python3
# DEPRECATED: canonical launch path is `python -m tools.adg.mcp.server`
# (configured in .windsurf/mcp_config.json).  This file is retained for
# emergency manual use only.  Do not reference from mcp_config.json.
"""ADG MCP Server launcher — DEPRECATED thin wrapper (use -m tools.adg.mcp.server)."""

import os
import sys

# Resolve repo root dynamically (this file is at tools/adg/mcp/server_launcher.py)
_REPO_ROOT = str(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
os.chdir(_REPO_ROOT)
sys.path.insert(0, _REPO_ROOT)

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
