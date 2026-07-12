"""MCP Health Diagnostics — Exposed as adg_health tool."""

import logging
from pathlib import Path
from typing import Any

from tools.adg.core.repo_health import read_repo_health
from tools.adg.core.service import ADGService

logger = logging.getLogger(__name__)


class HealthDiagnostics:
    """Health check utilities for MCP server."""

    def __init__(self, service: ADGService):
        self._service = service

    def _safe_projection_status(self) -> dict[str, Any]:
        """Return typed projection health without unavailable-to-empty fallback."""
        try:
            response = self._service.get_projection_status()
            if response.status != "ok" or not isinstance(
                response.data,
                dict,
            ):
                return {
                    "status": "UNKNOWN",
                    "available": False,
                    "stale": None,
                    "projection_path": None,
                    "reason": "projection status response malformed",
                }
            data = response.data
            available = data.get("available") is True
            stale = data.get("stale")
            if not available:
                verdict = "FAIL"
                reason = "required graph projection unavailable"
            elif stale is True:
                verdict = "FAIL"
                reason = "required graph projection is stale"
            elif stale is False:
                verdict = "PASS"
                reason = None
            else:
                verdict = "UNKNOWN"
                reason = "projection freshness was not evaluated"
            return {
                "status": verdict,
                "available": available,
                "stale": stale,
                "projection_path": data.get("projection_path"),
                "reason": reason,
            }
        except Exception as exc:  # guardian: allow-broad-exception -- health must report UNKNOWN instead of crashing
            logger.warning(
                "Projection status unavailable during health report: %s",
                exc,
            )
            return {
                "status": "UNKNOWN",
                "available": False,
                "stale": None,
                "projection_path": None,
                "reason": f"{type(exc).__name__}: {exc}",
            }

    def _safe_repo_health(self) -> dict[str, Any]:
        """Return Phase G repository health without breaking MCP startup."""
        try:
            backend = getattr(self._service, "_sqlite", None)
            if backend is None or not hasattr(backend, "health"):
                return {
                    "available": False,
                    "reason": "sqlite_backend_unavailable",
                }
            _status, metadata = backend.health()
            sqlite_path = metadata.get("path") if isinstance(metadata, dict) else None
            if not sqlite_path:
                return {
                    "available": False,
                    "reason": "sqlite_path_unavailable",
                }
            return read_repo_health(Path(str(sqlite_path)))
        except Exception as exc:  # guardian: allow-broad-exception -- additive repo-health probe
            logger.warning(
                "Repo-health status unavailable during health report: %s",
                exc,
            )
            return {
                "available": False,
                "reason": "repo_health_query_failed",
                "message": str(exc),
            }

    def full_report(self) -> dict[str, Any]:
        """Complete certification-aware health report."""
        health = self._service.health()
        status = self._service.get_status()
        projection = self._safe_projection_status()
        overall = getattr(health, "overall_status", None) or (
            "healthy" if getattr(health, "sqlite", None) == "healthy" else "critical"
        )
        reasons = list(getattr(health, "reasons", ()) or ())
        if projection["status"] != "PASS":
            overall = "critical"
            reasons.append(
                str(
                    projection.get("reason")
                    or "graph projection did not pass"
                )
            )

        return {
            "status": overall,
            "reasons": list(dict.fromkeys(reasons)),
            "mode": health.mode,
            "sqlite": health.sqlite,
            "redis": health.redis,
            "cache_hit_capable": health.cache_hit_capable,
            "schema_version": health.schema_version,
            "adg_snapshot_id": health.adg_snapshot_id,
            "views_materialized_at": health.views_materialized_at,
            "certification": {
                "certified": getattr(health, "certified", False),
                "selection": getattr(health, "snapshot_selection", None),
                "certification_status": getattr(
                    health,
                    "certification_status",
                    None,
                ),
                "artifact_status": getattr(health, "artifact_status", None),
                "pointer_path": getattr(health, "pointer_path", None),
                "digest_verified": getattr(health, "digest_verified", False),
            },
            "materialization": {
                "status": getattr(health, "materialization_status", None),
                "counts": getattr(health, "materialization_counts", {}),
            },
            "adg": status.data,
            "repo_health": self._safe_repo_health(),
            "graph_projection": projection,
        }

    def quick_check(self) -> dict[str, str]:
        """Quick health verdict that cannot pass on unknown prerequisites."""
        report = self.full_report()
        if report["status"] != "healthy":
            status = (
                "critical"
                if report["status"] in {"critical", "unknown"}
                else "degraded"
            )
            return {
                "status": status,
                "reason": "; ".join(report["reasons"])
                or "ADG health is not healthy",
            }
        return {"status": "healthy"}
