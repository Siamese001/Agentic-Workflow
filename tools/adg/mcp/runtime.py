"""Runtime bootstrap and lifecycle helpers for the ADG SQLite MCP server."""

from __future__ import annotations

import atexit
import datetime as dt
import hashlib
import logging
import os
import signal
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from tools.adg.core.service import ADGService
from tools.adg.mcp.health import HealthDiagnostics
from tools.mcp.mcp_bootstrap import mcp_process_identity

LOG_FILE = os.path.expanduser("~/adg_mcp_server.log")
LOGGER_NAME = "adg_mcp"


def _configure_adg_logger() -> logging.Logger:
    """Attach a FileHandler directly to the named logger.

    W1.1 F1 (plan ``adg-mcp-reopen-hardening``): ``logging.basicConfig``
    is a no-op when the root logger already has handlers, and FastMCP's
    stdio transport registers stderr handlers before our module imports.
    The silent-log regression (2026-04-22: log dead 13:39 → 20:33+
    despite active server PID 55784) traced to that override.

    This helper configures the ``adg_mcp`` logger explicitly:

    * Attach a single ``FileHandler`` with the canonical format.
    * Guard against duplicate handler registration on re-import (tests,
      hot-reload, subprocess relaunch).
    * Set ``propagate=False`` so our file output is not duplicated into
      FastMCP's stderr sinks.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers on module re-import.
    existing = {
        getattr(h, "baseFilename", None) for h in logger.handlers if isinstance(h, logging.FileHandler)
    }
    target = os.path.abspath(LOG_FILE)
    if target not in existing:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
        logger.addHandler(handler)
    # Keep log lines scoped to the file handler; FastMCP stderr sinks pick
    # up warnings via their own root config if they need to.
    logger.propagate = False
    return logger


LOG = _configure_adg_logger()


class ADGServerRuntime:
    """Owns process identity, singleton service lifecycle, and runtime ops."""

    def __init__(self) -> None:
        self.startup_time: float = time.time()
        self.startup_nonce: str = uuid.uuid4().hex[:12]
        self.stack_fingerprints, self.combined_fingerprint = self._compute_stack_fingerprints()
        self._service: ADGService | None = None
        self._health: HealthDiagnostics | None = None
        self._register_shutdown_handlers()

    def _compute_stack_fingerprints(self) -> tuple[dict[str, str], str]:
        """Return per-file md5[:10] fingerprints and a combined fingerprint."""
        repo_root = Path(__file__).resolve().parents[3]
        files = {
            "server.py": Path(__file__).resolve().with_name("server.py"),
            "runtime.py": Path(__file__).resolve(),
            "tool_handlers.py": Path(__file__).resolve().with_name("tool_handlers.py"),
            "validators.py": Path(__file__).resolve().with_name("validators.py"),
            "service.py": repo_root / "tools/adg/core/service.py",
            "sqlite_backend.py": repo_root / "tools/adg/core/sqlite_backend.py",
            "models.py": repo_root / "tools/adg/core/models.py",
        }
        per_file: dict[str, str] = {}
        combined = hashlib.md5()
        for label, path in files.items():
            try:
                content = path.read_bytes()
            except OSError:
                content = b""
            digest = hashlib.md5(content).hexdigest()[:10]
            per_file[label] = digest
            combined.update(content)
        return per_file, combined.hexdigest()[:10]

    @property
    def service(self) -> ADGService:
        """Return the singleton ADG service, creating it lazily on first use."""
        if self._service is None:
            LOG.info("Initializing ADGService...")
            self._service = ADGService()
            self._health = HealthDiagnostics(self._service)
            LOG.info("ADGService ready: %s", self._service.health().mode)
        return self._service

    @property
    def diagnostics(self) -> HealthDiagnostics:
        """Return cached health diagnostics bound to the current service instance."""
        if self._health is None:
            self._health = HealthDiagnostics(self.service)
        return self._health

    def safe_close_service(self, service: ADGService | None) -> None:
        """Best-effort close that never lets shutdown crash the process."""
        if service is None:
            return
        try:
            service.close()
        except (
            Exception
        ) as exc:  # guardian: allow-broad-exception -- shutdown paths must be best-effort and non-fatal
            LOG.exception("ADGService close failed during shutdown: %s", exc)

    def shutdown_service(self) -> None:
        """Gracefully shutdown ADGService and release all connections."""
        if self._service is None:
            return

        service = self._service
        self._service = None
        self._health = None
        LOG.info("Shutting down ADGService...")
        self.safe_close_service(service)
        LOG.info("ADGService shutdown complete")

    def close_connections(self) -> dict[str, Any]:
        """Close ADG backend connections to release SQLite file locks."""
        if self._service is None:
            return {
                "status": "ok",
                "data": {
                    "closed": False,
                    "message": "No active ADG service instance to close.",
                },
            }

        service = self._service
        self._service = None
        self._health = None
        self.safe_close_service(service)
        return {
            "status": "ok",
            "data": {
                "closed": True,
                "message": "ADG connections closed. SQLite file locks released.",
            },
        }

    def reopen_connections(self, timeout_s: float = 15.0) -> dict[str, Any]:
        """Reopen ADG backend connections after an explicit close.

        W2.2 (idempotency, F4) + W1.2 (bounded timeout, F2) remediation —
        plan ``adg-mcp-reopen-hardening``.

        Fast-path (F4 idempotency): when a live ``ADGService`` already points
        at the latest on-disk SQLite snapshot with an unchanged mtime, skip
        teardown/reconnect entirely and return ``noop=True``. The previous
        implementation forced 3+ SQLite opens plus a Redis ping on every call
        regardless of state change.

        Slow-path (F2 timeout): the actual ``service.reopen()`` call is
        executed on the CALLING thread with a watchdog daemon Thread enforcing
        an upper bound of ``timeout_s`` seconds (default 15). Under backend
        contention a bare ``reopen()`` could queue indefinitely and hang the
        MCP client; the watchdog surfaces a structured error instead of
        blocking forever. The earlier implementation wrapped reopen() in a
        ``concurrent.futures.ThreadPoolExecutor``, which pinned the new
        SQLite connection to an ephemeral worker thread and poisoned every
        subsequent query — see RCA below.
        """
        # F4 — idempotency: short-circuit if snapshot+mtime unchanged.
        if self._service is not None:
            sqlite_backend = getattr(self._service, "_sqlite", None)
            if sqlite_backend is not None:
                try:
                    from tools.adg.shared_modules.path_resolver import latest_sqlite

                    current_path = getattr(sqlite_backend, "_sqlite_path", None)
                    current_mtime = getattr(sqlite_backend, "_last_mtime", 0.0)
                    latest_path = latest_sqlite()
                    if (
                        latest_path is not None
                        and current_path is not None
                        and Path(current_path) == Path(latest_path)
                        and current_mtime == latest_path.stat().st_mtime
                    ):
                        LOG.info("reopen_connections noop: snapshot unchanged (%s)", current_path)
                        return {
                            "status": "ok",
                            "data": {
                                "reopened": True,
                                "noop": True,
                                "sqlite_path": str(current_path),
                                "message": "ADG connections unchanged; skipped reopen.",
                            },
                        }
                except (OSError, AttributeError) as exc:
                    # Idempotency check is best-effort; fall through to full reopen
                    # on any inspection error rather than block the caller.
                    LOG.debug("reopen idempotency check failed, proceeding: %s", exc)

        # F2 — bounded timeout via watchdog THREAD, not via ThreadPoolExecutor.
        #
        # RCA 2026-04-24 (plan mcp-destructive-gate-preflight-e9a14b W1 P3):
        # The previous implementation wrapped ``service.reopen()`` inside a
        # ThreadPoolExecutor(max_workers=1) to enforce ``timeout_s``. That
        # pinned the fresh sqlite3.Connection to an ephemeral worker thread
        # ("adg-reopen"). Every subsequent MCP tool call from the FastMCP
        # event loop then raised::
        #   sqlite3.ProgrammingError: SQLite objects created in a thread can
        #   only be used in that same thread.
        # ...and the server went dark until full MCP restart.
        #
        # Replacement: run ``service.reopen()`` on the CALLING thread (which
        # is the same thread that will then dispatch this tool's response),
        # and enforce the bound with a watchdog daemon thread that only
        # records whether reopen() completed in time. SQLite's own
        # ``busy_timeout`` (set to SQLITE_QUERY_TIMEOUT inside
        # ``sqlite_backend._connect``) already caps contention-driven hangs
        # at the pragma level, so the outer watchdog is belt-and-suspenders.
        #
        # The backend is additionally hardened with check_same_thread=False
        # and self-healing in ``SQLiteBackend._require_conn`` so that even
        # if a reopen() *does* end up on a different thread through some
        # future code path, queries will not fail.
        service = self.service
        done = threading.Event()
        reopen_error: list[BaseException] = []

        def _run_reopen() -> None:
            try:
                service.reopen()
            except BaseException as exc:  # guardian: allow-log-and-swallow -- watchdog boundary must capture and surface all exceptions to main thread via shared list
                reopen_error.append(exc)
            finally:
                done.set()

        worker = threading.Thread(
            target=_run_reopen,
            name="adg-reopen-watchdog",
            daemon=True,  # do not block interpreter shutdown if it hangs
        )
        worker.start()
        completed = done.wait(timeout=timeout_s)
        if not completed:
            LOG.error(
                "reopen_connections exceeded %.1fs; returning error. "
                "Worker thread left running daemonised — it will be reaped on "
                "process exit. Underlying reopen may still complete in background.",
                timeout_s,
            )
            return {
                "status": "error",
                "data": {
                    "reopened": False,
                    "reason": "timeout",
                    "timeout_s": timeout_s,
                    "detail": (
                        f"service.reopen() did not return within {timeout_s:.1f}s; "
                        "backend contention likely — retry after snapshot stabilises."
                    ),
                },
            }
        if reopen_error:
            reopen_exc = reopen_error[0]
            LOG.error("reopen_connections failed: %s", reopen_exc)
            return {
                "status": "error",
                "data": {
                    "reopened": False,
                    "reason": "reopen_exception",
                    "detail": f"{type(reopen_exc).__name__}: {reopen_exc}",
                },
            }
        return {
            "status": "ok",
            "data": {
                "reopened": True,
                "noop": False,
                "message": "ADG connections reopened.",
            },
        }

    def sqlite_health_meta(self) -> dict[str, Any]:
        """Safely fetch SQLite backend health metadata from service internals."""
        sqlite_backend = getattr(self.service, "_sqlite", None)
        if sqlite_backend is None or not hasattr(sqlite_backend, "health"):
            return {}

        try:
            _, meta = sqlite_backend.health()
        except Exception as exc:  # guardian: allow-broad-exception -- runtime info and reload should degrade gracefully if internals shift
            LOG.warning("SQLite health metadata unavailable: %s", exc)
            return {}

        return meta if isinstance(meta, dict) else {}

    def redis_available(self) -> bool:
        """Safely determine whether the optional Redis cache backend is live."""
        redis_backend = getattr(self.service, "_redis", None)
        return bool(getattr(redis_backend, "_available", False))

    def runtime_info(self) -> dict[str, Any]:
        """Return process-level runtime identity for verifying restarts."""
        health = self.service.health()
        sqlite_meta = self.sqlite_health_meta()
        return {
            "status": "ok",
            "data": {
                "pid": os.getpid(),
                "process": mcp_process_identity("adg_sqlite"),
                "startup_time": dt.datetime.fromtimestamp(self.startup_time).isoformat(),
                "startup_nonce": self.startup_nonce,
                "stack_fingerprints": self.stack_fingerprints,
                "combined_fingerprint": self.combined_fingerprint,
                "sqlite_path": sqlite_meta.get("path"),
                "snapshot_id": health.adg_snapshot_id,
                "redis_enabled": health.cache_hit_capable,
            },
        }

    def reload_latest_snapshot(self) -> dict[str, Any]:
        """Reload ADG SQLite snapshot if a newer file exists on disk."""
        service = self.service
        sqlite_meta = self.sqlite_health_meta()

        is_stale = sqlite_meta.get("is_stale", False)
        current_path = sqlite_meta.get("path")
        latest_path = sqlite_meta.get("latest_path")

        if not is_stale:
            return {
                "status": "ok",
                "data": {
                    "reloaded": False,
                    "message": "Already using latest snapshot.",
                    "current_path": current_path,
                    "redis_cleared": False,
                },
            }

        old_snapshot_id = getattr(service, "_adg_snapshot_id", None)

        LOG.info("Reloading ADG from %s to %s", current_path, latest_path)
        service.reopen()

        new_meta = self.sqlite_health_meta()
        new_snapshot_id = getattr(service, "_adg_snapshot_id", None)

        redis_cleared = False
        if old_snapshot_id != new_snapshot_id and self.redis_available():
            try:
                service._redis.clear_snapshot(old_snapshot_id)
                redis_cleared = True
                LOG.info("Cleared Redis keys for old snapshot %s", old_snapshot_id)
            except Exception as exc:  # guardian: allow-broad-exception -- Redis clear is best-effort; reload succeeds regardless
                LOG.warning("Redis clear_snapshot failed for %s: %s", old_snapshot_id, exc)

        return {
            "status": "ok",
            "data": {
                "reloaded": True,
                "message": "Reloaded to latest snapshot.",
                "old_path": current_path,
                "new_path": new_meta.get("path"),
                "old_snapshot_id": old_snapshot_id,
                "new_snapshot_id": new_snapshot_id,
                "redis_cleared": redis_cleared,
                "redis_cache_state": "cleared_old_snapshot" if redis_cleared else "cold",
            },
        }

    def _handle_shutdown_signal(self, sig: int, frame: object) -> None:
        """Terminate gracefully when the host sends a shutdown signal."""
        del frame
        LOG.info("Received shutdown signal %s", sig)
        self.shutdown_service()

    def _register_shutdown_handlers(self) -> None:
        """Register signal handlers when the runtime supports it."""
        atexit.register(self.shutdown_service)
        for signame in ("SIGTERM", "SIGINT"):
            signum = getattr(signal, signame, None)
            if signum is None:
                continue
            try:
                signal.signal(signum, self._handle_shutdown_signal)
            except (OSError, RuntimeError, ValueError) as exc:
                LOG.warning("Signal handler registration skipped for %s: %s", signame, exc)


runtime = ADGServerRuntime()
