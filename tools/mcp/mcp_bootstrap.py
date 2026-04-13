"""
Shared MCP Server Bootstrap — Standardized initialization for all Python MCP servers.

This module eliminates duplicated boilerplate across all 7 Python MCP servers
(adg_sqlite, memory, redis, otel_mcp, vector_db, enhanced_http, pytest_mcp)
by providing a single, tested entry point for:

  1. Repo-root sys.path bootstrapping
  2. Logging to stderr (never stdout — MCP stdio transport safety)
  3. Environment safety: TOKENIZERS_PARALLELISM, PYTHONUNBUFFERED
  4. FastMCP import with clear error on missing dependency
  5. Standardized entry point via run_server()

Usage in any MCP server::

    from tools.mcp.mcp_bootstrap import create_mcp_server, run_server

    mcp = create_mcp_server("my-server", "Description here")

    @mcp.tool()
    def my_tool(arg: str) -> str:
        return f"Hello {arg}"

    if __name__ == "__main__":
        run_server(mcp)

Pattern compliance
------------------
All working MCP servers follow this exact pattern:
- FastMCP("name") + @mcp.tool() decorators
- mcp.run(transport="stdio") entry point
- logging.basicConfig(stream=sys.stderr)
- sys.path.insert(0, repo_root)
- os.environ["TOKENIZERS_PARALLELISM"] = "false"

Servers that deviated (low-level Server API, anyio.run, asyncio.ensure_future)
caused persistent hanging on Windows stdio transport.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# ── Repo-root bootstrap — idempotent ──────────────────────────────────────
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ── MCP stdio transport safety ────────────────────────────────────────────
# These MUST be set before any transformer/tokenizer library is imported.
# tokenizers spawns parallel processes that inherit stdin/stdout and corrupt
# the JSON-RPC stream.  PYTHONUNBUFFERED prevents output buffering issues.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

# ── Logging — always stderr, never stdout ─────────────────────────────────
# basicConfig is a no-op if handlers already exist; force=True overrides that.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
)

# ── FastMCP import with clear error ───────────────────────────────────────
try:
    from mcp.server.fastmcp import FastMCP  # noqa: F401 — re-exported
except ImportError:
    print(
        "[mcp_bootstrap] FATAL: mcp package not found. Install with: pip install mcp",
        file=sys.stderr,
    )
    sys.exit(1)


def create_mcp_server(name: str, instructions: str = "") -> FastMCP:
    """Create a FastMCP server instance with standardized configuration.

    Args:
        name: Server name (e.g. "vector-db", "redis-mcp", "otel-mcp")
        instructions: Optional description surfaced to the MCP client

    Returns:
        Configured FastMCP instance ready for @mcp.tool() decorators
    """
    logger = logging.getLogger(name)
    logger.info("Creating FastMCP server: %s", name)
    return FastMCP(name, instructions=instructions) if instructions else FastMCP(name)


def run_server(mcp: FastMCP, *, transport: str = "stdio") -> None:
    """Run the MCP server — standardized entry point.

    This is the ONLY blessed way to start a Python MCP server in this repo.
    Using anyio.run(), asyncio.ensure_future, or low-level Server API
    has been proven to cause hanging on Windows stdio transport.

    Args:
        mcp: FastMCP instance with tools registered
        transport: Transport protocol ("stdio" for Windsurf)
    """
    logger = logging.getLogger(mcp.name if hasattr(mcp, "name") else "mcp")
    logger.info("Starting MCP server (transport=%s)", transport)
    mcp.run(transport=transport)
