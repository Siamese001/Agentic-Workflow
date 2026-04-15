"""
Redis MCP Server entrypoint.

Refactored into a small entrypoint plus a dedicated package:

- tools/mcp/redis_mcp/server.py        -> server construction and registration
- tools/mcp/redis_mcp/client.py        -> redis import, config, pool, safe connect
- tools/mcp/redis_mcp/read_tools.py    -> read-only inspection tools
- tools/mcp/redis_mcp/admin_tools.py   -> bounded invalidation tools
- tools/mcp/redis_mcp/scan_utils.py    -> reusable SCAN helpers
"""

from __future__ import annotations

import logging

from tools.mcp.redis_mcp.server import build_mcp_server, run_mcp_server

logger = logging.getLogger(__name__)

mcp = build_mcp_server()

if __name__ == "__main__":
    logger.info("Starting Redis MCP Server")
    run_mcp_server(mcp)
