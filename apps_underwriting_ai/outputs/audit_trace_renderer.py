"""
Audit Trace Renderer - Renders audit trace as formatted output.
"""

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)
import json
from typing import Any, Dict

from ..types import AuditTrace


class AuditTraceRenderer:
    """Renders AuditTrace as formatted JSON."""

    @traces_execute(layer="L1_COGNITION")
    def render(self, trace: AuditTrace) -> str:
        """Render audit trace as formatted JSON string."""
        data = {
            "request_id": trace.request_id,
            "trace_id": trace.trace_id,
            "policy_hash": trace.policy_hash,
            "derived_features": trace.derived_features.dict() if trace.derived_features else {},
            "evidence_count": len(trace.evidence_refs),
            "validators_executed": trace.validators_run,
            "routing_outcome": trace.routing_outcome,
            "decision_proposal": trace.decision_proposal,
            "human_review_triggered": trace.human_review_triggered,
            "determinism_digest": trace.determinism_digest,
        }

        return json.dumps(data, indent=2, default=str)

    def render_minimal(self, trace: AuditTrace) -> Dict[str, Any]:
        """Render minimal audit trace for embedding."""
        return {
            "request_id": trace.request_id,
            "trace_id": trace.trace_id,
            "decision": trace.decision_proposal,
            "human_review": trace.human_review_triggered,
        }


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.outputs.audit_trace_renderer', "module_loaded")
