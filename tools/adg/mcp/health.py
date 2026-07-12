"""MCP Health Diagnostics — Exposed as adg_health tool."""

import logging
from typing import Any

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

    def full_report(self) -> dict[str, Any]:
        """Complete certification-aware health report."""
        health = self._service.health()
        status = self._service.get_status()
        projection = self._safe_projection_status()
        overall = health.overall_status
        reasons = list(health.reasons)
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
                "certified": health.certified,
                "selection": health.snapshot_selection,
                "certification_status": health.certification_status,
                "artifact_status": health.artifact_status,
                "pointer_path": health.pointer_path,
                "digest_verified": health.digest_verified,
            },
            "materialization": {
                "status": health.materialization_status,
                "counts": health.materialization_counts,
            },
            "adg": status.data,
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
