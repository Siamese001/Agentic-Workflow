"""Optional telemetry adapter for anti-pattern registry.

This module provides lifecycle trace emission for anti-pattern registration
and reporting. It is NOT imported by antipattern_registry.py to maintain
purity of the registry module.

Import this module only if you need telemetry emission. The registry itself
remains side-effect free.
"""

from __future__ import annotations

from agentic_core.adg.runtime.antipattern_types import (
    AntipatternRecord,
    AntipatternRegistryReport,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_emits_metric_event,
    _emit_records_execution_trace,
)


class AntipatternTelemetryAdapter:
    """Optional telemetry adapter for anti-pattern registry operations.

    Wraps registry operations with lifecycle trace emission. Use this adapter
    only when you need observability; the registry itself is pure and
    side-effect free.

    Usage:
        adapter = AntipatternTelemetryAdapter()
        adapter.emit_registration(record)
        adapter.emit_report(report)
    """

    def emit_registration(self, record: AntipatternRecord) -> None:
        """Emit lifecycle trace for a single anti-pattern registration."""
        _emit_records_execution_trace(
            record.record_id,
            LayerSegment.L3_ORCHESTRATION,
            f"AntipatternRegistry.register:{record.category.value}",
        )
        _emit_captures_pattern(
            record.record_id,
            "p3lm",
            record.category.value,
        )

    def emit_report(self, report: AntipatternRegistryReport) -> None:
        """Emit lifecycle traces for aggregated report metrics."""
        if not isinstance(report, AntipatternRegistryReport):
            raise TypeError(f"Expected AntipatternRegistryReport, got {type(report).__name__}")
        _emit_emits_metric_event(
            "antipattern_registry",
            "p4obs",
            f"total_count:{report.total_count}",
        )
        _emit_emits_metric_event(
            "antipattern_registry",
            "p4obs",
            f"critical_count:{report.critical_count}",
        )
        _emit_emits_metric_event(
            "antipattern_registry",
            "p4obs",
            f"suppressed_count:{report.suppressed_count}",
        )
        _emit_emits_metric_event(
            "antipattern_registry",
            "p4obs",
            f"active_count:{report.active_count}",
        )
        _emit_emits_metric_event(
            "antipattern_registry",
            "p4obs",
            f"affected_files:{len(report.affected_files)}",
        )

    def emit_by_category_access(self, trace_id: str) -> None:
        """Emit lifecycle trace when by_category property is accessed."""
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "AntipatternRegistryReport.by_category",
        )
