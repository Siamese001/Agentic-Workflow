"""
agentic_core/L6_observability/utils/evaluation/promotion_gauntlet.py

Promotion gauntlet — validates staged PromotionCandidates for future-run advancement.

Gauntlet checks (5 per candidate):
  1. shadow_replay_available    — replay_references must be non-empty
  2. regression_gate_pass       — cluster failure_count >= _REGRESSION_GATE_MIN_FAILURES
  3. safety_policy_ready        — failure_mode must not be in _SAFETY_BLOCKED_MODES
  4. rollback_metadata_present  — suggested_changes must be non-empty
  5. destination_class_ready    — classification must be "PROPOSE"

Verdict:
  HOLD                      — candidate not yet ready (below threshold or replay missing)
  REJECT                    — candidate fails safety / policy check
  APPROVE_FOR_PACKETIZATION — all 5 checks pass

Future-run only.  No durable writes.  No L4 access.  No UWG bypass.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentic_core.L2_execution.utils.providers import get_clock

if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.promotion_stager import PromotionCandidate
    from agentic_core.L6_observability.utils.evaluation.rca_aggregator import RcaCluster

# ── Gauntlet verdicts ──────────────────────────────────────────────────────
VERDICT_HOLD = "HOLD"
VERDICT_REJECT = "REJECT"
VERDICT_APPROVE = "APPROVE_FOR_PACKETIZATION"

# ── Thresholds ─────────────────────────────────────────────────────────────
_REGRESSION_GATE_MIN_FAILURES = 3  # must match PromotionStager._PROPOSE_MIN_FAILURES
_SAFETY_BLOCKED_MODES = frozenset({"ESCALATION_MISSED", "POLICY_VIOLATION"})


@dataclass(frozen=True)
class GauntletCheckResult:
    """Result of a single gauntlet check."""

    check_name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class GauntletResult:
    """Sealed gauntlet outcome for one PromotionCandidate.

    verdict:
        "HOLD"                      — not ready; continue monitoring
        "REJECT"                    — fails safety / policy; do not promote
        "APPROVE_FOR_PACKETIZATION" — all 5 checks pass; ready to packetize
    """

    result_id: str
    candidate_id: str
    cluster_key: str
    verdict: str
    checks: tuple[GauntletCheckResult, ...]
    failure_reason: str  # "" for APPROVE
    evaluated_at: float


class PromotionGauntlet:
    """Run gauntlet checks on staged PromotionCandidates.

    No side effects.  No durable writes.  Future-run only.
    """

    def evaluate(
        self,
        candidate: "PromotionCandidate",
        cluster: "RcaCluster",
    ) -> GauntletResult:
        """Run all 5 gauntlet checks against a (candidate, cluster) pair.

        Args:
            candidate: PromotionCandidate from PromotionStager.
            cluster:   RcaCluster from RcaAggregator (must match candidate.cluster_id).

        Returns:
            GauntletResult — sealed outcome.
        """
        checks: list[GauntletCheckResult] = []

        # Check 1: shadow replay available
        replay_ok = len(candidate.replay_references) >= 1
        checks.append(
            GauntletCheckResult(
                check_name="shadow_replay_available",
                passed=replay_ok,
                detail=f"{len(candidate.replay_references)} replay ref(s)",
            )
        )

        # Check 2: regression gate pass (failure count)
        regression_ok = cluster.failure_count >= _REGRESSION_GATE_MIN_FAILURES
        checks.append(
            GauntletCheckResult(
                check_name="regression_gate_pass",
                passed=regression_ok,
                detail=f"failures={cluster.failure_count} min={_REGRESSION_GATE_MIN_FAILURES}",
            )
        )

        # Check 3: safety / policy readiness
        safety_ok = cluster.failure_mode not in _SAFETY_BLOCKED_MODES
        checks.append(
            GauntletCheckResult(
                check_name="safety_policy_ready",
                passed=safety_ok,
                detail=f"mode={cluster.failure_mode} blocked={not safety_ok}",
            )
        )

        # Check 4: rollback metadata present
        rollback_ok = len(candidate.suggested_changes) >= 1
        checks.append(
            GauntletCheckResult(
                check_name="rollback_metadata_present",
                passed=rollback_ok,
                detail=f"{len(candidate.suggested_changes)} change suggestion(s)",
            )
        )

        # Check 5: destination classification ready
        dest_ok = candidate.classification == "PROPOSE"
        checks.append(
            GauntletCheckResult(
                check_name="destination_class_ready",
                passed=dest_ok,
                detail=f"classification={candidate.classification}",
            )
        )

        verdict, failure_reason = _derive_verdict(checks, cluster)
        return GauntletResult(
            result_id=f"gr-{uuid.uuid4().hex[:12]}",
            candidate_id=candidate.candidate_id,
            cluster_key=candidate.cluster_key,
            verdict=verdict,
            checks=tuple(checks),
            failure_reason=failure_reason,
            evaluated_at=get_clock().now_epoch(),
        )


def _derive_verdict(
    checks: list[GauntletCheckResult],
    cluster: "RcaCluster",
) -> tuple[str, str]:
    """Derive verdict and failure_reason from check results.

    Priority:
      1. HOLD   — destination_class_ready failed (HOLD candidate, not PROPOSE)
                  OR shadow_replay_available failed (evidence not yet available)
      2. REJECT — safety/policy check failed, regression gate insufficient, or
                  rollback metadata missing (cannot guarantee safe reversal)
      3. APPROVE_FOR_PACKETIZATION — all 5 passed
    """
    by_name = {c.check_name: c for c in checks}

    if not by_name["destination_class_ready"].passed:
        return VERDICT_HOLD, "Classification is HOLD — cluster below promotion threshold"
    if not by_name["shadow_replay_available"].passed:
        return VERDICT_HOLD, "No shadow replay references available; evidence unverifiable"
    if not by_name["safety_policy_ready"].passed:
        return VERDICT_REJECT, f"Safety/policy blocked: failure_mode={cluster.failure_mode}"
    if not by_name["regression_gate_pass"].passed:
        return (
            VERDICT_REJECT,
            f"Regression gate: {cluster.failure_count} failures below minimum {_REGRESSION_GATE_MIN_FAILURES}",
        )
    if not by_name["rollback_metadata_present"].passed:
        return VERDICT_REJECT, "No rollback metadata; cannot guarantee safe reversal"

    return VERDICT_APPROVE, ""


__all__ = [
    "GauntletCheckResult",
    "GauntletResult",
    "PromotionGauntlet",
    "VERDICT_APPROVE",
    "VERDICT_HOLD",
    "VERDICT_REJECT",
]
