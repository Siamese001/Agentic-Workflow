"""HOP7 gate_decision — decide whether to accept or halt the run.

Reads ``context["validation_report"]`` and emits ``passed`` + ``gate_reason``
into the context. The shared ``HopPipelineExecutor`` halts the run with
``StageStatus.GATED`` when ``passed`` is falsy (this spec declares
``gate=True``).
"""

from __future__ import annotations

from typing import Any


class GateDecisionEngine:
    """Gate on the validation report."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        report = context.get("validation_report") or {}
        passed = bool(report.get("passed", False))
        issues = list(report.get("issues") or [])

        if passed:
            reason = "validation_passed"
        elif issues:
            reason = f"validation_failed: {'; '.join(issues[:3])}"
        else:
            reason = "validation_missing"

        return {
            "passed": passed,
            "gate_reason": reason,
        }
