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

from apps_lic.types import DraftPackage, ValidationResult

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

    def submit_draft(
        self, draft_package: DraftPackage, validation: ValidationResult
    ) -> dict[str, Any]:
        """
        Submit draft for execution tracking.

        Returns:
            Submission receipt with provenance
        """
        exec_request = ExecutionRequest(
            request_id=f"LIC-{hash(draft_package.draft) & 0xFFFFFF:06x}",
            priority="high" if not validation.passed else "normal",
            payload={
                "draft": draft_package.draft[:200],
                "validation_passed": validation.passed,
                "artifacts_count": len(draft_package.artifacts),
            },
        )

        receipt = {
            "receipt_id": exec_request.request_id,
            "status": "submitted",
            "app": exec_request.app_name,
            "provenance": {
                "validation_passed": validation.passed,
                "artifacts_count": len(draft_package.artifacts),
                "submitted_at": self._timestamp(),
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
