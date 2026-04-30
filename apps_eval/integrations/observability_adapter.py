"""
Observability Adapter — Integration with observability plane.

SVP Standards:
- Explicit metric emission
- Full trace context
- No silent failures
"""

from __future__ import annotations

import logging
from typing import Any

from apps_eval.types import EvalRequest, EvalResult, SuiteResult

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Adapter for observability integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._metrics: list[dict] = []

    def emit_eval_start(self, request: EvalRequest) -> dict[str, Any]:
        """Emit evaluation start event."""
        event = {
            "event_type": "eval_start",
            "trace_id": request.trace_id,
            "suites": len(request.suite_ids),
            "dry_run": request.dry_run,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_eval_complete(self, result: EvalResult) -> dict[str, Any]:
        """Emit evaluation completion event."""
        event = {
            "event_type": "eval_complete",
            "trace_id": result.trace_id,
            "status": result.status,
            "overall_score": result.overall_score,
            "gate_passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_suite_metric(self, suite: SuiteResult) -> dict[str, Any]:
        """Emit suite-level metric."""
        metric = {
            "event_type": "suite_complete",
            "suite_id": suite.suite_id,
            "pass_rate": suite.pass_rate,
            "latency_ms": suite.mean_latency_ms,
            "scenarios": len(suite.scenarios),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(metric)
        return metric

    def get_metrics(self) -> list[dict]:
        """Get all emitted metrics."""
        return self._metrics.copy()

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_eval.integrations.observability_adapter', "module_loaded")
