# FILE: 10_10/l5.py
"""
L5 Safety Gateway — Final Gating Layer (v10_10 · Phase 1)
=========================================================

Responsibilities:
    • Interpret SafetyResult produced by L2 cognitive safety agent.
    • Apply a deterministic SafetyPolicy (G19–G23).
    • Emit structured PolicyDecisionEvent records for auditability.
    • Produce a single boolean gate: safety_passed = True/False.

Non-Responsibilities:
    • No LLM calls (handled at L2).
    • No execution / tools (L2).
    • No DAG orchestration (L3).
    • No state mutation (L4).

This module is the canonical L5 implementation for v10_10 Phase 1:
    • Uses Phase 0 types: SafetyResult, SafetyFinding, PolicyDecisionEvent.
    • Uses observability.emit_policy_decision for structured safety audit logs.
    • Fails closed on errors (conservative stance).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from models import SafetyResult, SafetyFinding, PolicyDecisionEvent
from observability import emit_policy_decision, record_exception


# =============================================================================
# Safety Policy Model
# =============================================================================


@dataclass
class SafetyPolicy:
    """
    Deterministic safety policy for final gating.

    Fields:
        block_on_pii:
            If True, any "pii" finding with status="blocked" blocks the output.
        block_on_policy:
            If True, any "policy" finding with status="blocked" blocks the output.
        block_on_professionalism:
            If True, any "professionalism" finding with status="blocked" blocks.
    """

    block_on_pii: bool = True
    block_on_policy: bool = True
    block_on_professionalism: bool = False  # Soft fail by default

    def should_block(self, finding: SafetyFinding) -> bool:
        """
        Determine if a single finding should block the output.

        We interpret SafetyFinding.status as:
            • "blocked"  → candidate for hard block
            • "warning"  → candidate for soft block
            • "ok"       → non-blocking
        """
        cat = (finding.category or "").lower()
        status = (finding.status or "").lower()
        is_blocked = status == "blocked"

        # PII — always severe if we are configured to block
        if cat == "pii" and self.block_on_pii and is_blocked:
            return True

        # Harmful / disallowed policy content
        if cat == "policy" and self.block_on_policy and is_blocked:
            return True

        # Professionalism issues (optional hard-block)
        if cat == "professionalism" and self.block_on_professionalism and is_blocked:
            return True

        # Unknown category but explicitly "blocked" → conservative fail
        if cat not in ("pii", "policy", "professionalism") and is_blocked:
            return True

        return False


# =============================================================================
# Safety Gateway Entrypoint
# =============================================================================


def safety_gate(
    safety: SafetyResult,
    policy: Optional[SafetyPolicy] = None,
    workflow_id: Optional[str] = None,
) -> bool:
    """
    Evaluate final SafetyResult and decide if the workflow output is allowed.

    Parameters:
        safety:
            Aggregated SafetyResult from L2 safety agent.
        policy:
            Optional SafetyPolicy override. If None, a default strict policy is used.
        workflow_id:
            Optional workflow identifier for audit logging.

    Returns:
        True  → safe to proceed (including "soft_block" paths).
        False → must be blocked or redacted.
    """
    if policy is None:
        policy = SafetyPolicy()

    try:
        findings: List[SafetyFinding] = list(safety.findings or [])

        blocking_items: List[SafetyFinding] = []
        soft_block_items: List[SafetyFinding] = []
        ok_items: List[SafetyFinding] = []

        for f in findings:
            if policy.should_block(f):
                blocking_items.append(f)
                continue

            status = (f.status or "").lower()
            if status == "warning":
                soft_block_items.append(f)
            else:
                ok_items.append(f)

        # Determine decision label for PolicyDecisionEvent
        if blocking_items:
            decision_label = "block"
            reason = "Blocking safety findings present."
        elif soft_block_items:
            decision_label = "soft_block"
            reason = "Only soft-block safety warnings present."
        else:
            decision_label = "allow"
            reason = "No blocking safety findings."

        # Construct PolicyDecisionEvent for auditability (G20–G21)
        decision_event = PolicyDecisionEvent(
            decision=decision_label,
            reason=reason,
            workflow_id=workflow_id,
            check_id=None,
            details=_build_policy_details(
                safety=safety,
                blocking_items=blocking_items,
                soft_block_items=soft_block_items,
                ok_items=ok_items,
            ),
        )

        emit_policy_decision(decision_event)

        # Hard gate: any "block" decision returns False (fail closed).
        if decision_label == "block":
            return False

        # "allow" and "soft_block" both return True (Phase 1 semantics).
        return True

    except Exception as exc:
        # L5 must always fail closed (conservative stance)
        record_exception("l5.safety_gate_error", exc)
        return False


# =============================================================================
# Helpers
# =============================================================================


def _build_policy_details(
    safety: SafetyResult,
    blocking_items: List[SafetyFinding],
    soft_block_items: List[SafetyFinding],
    ok_items: List[SafetyFinding],
) -> Dict[str, Any]:
    """
    Build a compact, structured details payload for PolicyDecisionEvent.
    """
    return {
        "overall_status": safety.overall_status,
        "num_findings": len(safety.findings or []),
        "num_blocking": len(blocking_items),
        "num_soft_blocking": len(soft_block_items),
        "num_ok": len(ok_items),
        "categories": _summarize_categories(list(safety.findings or [])),
    }


def _summarize_categories(findings: List[SafetyFinding]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for f in findings:
        cat = (f.category or "").lower()
        counts[cat] = counts.get(cat, 0) + 1
    return counts
