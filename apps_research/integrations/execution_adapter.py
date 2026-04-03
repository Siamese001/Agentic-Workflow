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

from apps_research.types import ResearchRequest, ResearchResult

# L1 retrieval wiring (Turn 2, Wave 8): Import creates ADG edge to L1_cognition

# L3 retrieval wiring (Turn 2, Wave 19): Import creates ADG edge to L3_orchestration

# L4 retrieval wiring (Turn 3, Wave 24): Import creates ADG edge to L4_state

# L5 retrieval wiring (Turn 3, Wave 31): Import creates ADG edge to L5_safety

_log = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Request for execution handoff."""

    app_name: str = "apps_research"
    request_id: str = ""
    intent_type: str = "research_run"
    priority: str = "normal"
    sla_deadline: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


class ExecutionAdapter:
    """Adapter for execution runtime handoff."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._execution_log: list[dict] = []

    def submit(self, request: ResearchRequest, result: ResearchResult) -> dict[str, Any]:
        """
        Submit research result for execution tracking.

        Returns:
            Submission receipt with provenance
        """
        exec_request = ExecutionRequest(
            request_id=request.trace_id or "research-unknown",
            priority="high" if not result.passed_gate else "normal",
            payload={
                "research_request": request.model_dump(),
                "research_result": result.model_dump(),
                "gate_passed": result.passed_gate,
                "sections_count": len(result.sections),
                "sources_count": len(result.source_register),
            },
        )

        receipt = {
            "receipt_id": f"RES-{exec_request.request_id}",
            "status": "submitted",
            "app": exec_request.app_name,
            "provenance": {
                "topic": result.topic,
                "mode": result.mode,
                "sections_count": len(result.sections),
                "sources_count": len(result.source_register),
                "gate_passed": result.passed_gate,
                "submitted_at": self._timestamp(),
            },
        }

        self._execution_log.append(receipt)
        _log.info(f"Research submitted: {receipt['receipt_id']}")

        return receipt

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def get_execution_log(self) -> list[dict]:
        """Get execution submission log."""
        return self._execution_log.copy()
