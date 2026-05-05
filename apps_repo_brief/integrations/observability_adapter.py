"""
Observability Adapter — apps_repo_brief.

Emits spans under the canonical apps_repo_brief.* namespace only.

W5 P5.7: Legacy apps_exec.* dual-span emission retired. The W1-W4
transition window is complete; apps_exec package archived.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P5.7
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

_log = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RepoBriefObservabilityAdapter:
    """
    OTEL observability adapter for apps_repo_brief.

    Emits spans under apps_repo_brief.* (canonical namespace only).
    W5 P5.7: Legacy apps_exec.* dual-span retired.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._metrics: list[dict[str, Any]] = []

    def emit_brief_start(self, request: Any) -> dict[str, Any]:
        """Emit brief generation start."""
        canonical = {
            "event_type": "apps_repo_brief.brief_start",
            "trace_id": getattr(request, "trace_id", None),
            "audience": getattr(request, "audience", None),
            "emphasis_areas": getattr(request, "emphasis_areas", []),
            "dry_run": getattr(request, "dry_run", False),
            "timestamp": _now_iso(),
        }
        self._metrics.append(canonical)
        _log.debug("emit_brief_start: canonical span emitted")
        return canonical

    def emit_brief_complete(self, result: Any) -> dict[str, Any]:
        """Emit brief generation complete."""
        canonical = {
            "event_type": "apps_repo_brief.brief_complete",
            "trace_id": getattr(result, "trace_id", None),
            "audience": getattr(result, "audience", None),
            "status": getattr(result, "status", None),
            "quality_score": getattr(result, "quality_score", None),
            "gate_passed": getattr(result, "passed_gate", None),
            "timestamp": _now_iso(),
        }
        self._metrics.append(canonical)
        return canonical

    def emit_evidence_gate(
        self,
        evidence_status: str,
        source_count: int,
        citation_anchor_count: int,
        section_coverage_pct: float,
    ) -> dict[str, Any]:
        """Emit C0 evidence gate result — canonical only (no legacy equivalent)."""
        event = {
            "event_type": "apps_repo_brief.evidence_gate",
            "evidence_status": evidence_status,
            "source_count": source_count,
            "citation_anchor_count": citation_anchor_count,
            "section_coverage_pct": section_coverage_pct,
            "timestamp": _now_iso(),
        }
        self._metrics.append(event)
        return event

    def get_metrics(self) -> list[dict[str, Any]]:
        """Return all emitted metrics (canonical apps_repo_brief.* only)."""
        return self._metrics.copy()

    def get_canonical_metrics(self) -> list[dict[str, Any]]:
        """Return canonical apps_repo_brief.* spans (alias for get_metrics — no legacy spans exist)."""
        return self._metrics.copy()


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit (canonical only; legacy retired W5 P5.7).
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event(
    "p4",
    "apps_repo_brief.integrations.observability_adapter",
    "module_loaded",
)
