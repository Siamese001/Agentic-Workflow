# FILE: 10_10/l5.py
"""
L5 Safety Gateway — Final Gating Layer (v10_10)
===============================================

Responsibilities:
    • Interpret SafetyResult produced by L2 cognitive safety agent.
    • Apply a deterministic SafetyPolicy.
    • Produce a single boolean gate: safety_passed = True/False.
    • Emit observability events for auditing and meta-learning.

Non-Responsibilities:
    • No LLM calls (handled at L2).
    • No execution (L2).
    • No DAG orchestration (L3).
    • No state mutation (L4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from models import SafetyResult, SafetyFinding
from observability import record_event, record_exception


# =============================================================================
# Safety Policy Model
# =============================================================================

@dataclass
class SafetyPolicy:
    """
    Deterministic safety policy for final gating.

    Rules:
        • If category == "pii"        AND blocking=True → FAIL
        • If category == "policy"     AND blocking=True → FAIL
        • If category == "professionalism" AND blocking=True:
              → FAIL only if block_on_professionalism=True
        • If unknown category AND blocking=True:
              → Always FAIL (conservative default)
    """

    block_on_pii: bool = True
    block_on_policy: bool = True
    block_on_professionalism: bool = False  # Soft fail by default

    def should_block(self, finding: SafetyFinding) -> bool:
        """
        Determine if a single finding should block the output.
        """
        cat = (finding.category or "").lower()

        # PII — always severe if blocking
        if cat == "pii" and self.block_on_pii and finding.blocking:
            return True

        # Harmful content / disallowed content
        if cat == "policy" and self.block_on_policy and finding.blocking:
            return True

        # Professionalism issues
        if cat == "professionalism" and self.block_on_professionalism and finding.blocking:
            return True

        # Unknown category but blocking=True → conservative fail
        if cat not in ("pii", "policy", "professionalism") and finding.blocking:
            return True

        return False


# =============================================================================
# Safety Gateway Entrypoint
# =============================================================================

def safety_gate(
    safety: SafetyResult,
    policy: SafetyPolicy | None = None,
) -> bool:
    """
    Evaluate final SafetyResult and decide if the workflow output is allowed.

    Returns:
        True  → safe to proceed
        False → must be blocked or redacted
    """

    if policy is None:
        policy = SafetyPolicy()

    try:
        blocking_items: List[SafetyFinding] = []
        soft_block_items: List[SafetyFinding] = []

        for f in (safety.findings or []):
            if policy.should_block(f):
                blocking_items.append(f)
            elif f.blocking:
                # "blocking=True" but policy treats category as soft
                soft_block_items.append(f)

        # Emit observability event
        record_event(
            "l5.safety_gate_evaluated",
            {
                "num_findings": len(safety.findings or []),
                "num_blocking_policy": len(blocking_items),
                "num_soft_blocking": len(soft_block_items),
            },
        )

        # Hard decision
        if blocking_items:
            return False

        return True

    except Exception as exc:
        # L5 must always fail closed (conservative stance)
        record_exception("l5.safety_gate_error", exc)
        return False
