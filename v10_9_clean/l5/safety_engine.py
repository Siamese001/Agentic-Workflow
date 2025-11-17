# safety_engine.py
"""
L5 — Safety Engine (v10_9)

Top-level safety orchestrator:
    • Runs redaction
    • Aggregates basic safety checks
    • Invokes PolicyEngine for allow/block decisions

Produces:
    • SafetyReport
    • policy decision payload
"""

from __future__ import annotations

from typing import Dict, Any, Tuple

from .redaction import redact_payload
from .policy_engine import PolicyEngine
from .safety_contracts import SafetyReport
from ..shared.exceptions import SafetyViolationError


class SafetyEngine:
    """Main entrypoint for safety checks."""

    def __init__(self, policy_engine: PolicyEngine | None = None) -> None:
        self.policy_engine = policy_engine or PolicyEngine()

    def evaluate(self, payload: Dict[str, Any], metadata: Dict[str, Any]) -> Tuple[SafetyReport, Dict[str, Any]]:
        """
        Run end-to-end safety checks for the given payload.

        Returns:
            (safety_report, policy_decision)
        """

        # 1) Redaction & base safety analysis
        safety_report = redact_payload(payload)

        # 2) Policy evaluation
        policy_input = {
            "objective": metadata.get("objective", ""),
            "audience": metadata.get("audience", "general"),
            "sensitivity": metadata.get("sensitivity", "low"),
        }
        policy_decision = self.policy_engine.evaluate(policy_input, safety_report)

        # 3) If policy blocks, surface a violation
        if policy_decision.get("blocked"):
            raise SafetyViolationError(
                f"Safety policy blocked response: {policy_decision.get('reasons')}"
            )

        return safety_report, policy_decision
