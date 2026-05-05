"""
Observability Adapter — apps_repo_brief.

Dual-span OTEL emission: emits spans under BOTH the legacy
apps_exec.* namespace (for continuity during W1-W4 transition) and
the canonical apps_repo_brief.* namespace.

During W5 the apps_exec.* spans are retired.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P2.6
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

    Emits spans under apps_repo_brief.* (canonical) and apps_exec.*
    (legacy compatibility) simultaneously during the W1-W4 transition.
    The legacy namespace is removed in W5.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._metrics: list[dict[str, Any]] = []

    def emit_brief_start(self, request: Any) -> dict[str, Any]:
        """Emit brief generation start — dual span."""
        base = {
            "trace_id": getattr(request, "trace_id", None),
            "audience": getattr(request, "audience", None),
            "emphasis_areas": getattr(request, "emphasis_areas", []),
            "dry_run": getattr(request, "dry_run", False),
            "timestamp": _now_iso(),
        }
        # Canonical span
        canonical = {**base, "event_type": "apps_repo_brief.brief_start"}
        # Legacy span — retained through W4 for continuity with existing dashboards
        legacy = {**base, "event_type": "apps_exec.brief_start", "_legacy": True}
        self._metrics.extend([canonical, legacy])
        _log.debug("emit_brief_start: canonical + legacy spans emitted")
        return canonical

    def emit_brief_complete(self, result: Any) -> dict[str, Any]:
        """Emit brief generation complete — dual span."""
        base = {
            "trace_id": getattr(result, "trace_id", None),
            "audience": getattr(result, "audience", None),
            "status": getattr(result, "status", None),
            "quality_score": getattr(result, "quality_score", None),
            "gate_passed": getattr(result, "passed_gate", None),
            "timestamp": _now_iso(),
        }
        canonical = {**base, "event_type": "apps_repo_brief.brief_complete"}
        legacy = {**base, "event_type": "apps_exec.brief_complete", "_legacy": True}
        self._metrics.extend([canonical, legacy])
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
        """Return all emitted metrics (canonical + legacy)."""
        return self._metrics.copy()

    def get_canonical_metrics(self) -> list[dict[str, Any]]:
        """Return only canonical apps_repo_brief.* spans."""
        return [m for m in self._metrics if not m.get("_legacy")]


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit (matches apps_exec pattern).
# Dual span: apps_repo_brief (canonical) + apps_exec (legacy W1-W4).
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event(
    "p4",
    "apps_repo_brief.integrations.observability_adapter",
    "module_loaded",
)
_emit_records_telemetry_event(
    "p4",
    "apps_exec.integrations.observability_adapter",
    "module_loaded_legacy_alias",
)
