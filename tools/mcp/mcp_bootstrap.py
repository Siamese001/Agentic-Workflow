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
from typing import Any, Callable

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


def register_standard_health(
    mcp: FastMCP,
    server_name: str,
    extra: "Callable[[], dict[str, Any]] | None" = None,
) -> None:
    """Register a uniform ``{server_name}_health`` tool on the given FastMCP.

    Purpose (MCP fleet standardization, 2026-04-22):
        Before this helper existed, each MCP server implemented health probing
        differently: adg_sqlite used ``adg_health``, redis used ``redis_health``,
        otel_mcp used ``otel_status`` + ``otel_server_info``, vector_db used
        ``readiness``, and memory/pytest_mcp/enhanced_http had no explicit
        health endpoint at all. The inconsistency forced
        ``.windsurf/scripts/mcp_fleet_health.py`` to probe 8 different
        preconditions per server instead of calling one uniform endpoint.

    Contract:
        Registers a tool named ``{server_name}_health`` returning a dict with
        at minimum ``{"status": "ok", "server": <server_name>}``. If
        ``extra`` is provided, it is called and its result merged into the
        response; exceptions from ``extra`` are surfaced as ``status="error"``
        with ``error`` field (never re-raised — health must never crash).

    Args:
        mcp: FastMCP instance to register the tool on.
        server_name: Stable server name used for both the tool name and the
            ``server`` field. Lowercase, snake_case.
        extra: Optional zero-arg callable producing additional fields
            (version, db_path, backing store state, etc.).
    """
    tool_name = f"{server_name}_health"

    def _health() -> dict[str, Any]:
        base: dict[str, Any] = {"status": "ok", "server": server_name}
        if extra is None:
            return base
        try:
            merged = extra()
            if isinstance(merged, dict):
                base.update(merged)
            return base
        except (OSError, RuntimeError, ValueError, TypeError, ImportError) as exc:
            return {"status": "error", "server": server_name, "error": f"{type(exc).__name__}: {exc}"}

    _health.__name__ = tool_name
    _health.__doc__ = (
        f"Health probe for the {server_name} MCP server.\n\n"
        "Uniform fleet-health endpoint. Returns {status, server, ...}. "
        "Never raises; errors are surfaced via status='error' + error field."
    )
    mcp.tool()(_health)


def guard_single_instance(script_marker: str, *, skip_env: str | None = None) -> None:
    """Terminate any other process whose cmdline contains ``script_marker``.

    Purpose (MCP fleet standardization, 2026-04-22):
        Windsurf occasionally spawns a second MCP server process on reconnect
        without terminating the first. Two concurrent instances deadlock on
        shared resources: ChromaDB's SQLite WAL lock (vector_db), the memory
        SQLite store, the ADG snapshot, etc. Originally this guard lived in
        ``tools/mcp/vector_db_server.py`` as ``_kill_zombie_siblings()`` for
        a vector_db-only scenario. Extracted here so every Python MCP server
        can adopt it in one line.

    Safe by construction:
        - Matches on a specific script filename substring (never arbitrary python)
        - Skips own PID explicitly
        - Fails soft when psutil is not installed
        - Honors an opt-out env var for test isolation
        - Never raises; logs and returns

    Args:
        script_marker: Substring uniquely identifying this server's script in
            ``proc.cmdline`` (e.g. ``"vector_db_server.py"``, ``"adg/mcp/server"``).
        skip_env: Optional env var name. When set to ``"1"``, the guard is
            skipped. Use for test harnesses that legitimately spawn siblings.
    """
    if skip_env and os.environ.get(skip_env) == "1":
        logging.getLogger("mcp_bootstrap").info(
            "GUARD_SKIPPED: %s=1 (script_marker=%s)", skip_env, script_marker
        )
        return

    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError:
        logging.getLogger("mcp_bootstrap").warning(
            "GUARD_UNAVAILABLE: psutil not installed; concurrent-process "
            "deadlock guard disabled for marker=%s",
            script_marker,
        )
        return

    my_pid = os.getpid()
    killed: list[int] = []
    logger = logging.getLogger("mcp_bootstrap")

    for proc in psutil.process_iter(attrs=("pid", "name", "cmdline")):
        try:
            if proc.info["pid"] == my_pid:
                continue
            cmdline = proc.info.get("cmdline") or []
            if not any(script_marker in str(part) for part in cmdline):
                continue
            logger.warning(
                "GUARD_DETECTED: pid=%d cmdline=%s -- terminating (marker=%s)",
                proc.info["pid"],
                " ".join(str(c) for c in cmdline)[:200],
                script_marker,
            )
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
            killed.append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as exc:
            logger.debug("GUARD_SKIP: pid=%s reason=%s", proc.info.get("pid"), exc)

    if killed:
        logger.info("GUARD_COMPLETE: terminated pids=%s (marker=%s)", killed, script_marker)
    else:
        logger.info("GUARD_CLEAN: no sibling processes (marker=%s)", script_marker)
