#!/usr/bin/env python3
# DEPRECATED: canonical launch path is `python -m tools.adg.mcp.server`
# (configured in .windsurf/mcp_config.json).  This file is retained for
# emergency manual use only.  Do not reference from mcp_config.json.
"""ADG MCP Server — DEPRECATED direct entry point (use -m tools.adg.mcp.server)."""

import os
import sys

# Resolve repo root dynamically (this file is at tools/adg/adg_mcp_entry.py)
_REPO_ROOT = str(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _REPO_ROOT)
os.chdir(_REPO_ROOT)

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
