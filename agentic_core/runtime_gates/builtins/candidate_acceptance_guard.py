"""Candidate Acceptance Guard — Non-bypassable core gate.

Ensures that rejected candidates (accepted=False from PER-CAND gates) are
NEVER written to resume_data. This is the core write-boundary guard that
prevents the exec_summary RCA bug: winner written despite accepted=False.

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W1.P1)
"""

from __future__ import annotations

from typing import Any

from agentic_core.L5_safety.runtime_gates.contracts import Result
from agentic_core.runtime_gates.definitions import GateVerdict


class CandidateAcceptanceGuard:
    """Core write-boundary gate: validates candidate acceptance before write.
    
    This is a non-bypassable gate that lives in agentic_core, ensuring
    apps_rg cannot accidentally write rejected candidates to resume_data.
    """

    GATE_ID: str = "candidate_acceptance_guard"

    @staticmethod
    def evaluate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
        """Evaluate whether the candidate is accepted.

        Args:
            artifact: The candidate/winner artifact (expected to have 'accepted' attr)
            context: Runtime context with per-cand gate results

        Returns:
            GateVerdict: FAIL if candidate rejected, PASS if accepted
        """
        # Extract accepted status from artifact
        # The artifact should be the ensemble winner with 'accepted' field
        accepted = getattr(artifact, "accepted", None)
        
        if accepted is None and isinstance(artifact, dict):
            accepted = artifact.get("accepted")

        # Also check context for per-cand gate failures
        per_cand_results = context.get("per_cand_results", {})
        has_per_cand_failure = any(
            r in (Result.FAIL, Result.UNKNOWN)
            for r in per_cand_results.values()
        )

        if accepted is False or has_per_cand_failure:
            reason = "Candidate rejected by PER-CAND gate — cannot write to resume_data"
            codes = ["candidate_rejected_by_per_cand_gate", "write_blocked"]
            if has_per_cand_failure:
                failed_gates = [
                    g for g, r in per_cand_results.items()
                    if r in (Result.FAIL, Result.UNKNOWN)
                ]
                codes.extend(failed_gates)
            
            return GateVerdict(
                gate_id=CandidateAcceptanceGuard.GATE_ID,
                result=Result.FAIL,
                reason=reason,
                reason_codes=tuple(codes),
            )

        if accepted is True:
            return GateVerdict(
                gate_id=CandidateAcceptanceGuard.GATE_ID,
                result=Result.PASS,
                reason="Candidate accepted by PER-CAND gate",
                reason_codes=("candidate_accepted", "write_authorized"),
            )

        # accepted is None or unknown
        return GateVerdict(
            gate_id=CandidateAcceptanceGuard.GATE_ID,
            result=Result.UNKNOWN,
            reason="Candidate acceptance status unknown — fail-closed",
            reason_codes=("unknown_acceptance_status", "fail_closed"),
        )


def candidate_acceptance_guard_callable(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """Callable wrapper for use in RuntimeGateEngine."""
    return CandidateAcceptanceGuard.evaluate(artifact, context)


__all__ = [
    "CandidateAcceptanceGuard",
    "candidate_acceptance_guard_callable",
]
