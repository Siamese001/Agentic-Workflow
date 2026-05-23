"""Terminal U0 rejection for apps_rg — sealed RejectedRequestNotice (REQ-U0-REJECTION-TERMINAL-001)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.validated_request import RejectedRequestNotice
from agentic_core.L0_routing.intake.verdicts import SourceClass


@dataclass(frozen=True, slots=True)
class AppsRgU0RejectedError(Exception):
    """Raised when apps_rg U0 validation fails; carries a terminal rejection notice."""

    notice: RejectedRequestNotice
    message: str = ""

    def __str__(self) -> str:
        return self.message or self.notice.rejection_reason.value


def build_u0_rejected_notice(
    *,
    request_id: str,
    trace_root: str,
    rejection_reason: IngressReasonCode,
    rejection_stage: str = "E4",
    machine_readable_detail: Mapping[str, Any] | None = None,
) -> RejectedRequestNotice:
    """Build a sealed RejectedRequestNotice for apps_rg U0 failures."""

    return RejectedRequestNotice(
        request_id=request_id or "unknown",
        trace_root=trace_root or request_id or "unknown",
        source_class=SourceClass.BATCH,
        received_at_iso=datetime.now(timezone.utc).isoformat(),
        rejection_stage=rejection_stage,
        rejection_reason=rejection_reason,
        reason_codes=(rejection_reason,),
        retry_after_seconds=None,
        machine_readable_detail=dict(machine_readable_detail or {}),
    )


__all__ = [
    "AppsRgU0RejectedError",
    "build_u0_rejected_notice",
]
