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
from collections.abc import Sequence
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
        raise ImportError("mcp package not found. Install with: pip install mcp")
    logger = logging.getLogger(name)
    logger.info("Creating FastMCP server: %s", name)
    return FastMCP(name, **_resolve_fastmcp_kwargs(name, instructions))


def run_server(mcp: FastMCP, *, transport: str = "stdio") -> None:
    """Run the MCP server using the standard repo entrypoint."""
    logger = logging.getLogger(getattr(mcp, "name", "mcp"))
    logger.info("Starting MCP server (transport=%s)", transport)
    mcp.run(transport=transport)


def mcp_process_identity(server_id: str) -> dict[str, Any]:
    """Return host-attachment proof fields for Codex MCP lifecycle cleanup."""
    normalized = server_id.strip().lower().replace("-", "_")
    pid = os.getpid()
    env_key = f"CODEX_MCP_ATTACHED_{normalized.upper()}_PID"
    return {
        "server_id": normalized,
        "pid": pid,
        "ppid": os.getppid(),
        "cwd": str(Path.cwd()),
        "attached_pid_env_key": env_key,
        "attached_pid_env": f"{env_key}={pid}",
        "attached_pid_arg": f"{normalized}={pid}",
        "cleanup_arg": f"--codex-attached-pid {normalized}={pid}",
    }


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
        ``docs/archive/windsurf/legacy-tree/governance_scripts/mcp_fleet_health.py`` to probe 8 different
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
        base: dict[str, Any] = {
            "status": "ok",
            "server": server_name,
            "process": mcp_process_identity(server_name),
        }
        if extra is None:
            return base
        try:
            merged = extra()
            if isinstance(merged, dict):
                base.update(merged)
            return base
        except (OSError, RuntimeError, ValueError, TypeError, ImportError) as exc:
            base["status"] = "error"
            base["error"] = f"{type(exc).__name__}: {exc}"
            return base

    _health.__name__ = tool_name
    _health.__doc__ = (
        f"Health probe for the {server_name} MCP server.\n\n"
        "Uniform fleet-health endpoint. Returns {status, server, ...}. "
        "Never raises; errors are surfaced via status='error' + error field."
    )
    mcp.tool()(_health)


def _normalize_marker_text(value: str) -> str:
    return value.strip().strip("\"'").lower().replace("\\", "/")


def _match_cmdline_marker(cmdline: list[Any], markers: tuple[str, ...]) -> str | None:
    """Match only direct argv entries for script/module MCP launches."""
    normalized_markers = tuple(_normalize_marker_text(marker) for marker in markers)
    for raw_part in cmdline:
        part = _normalize_marker_text(str(raw_part))
        for marker in normalized_markers:
            if not marker:
                continue
            if "/" in marker:
                part_without_suffix = part[:-3] if part.endswith(".py") else part
                marker_without_suffix = marker[:-3] if marker.endswith(".py") else marker
                if part_without_suffix == marker_without_suffix or part_without_suffix.endswith(
                    f"/{marker_without_suffix}"
                ):
                    return marker
                continue
            if part == marker or part.endswith(f"/{marker}"):
                return marker
    return None


def _is_windows_launcher_wrapper(process_name: Any, cmdline: list[Any]) -> bool:
    """Return True for shell wrappers that launch the real MCP child process.

    Codex Desktop projects repo MCPs through ``cmd /c ...`` on Windows. Killing
    that wrapper during MCP initialize can close the host stdio pipe even when
    the Python child server is healthy. The single-instance guard should target
    the actual Python server process, never the shell launcher wrapped around it.
    """
    name = Path(str(process_name or "")).name.lower()
    if not name and cmdline:
        name = Path(str(cmdline[0])).name.lower()
    if name not in {"cmd.exe", "cmd", "powershell.exe", "powershell", "pwsh.exe", "pwsh"}:
        return False
    normalized = {_normalize_marker_text(str(part)) for part in cmdline}
    return bool({"/c", "-c", "-command", "-encodedcommand"} & normalized)


def guard_single_instance(
    script_marker: "str | Sequence[str]",
    *,
    skip_env: str | None = None,
) -> None:
    """Terminate any other process whose cmdline contains ``script_marker``.

    Purpose (MCP fleet standardization, 2026-04-22):
        legacy editor occasionally spawns a second MCP server process on reconnect
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
        script_marker: Module or script-path marker uniquely identifying this
            server's direct argv entry in ``proc.cmdline``. When a sequence is
            provided, a process is matched if ANY marker is present as a direct
            argv module/path argument. Use a sequence when the server can be
            invoked in multiple forms, e.g. both ``python -m
            tools.adg.mcp.server`` (dot-separated) and ``python
            tools/adg/mcp/server.py`` (slash-separated).
        skip_env: Optional env var name. When set to ``"1"``, the guard is
            skipped. Use for test harnesses that legitimately spawn siblings.
    """
    # Normalize marker to a tuple for uniform matching logic downstream.
    if isinstance(script_marker, str):
        markers: tuple[str, ...] = (script_marker,)
    else:
        markers = tuple(str(m) for m in script_marker if m)
    if not markers:
        logging.getLogger("mcp_bootstrap").warning("GUARD_NOOP: empty marker list, guard disabled")
        return
    marker_display = markers[0] if len(markers) == 1 else list(markers)

    if skip_env and os.environ.get(skip_env) == "1":
        logging.getLogger("mcp_bootstrap").info(
            "GUARD_SKIPPED: %s=1 (script_marker=%s)", skip_env, marker_display
        )
        return

    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError:
        logging.getLogger("mcp_bootstrap").warning(
            "GUARD_UNAVAILABLE: psutil not installed; concurrent-process "
            "deadlock guard disabled for marker=%s",
            marker_display,
        )
        return

    my_pid = os.getpid()
    killed: list[int] = []
    deferred: list[int] = []
    logger = logging.getLogger("mcp_bootstrap")

    # Heartbeat-aware sibling check (2026-04-23 RCA hardening; F5.1 strict
    # authority: liveness verified against process table, not just file mtime).
    # `MCP_GUARD_FORCE_KILL=1` bypasses and restores the pre-hardening
    # "kill every sibling" behavior for debugging or emergency use.
    force_kill = os.environ.get("MCP_GUARD_FORCE_KILL") == "1"
    heartbeat_owner_pids: set[int] = set()
    if not force_kill:
        try:
            from tools.mcp.mcp_heartbeat import is_heartbeat_authoritative, read_heartbeat  # noqa: PLC0415

            # Authoritative: heartbeat file fresh AND owning PID alive + non-zombie.
            # A wedged or terminating sibling no longer earns a deferral.
            for marker in markers:
                if not is_heartbeat_authoritative(marker):
                    continue
                heartbeat = read_heartbeat(marker)
                if heartbeat is not None:
                    _ts, owner_pid = heartbeat
                    heartbeat_owner_pids.add(owner_pid)
        except ImportError:
            heartbeat_owner_pids = set()

    for proc in psutil.process_iter(attrs=("pid", "name", "cmdline")):
        try:
            if proc.info["pid"] == my_pid:
                continue
            cmdline = proc.info.get("cmdline") or []
            if _is_windows_launcher_wrapper(proc.info.get("name"), cmdline):
                logger.debug(
                    "GUARD_SKIP_WRAPPER: pid=%d name=%s cmdline=%s",
                    proc.info["pid"],
                    proc.info.get("name"),
                    " ".join(str(c) for c in cmdline)[:200],
                )
                continue
            matched_marker = _match_cmdline_marker(cmdline, markers)
            if matched_marker is None:
                continue

            # If a fresh heartbeat is present AND force_kill is not set, defer
            # the kill: the sibling is active and likely serving a live
            # legacy editor client. Clobbering it would produce the split-brain
            # failure mode documented in the RCA.
            if proc.info["pid"] in heartbeat_owner_pids and not force_kill:
                logger.warning(
                    "GUARD_DEFERRED: pid=%d owns fresh heartbeat; skipping "
                    "termination to avoid split-brain "
                    "(matched=%s marker=%s). Set MCP_GUARD_FORCE_KILL=1 to override.",
                    proc.info["pid"],
                    matched_marker,
                    marker_display,
                )
                deferred.append(proc.info["pid"])
                continue

            logger.warning(
                "GUARD_DETECTED: pid=%d cmdline=%s -- terminating "
                "(matched=%s marker=%s heartbeat_fresh=%s force_kill=%s)",
                proc.info["pid"],
                " ".join(str(c) for c in cmdline)[:200],
                matched_marker,
                marker_display,
                bool(heartbeat_owner_pids),
                force_kill,
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
        logger.info(
            "GUARD_COMPLETE: terminated pids=%s deferred=%s (marker=%s)",
            killed,
            deferred,
            marker_display,
        )
    elif deferred:
        logger.info(
            "GUARD_DEFERRED_ALL: no terminations; %d fresh sibling(s) preserved (marker=%s)",
            len(deferred),
            marker_display,
        )
    else:
        logger.info("GUARD_CLEAN: no sibling processes (marker=%s)", marker_display)

    # Start a daemon heartbeat writer for this server. Subsequent bootstraps
    # will see our heartbeat as fresh and skip terminating us. Safe to call
    # even if heartbeat_fresh was True (we are THE fresh sibling from here on).
    # Opt out via `MCP_HEARTBEAT_DISABLE=1`.
    if os.environ.get("MCP_HEARTBEAT_DISABLE") != "1":
        try:
            from tools.mcp.mcp_heartbeat import start_heartbeat_writer  # noqa: PLC0415

            # Register a heartbeat per marker so multi-form markers all show up.
            for marker in markers:
                start_heartbeat_writer(marker)
            logger.info(
                "HEARTBEAT_STARTED: markers=%s interval=10s stale_after=30s",
                list(markers),
            )
        except ImportError:
            logger.debug("HEARTBEAT_UNAVAILABLE: mcp_heartbeat module missing")
        except (OSError, RuntimeError) as exc:
            logger.warning("HEARTBEAT_START_FAILED: %s", exc)


_prewarm_registry: list[tuple[str, Callable[[], None]]] = []


def register_prewarm(fn: Callable[[], None], *, name: str) -> None:
    """Register a zero-arg callable to run on a daemon thread at server start.

    Purpose (MCP fleet standardization, 2026-04-22):
        Prewarm logic was forked 3 ways: ``vector_db_server._start_background_prewarm``
        (threading.Thread + try/except, ~40 lines), ``otel_mcp._prewarm``
        (loader.prewarm + lifecycle), ``adg_sqlite._init_service`` (eager
        singleton). This registry gives one protocol: declare prewarm
        callables during import, invoke them all from ``run_prewarms()`` in
        ``__main__`` before ``run_server()``.

    Each callable runs on its own daemon thread. Exceptions are logged but
    never propagated — prewarm failure should never block the MCP transport.

    Args:
        fn: Zero-arg callable performing the warmup work (open client,
            load model, seed caches, etc.).
        name: Human-readable identifier used in thread name + log lines.
    """
    _prewarm_registry.append((name, fn))


def run_prewarms() -> None:
    """Start a daemon thread for each registered prewarm callable."""
    import threading as _threading
    import time as _time

    logger = logging.getLogger("mcp_bootstrap")

    def _wrap(wname: str, wfn: Callable[[], None]) -> None:
        t0 = _time.monotonic()
        try:
            wfn()
            logger.info("PREWARM_DONE: %s (%.2fs)", wname, _time.monotonic() - t0)
        except (OSError, RuntimeError, ValueError, TypeError, ImportError) as exc:
            logger.warning("PREWARM_FAILED: %s: %s", wname, exc)

    for wname, wfn in _prewarm_registry:
        _threading.Thread(
            target=_wrap,
            args=(wname, wfn),
            daemon=True,
            name=f"mcp-prewarm-{wname}",
        ).start()
