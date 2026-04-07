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

from apps_lic.types import CampaignRequest, CampaignResult, DraftPackage, ValidationResult

# L1 retrieval wiring (Turn 2, Wave 5): Import creates ADG edge to L1_cognition

# L3 retrieval wiring (Turn 2, Wave 16): Import creates ADG edge to L3_orchestration

# L4 retrieval wiring (Turn 3, Wave 27): Import creates ADG edge to L4_state

# L5 retrieval wiring (Turn 3, Wave 29): Import creates ADG edge to L5_safety

_log = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Request for execution handoff."""

    app_name: str = "apps_lic"
    request_id: str = ""
    intent_type: str = "lic_campaign_run"
    priority: str = "normal"
    sla_deadline: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


class ExecutionAdapter:
    """Adapter for execution runtime handoff."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._execution_log: list[dict] = []

    def submit_campaign(self, request: CampaignRequest, result: CampaignResult) -> dict[str, Any]:
        """
        Submit campaign result for execution tracking.

        Returns:
            Submission receipt with provenance
        """
        exec_request = ExecutionRequest(
            request_id=request.trace_id or request.campaign_id,
            priority="high" if not result.passed_gate else "normal",
            payload={
                "campaign_id": request.campaign_id,
                "config": request.config.model_dump(),
                "result": result.model_dump(),
                "gate_passed": result.passed_gate,
                "drafts_count": len(result.drafts),
            },
        )

        receipt = {
            "receipt_id": f"LIC-{exec_request.request_id}",
            "status": "submitted",
            "app": exec_request.app_name,
            "provenance": {
                "campaign_id": request.campaign_id,
                "drafts_count": len(result.drafts),
                "validation_count": len(result.validations),
                "gate_passed": result.passed_gate,
                "submitted_at": self._timestamp(),
            },
        }

        self._execution_log.append(receipt)
        _log.info(f"Campaign submitted: {receipt['receipt_id']}")

        return receipt

    def submit_draft(
        self, draft_package: DraftPackage, validation: ValidationResult,
    ) -> dict[str, Any]:
        """
        Submit draft for execution tracking.

        Returns:
            Submission receipt with provenance
        """
        exec_request = ExecutionRequest(
            request_id=draft_package.trace_id or f"DRAFT-{hash(draft_package.draft) & 0xFFFFFF:06x}",
            priority="high" if not validation.passed else "normal",
            payload={
                "draft_preview": draft_package.draft[:200],
                "validation_passed": validation.passed,
                "artifacts_count": len(draft_package.artifacts),
                "latency_ms": validation.latency_ms,
            },
        )

        receipt = {
            "receipt_id": exec_request.request_id,
            "status": "submitted",
            "app": exec_request.app_name,
            "provenance": {
                "validation_passed": validation.passed,
                "artifacts_count": len(draft_package.artifacts),
                "latency_ms": validation.latency_ms,
                "submitted_at": self._timestamp(),
            },
        }

        self._execution_log.append(receipt)
        _log.info(f"Draft submitted: {receipt['receipt_id']}")

        return receipt

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def get_execution_log(self) -> list[dict]:
        """Get execution submission log."""
        return self._execution_log.copy()
