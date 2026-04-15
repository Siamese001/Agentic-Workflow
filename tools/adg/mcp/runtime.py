"""Runtime bootstrap and lifecycle helpers for the ADG SQLite MCP server."""

from __future__ import annotations

import atexit
import datetime as dt
import hashlib
import logging
import os
import signal
import time
import uuid
from pathlib import Path
from typing import Any

from tools.adg.core.service import ADGService
from tools.adg.mcp.health import HealthDiagnostics

LOG_FILE = os.path.expanduser("~/adg_mcp_server.log")
LOGGER_NAME = "adg_mcp"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
LOG = logging.getLogger(LOGGER_NAME)


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

    def reopen_connections(self) -> dict[str, Any]:
        """Reopen ADG backend connections after an explicit close."""
        service = self.service
        service.reopen()
        return {
            "status": "ok",
            "data": {
                "reopened": True,
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
