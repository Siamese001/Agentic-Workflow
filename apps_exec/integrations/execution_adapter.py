"""
Execution Adapter — Handoff to execution runtime.

SVP Standards:
- Explicit request contracts
- No silent failures
- Full provenance capture
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from apps_exec.types import ExecBriefRequest, ExecBriefResult

# L1 retrieval wiring (Turn 2, Wave 7): Import creates ADG edge to L1_cognition

# L3 retrieval wiring (Turn 2, Wave 18): Import creates ADG edge to L3_orchestration

# L4 retrieval wiring (Turn 3, Wave 23): Import creates ADG edge to L4_state

# L5 retrieval wiring (Turn 3, Wave 30): Import creates ADG edge to L5_safety

_log = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Request for execution handoff."""

    app_name: str = "apps_exec"
    request_id: str = ""
    intent_type: str = "exec_brief_run"
    priority: str = "normal"
    sla_deadline: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


class ExecutionAdapter:
    """Adapter for execution runtime handoff."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._execution_log: list[dict] = []

    def submit(self, request: ExecBriefRequest, result: ExecBriefResult) -> dict[str, Any]:
        """
        Submit brief result for execution tracking.

        Returns:
            Submission receipt with provenance
        """
        exec_request = ExecutionRequest(
            request_id=request.trace_id or "exec-unknown",
            priority="high" if not result.passed_gate else "normal",
            payload={
                "exec_request": request.model_dump(),
                "exec_result": result.model_dump(),
                "gate_passed": result.passed_gate,
                "sections_count": len(result.sections),
                "capabilities_count": len(result.capabilities_extracted),
            },
        )

        receipt = {
            "receipt_id": f"EXEC-{exec_request.request_id}",
            "status": "submitted",
            "app": exec_request.app_name,
            "provenance": {
                "audience": result.audience,
                "tone": result.tone,
                "sections_count": len(result.sections),
                "capabilities_count": len(result.capabilities_extracted),
                "gate_passed": result.passed_gate,
                "submitted_at": self._timestamp(),
            },
        }

        self._execution_log.append(receipt)
        _log.info(f"Brief submitted: {receipt['receipt_id']}")

        return receipt

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    def get_execution_log(self) -> list[dict]:
        """Get execution submission log."""
        return self._execution_log.copy()


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_exec.integrations.execution_adapter', "module_loaded")
