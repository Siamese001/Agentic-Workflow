"""MCP Health Diagnostics — Exposed as adg_health tool."""

import logging
from typing import Any

from tools.adg.core.service import ADGService

logger = logging.getLogger(__name__)


class HealthDiagnostics:
    """Health check utilities for MCP server."""

    def __init__(self, service: ADGService):
        self._service = service

    def full_report(self) -> dict[str, Any]:
        """Complete health report."""
        health = self._service.health()
        status = self._service.get_status()

        return {
            "mode": health.mode,
            "sqlite": health.sqlite,
            "redis": health.redis,
            "cache_hit_capable": health.cache_hit_capable,
            "schema_version": health.schema_version,
            "adg_snapshot_id": health.adg_snapshot_id,
            "adg": status.data if status.status == "ok" else None,
        }

    def quick_check(self) -> dict[str, str]:
        """Quick binary health check."""
        health = self._service.health()

        if health.sqlite != "healthy":
            return {"status": "critical", "reason": "SQLite unavailable"}

        if health.mode == "sqlite_only":
            return {"status": "degraded", "reason": "Redis unavailable, SQLite only"}

        return {"status": "healthy"}
