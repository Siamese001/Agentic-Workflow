"""apps_architect L6 Observability layer.

L6 runs AFTER Exit v6. It may read run-state for metrics/telemetry but
must NEVER mutate the current-run record, re-emit Exit, write L4, or call
provider synthesis directly.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W5.P1.
"""

from apps_architect.L6_observability.span_emitters import (
    ArchitectSpanEmitter,
    emit_scan_span,
    emit_delta_span,
    emit_rules_span,
    emit_sync_span,
)

__all__ = [
    "ArchitectSpanEmitter",
    "emit_scan_span",
    "emit_delta_span",
    "emit_rules_span",
    "emit_sync_span",
]
