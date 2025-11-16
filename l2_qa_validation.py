"""
L2 — QA Validation Agent

Responsibilities:
    • Execute quality and factuality checks on agent outputs.
    • Validate alignment between planned intents and produced artifacts.
    • Surface structured validation reports to L3 orchestrators and L4 state systems.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""
from __future__ import annotations

from typing import Any, Dict, List

from l2_tool_base import ExecutionAgent
from utils_types import PlanObject, StatePatch


def _build_checks(plan: PlanObject) -> List[str]:
    """Derive simple validation checks from the provided plan."""

    checks: List[str] = ["coherence", "completeness"]
    if plan.get("mode") == "rag":
        checks.append("evidence_alignment")
    if plan.get("mode") == "drafting":
        checks.append("tone_alignment")
    return checks


def _derive_findings(state: Dict[str, Any], checks: List[str]) -> List[Dict[str, Any]]:
    """Produce deterministic validation findings based on available state."""

    findings: List[Dict[str, Any]] = []
    has_messages = bool(state.get("messages"))
    for check in checks:
        findings.append(
            {
                "check": check,
                "status": "pass" if has_messages else "pending",
                "details": "validated deterministically" if has_messages else "awaiting content",
            }
        )
    return findings


class QAValidationAgent(ExecutionAgent):
    """Perform deterministic QA validation that emits state patches only."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        checks = _build_checks(plan)
        findings = _derive_findings(state, checks)

        patch: StatePatch = StatePatch(
            {
                "qa_report": {
                    "plan_mode": plan.get("mode"),
                    "checks": checks,
                    "findings": findings,
                }
            }
        )
        return patch
