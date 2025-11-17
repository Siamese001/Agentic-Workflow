# arbitration_engine.py
"""
L5 — Arbitration Engine (v10_9)

Takes:
    • safety report
    • policy decision
    • optional QA signals

Emits:
    • ArbitrationDecision (accept / retry / replan / halt / fail)
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from .safety_contracts import ArbitrationDecision, SafetyReport
from ..shared.exceptions import ArbitrationError


class ArbitrationEngine:
    """
    Decides how the system should proceed after safety/QA:
        - accept: proceed to user
        - retry:  re-run the last execution
        - replan: send back to L1/L3 for new plan
        - halt:   stop gracefully, no output
        - fail:   hard failure
    """

    def decide(
        self,
        safety: SafetyReport,
        policy_decision: Dict[str, Any],
        qa_signal: Optional[Dict[str, Any]] = None,
    ) -> ArbitrationDecision:
        """
        Simple deterministic decision policy.

        qa_signal (optional example keys):
            - confidence: float in [0,1]
            - issues: list of strings
        """

        # Default outcome
        decision = "accept"
        reasons = []

        blocked = policy_decision.get("blocked", False)
        qa_conf = float(qa_signal.get("confidence", 1.0)) if qa_signal else 1.0
        qa_issues = qa_signal.get("issues", []) if qa_signal else []

        if blocked:
            decision = "fail"
            reasons.append("Policy engine blocked response.")

        elif not safety.is_safe:
            decision = "replan"
            reasons.append("Safety report indicates unsafe content.")

        elif qa_conf < 0.5:
            decision = "retry"
            reasons.append("QA confidence too low.")

        if qa_issues:
            reasons.extend(qa_issues)

        if decision not in {"accept", "retry", "replan", "halt", "fail"}:
            raise ArbitrationError(f"Invalid arbitration decision: {decision!r}")

        return ArbitrationDecision(
            decision=decision,
            rationale="; ".join(reasons) if reasons else "No issues detected.",
            metadata={
                "blocked": blocked,
                "qa_confidence": qa_conf,
                "qa_issues": qa_issues,
            },
        )
