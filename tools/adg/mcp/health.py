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
        try:
            proj = self._service.get_projection_status()
            graph_projection = {
                "available": proj.data.get("available", False),
                "stale": proj.data.get("stale", False),
                "projection_path": proj.data.get("projection_path"),
            }
        except Exception:  # guardian: allow-broad-exception -- projection table absent on older snapshots; health report must never crash
            graph_projection = {"available": False, "stale": False, "projection_path": None}

        return {
            "mode": health.mode,
            "sqlite": health.sqlite,
            "redis": health.redis,
            "cache_hit_capable": health.cache_hit_capable,
            "schema_version": health.schema_version,
            "adg_snapshot_id": health.adg_snapshot_id,
            "adg": status.data if status.status == "ok" else None,
            "graph_projection": graph_projection,
        }

    def quick_check(self) -> dict[str, str]:
        """Quick binary health check."""
        health = self._service.health()

        if health.sqlite != "healthy":
            return {"status": "critical", "reason": "SQLite unavailable"}

        if health.mode == "sqlite_only":
            return {"status": "degraded", "reason": "Redis unavailable, SQLite only"}

        return {"status": "healthy"}
