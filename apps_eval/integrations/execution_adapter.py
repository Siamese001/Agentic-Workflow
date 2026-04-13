"""
Execution Adapter — Handoff to execution runtime.

SVP Standards:
- Explicit request contracts
- No silent failures
- Full provenance capture

EVAL-PIPELINE SCOPE: NON_CANONICAL_EVAL_LAB
This module is intentionally outside the canonical runtime evaluation pipeline.
ExecutionAdapter.submit() is an eval-lab internal execution tracker;
it does not invoke ExitControlGate, build shadow packets, or perform UWG handoff.
Do not add canonical pipeline wiring here.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from apps_eval.types import EvalRequest, EvalResult

# L1 retrieval wiring (Turn 2, Wave 6): Import creates ADG edge to L1_cognition

# L3 retrieval wiring (Turn 2, Wave 17): Import creates ADG edge to L3_orchestration

# L4 retrieval wiring (Turn 3, Wave 22): Import creates ADG edge to L4_state

_log = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Request for execution handoff."""

    app_name: str = "apps_eval"
    request_id: str = ""
    intent_type: str = "evaluation_run"
    priority: str = "normal"
    sla_deadline: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


class ExecutionAdapter:
    """Adapter for execution runtime handoff."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._execution_log: list[dict] = []

    def submit(self, request: EvalRequest, result: EvalResult) -> dict[str, Any]:
        """
        Submit evaluation result for execution tracking.

        Returns:
            Submission receipt with provenance
        """
        exec_request = ExecutionRequest(
            request_id=request.trace_id,
            priority="high" if not result.passed_gate else "normal",
            payload={
                "eval_request": request.dict(),
                "eval_result": result.dict(),
                "gate_passed": result.passed_gate,
            },
        )

        receipt = {
            "receipt_id": f"EXEC-{request.trace_id}",
            "status": "submitted",
            "app": exec_request.app_name,
            "provenance": {
                "trace_id": request.trace_id,
                "submitted_at": self._timestamp(),
                "gate_passed": result.passed_gate,
            },
        }

        self._execution_log.append(receipt)
        _log.info(f"Execution submitted: {receipt['receipt_id']}")

        return receipt

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"

    def get_execution_log(self) -> list[dict]:
        """Get execution submission log."""
        return self._execution_log.copy()
