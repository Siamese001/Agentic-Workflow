"""
Shared MCP Server Bootstrap — standardized initialization for Python MCP servers.

This module keeps transport-specific concerns in one place:
1. Repo-root sys.path bootstrapping
2. Logging to stderr only (never stdout on stdio MCP)
3. Environment safety for tokenizer / buffering behavior
4. FastMCP import with clear failure messaging
5. Optional worker-cap wiring when supported by the installed FastMCP
"""

from __future__ import annotations

import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
)

# Lazy import to allow module to be imported without MCP installed
# FastMCP will be imported on first use in create_mcp_server()
_FASTMCP_AVAILABLE = False
try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
    _FASTMCP_AVAILABLE = True
except ImportError:
    FastMCP = None  # type: ignore


def _parse_positive_int_env(name: str) -> int | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        logging.getLogger("mcp_bootstrap").warning(
            "%s=%r is invalid — expected a positive integer; ignoring",
            name,
            raw,
        )
        return None
    if value < 1:
        logging.getLogger("mcp_bootstrap").warning(
            "%s=%r is invalid — expected >= 1; ignoring",
            name,
            raw,
        )
        return None
    return value


def _resolve_fastmcp_kwargs(name: str, instructions: str) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if instructions:
        kwargs["instructions"] = instructions

    workers = _parse_positive_int_env("MCP_MAX_THREADPOOL_WORKERS")
    if workers is None:
        return kwargs

    logger = logging.getLogger(name)
    try:
        params = inspect.signature(FastMCP).parameters
    except (TypeError, ValueError):
        logger.warning(
            "Could not inspect FastMCP signature; MCP_MAX_THREADPOOL_WORKERS=%d will be ignored",
            workers,
        )
        return kwargs

    for candidate in ("workers", "thread_pool_workers", "max_workers"):
        if candidate in params:
            kwargs[candidate] = workers
            logger.info("FastMCP concurrency cap enabled: %s=%d", candidate, workers)
            return kwargs

    logger.warning(
        "MCP_MAX_THREADPOOL_WORKERS=%d is set but the installed FastMCP constructor "
        "does not expose a supported worker parameter",
        workers,
    )
    return kwargs


def create_mcp_server(name: str, instructions: str = "") -> FastMCP:
    """Create a FastMCP server instance with standardized configuration.
    
    Raises:
        ImportError: If the mcp package is not installed.
    """
    if not _FASTMCP_AVAILABLE or FastMCP is None:
        raise ImportError(
            "mcp package not found. Install with: pip install mcp"
        )
    logger = logging.getLogger(name)
    logger.info("Creating FastMCP server: %s", name)
    return FastMCP(name, **_resolve_fastmcp_kwargs(name, instructions))


def run_server(mcp: FastMCP, *, transport: str = "stdio") -> None:
    """Run the MCP server using the standard repo entrypoint."""
    logger = logging.getLogger(getattr(mcp, "name", "mcp"))
    logger.info("Starting MCP server (transport=%s)", transport)
    mcp.run(transport=transport)
