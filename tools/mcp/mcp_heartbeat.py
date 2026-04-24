"""MCP server heartbeat file writer/reader.

Closes the GUARD_CLEAN hardening deferred item from
`docs/reports/plans/rca-otel-mcp-transport-closed-2026-04-23.md`.

Problem
-------
`guard_single_instance()` unconditionally terminates every sibling process
that matches its script marker. When Windsurf opens/closes several windows
in quick succession, each new window's GUARD_CLEAN kills the previous
window's MCP servers, then the new window may itself close before its
servers finish bootstrapping \u2014 leaving zero live MCP servers across all
Windsurf instances. This is the split-brain failure mode recorded in the
RCA: 2026-04-23 saw all 7 Python MCP servers dead after 5 window restarts.

Fix
---
This module provides a lightweight heartbeat layer that `guard_single_instance`
consults BEFORE terminating a sibling:

    1. Each server starts a background daemon thread that touches
       `artifacts/mcp_heartbeat/<sanitized_marker>.hb` every
       HEARTBEAT_INTERVAL_SECONDS. The file content is a single line
       `<unix_timestamp>:<pid>`.

    2. Before terminating a sibling, GUARD_CLEAN reads the heartbeat and
       checks if it's FRESH (within HEARTBEAT_STALE_AFTER_SECONDS). If so,
       the sibling is considered ACTIVE and is NOT killed.

    3. If the heartbeat file is missing (backward compat) or stale, the
       sibling is considered ORPHAN and is terminated as before.

    4. Escape hatch: `MCP_GUARD_FORCE_KILL=1` forces the legacy "kill every
       sibling" behavior, bypassing the heartbeat check.

Never raises. Fails open (treats missing/corrupt heartbeat as absent).
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time
from pathlib import Path

_logger = logging.getLogger("mcp_heartbeat")

# Tunables. Conservative: heartbeat every 10s, stale after 30s (3 missed beats).
HEARTBEAT_INTERVAL_SECONDS: float = 10.0
HEARTBEAT_STALE_AFTER_SECONDS: float = 30.0

_HEARTBEAT_DIR = Path("artifacts/mcp_heartbeat")


def _sanitize_marker(marker: str) -> str:
    """Collapse a script marker into a filesystem-safe filename stem."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", marker).strip("_") or "_unknown"


def _heartbeat_path(marker: str) -> Path:
    return _HEARTBEAT_DIR / f"{_sanitize_marker(marker)}.hb"


def write_heartbeat(marker: str) -> bool:
    """Write a single heartbeat tick for `marker`. Returns True on success."""
    try:
        _HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
        path = _heartbeat_path(marker)
        payload = f"{time.time():.3f}:{os.getpid()}\n"
        path.write_text(payload, encoding="utf-8")
        return True
    except (OSError, ValueError) as exc:
        _logger.debug("heartbeat_write_failed marker=%s error=%s", marker, exc)
        return False


def read_heartbeat(marker: str) -> tuple[float, int] | None:
    """Return (timestamp, pid) for marker, or None if missing/corrupt."""
    try:
        path = _heartbeat_path(marker)
        if not path.exists():
            return None
        line = path.read_text(encoding="utf-8").strip()
        ts_str, _, pid_str = line.partition(":")
        return (float(ts_str), int(pid_str))
    except (OSError, ValueError) as exc:
        _logger.debug("heartbeat_read_failed marker=%s error=%s", marker, exc)
        return None


def is_heartbeat_fresh(
    marker: str,
    now: float | None = None,
    stale_after: float = HEARTBEAT_STALE_AFTER_SECONDS,
) -> bool:
    """True iff a heartbeat exists for `marker` and was written recently."""
    hb = read_heartbeat(marker)
    if hb is None:
        return False
    ts, _pid = hb
    resolved_now = now if now is not None else time.time()
    return (resolved_now - ts) <= stale_after


def is_heartbeat_authoritative(
    marker: str,
    now: float | None = None,
    stale_after: float = HEARTBEAT_STALE_AFTER_SECONDS,
) -> bool:
    """True iff a heartbeat is fresh AND its owning PID is alive + non-zombie.

    F5.1 hardening (2026-04-23): a process can be wedged (zombie, stopped,
    or mid-crash) while its heartbeat thread has just managed to touch the
    file. Relying on `is_heartbeat_fresh` alone therefore defers kills on
    dying siblings and keeps the split-brain failure mode alive.

    This helper performs an additional liveness check against the OS
    process table via psutil. If psutil is unavailable (soft dep), we fall
    back to `is_heartbeat_fresh` — never worse than the prior behavior.

    Never raises; fails open (returns False) on any unexpected condition.
    """
    if not is_heartbeat_fresh(marker, now=now, stale_after=stale_after):
        return False
    hb = read_heartbeat(marker)
    if hb is None:
        return False
    _ts, pid = hb
    try:
        import psutil  # type: ignore[import-not-found]  # noqa: PLC0415
    except ImportError:
        # psutil missing: degrade gracefully to fresh-only semantics.
        return True
    try:
        proc = psutil.Process(pid)
        if not proc.is_running():
            return False
        status = proc.status()
        # ZOMBIE / STOPPED / DEAD — all ineligible to claim liveness.
        if status in (psutil.STATUS_ZOMBIE, psutil.STATUS_STOPPED, psutil.STATUS_DEAD):
            return False
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
    except OSError as exc:
        _logger.debug("heartbeat_authoritative_os_error marker=%s pid=%d error=%s", marker, pid, exc)
        return False


def start_heartbeat_writer(marker: str) -> threading.Thread:
    """Launch a daemon thread that writes heartbeats for `marker` forever.

    Returns the thread object so callers can inspect it; the thread is
    daemonized so it dies with the process.
    """
    def _loop() -> None:
        # Write immediately so sibling GUARD_CLEAN checks see us right away.
        write_heartbeat(marker)
        while True:
            time.sleep(HEARTBEAT_INTERVAL_SECONDS)
            try:
                write_heartbeat(marker)
            except (OSError, ValueError):
                # Never let a heartbeat failure kill the host process.
                pass

    thread = threading.Thread(
        target=_loop,
        name=f"mcp-heartbeat-{_sanitize_marker(marker)}",
        daemon=True,
    )
    thread.start()
    return thread


def clear_heartbeat(marker: str) -> None:
    """Remove the heartbeat file for `marker`. Best-effort; never raises."""
    try:
        p = _heartbeat_path(marker)
        if p.exists():
            p.unlink()
    except OSError as exc:
        _logger.debug("heartbeat_clear_failed marker=%s error=%s", marker, exc)


__all__ = [
    "HEARTBEAT_INTERVAL_SECONDS",
    "HEARTBEAT_STALE_AFTER_SECONDS",
    "write_heartbeat",
    "read_heartbeat",
    "is_heartbeat_fresh",
    "is_heartbeat_authoritative",
    "start_heartbeat_writer",
    "clear_heartbeat",
]
