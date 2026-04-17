"""Validate staged promotion candidates for future-run advancement."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

try:
    from agentic_core.L2_execution.utils.providers import (
        get_clock,
    )  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
except Exception:  # guardian: allow-broad-exception
    get_clock = None

if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.promotion_stager import PromotionCandidate
    from agentic_core.L6_observability.utils.evaluation.rca_aggregator import RcaCluster

VERDICT_HOLD = "HOLD"
VERDICT_REJECT = "REJECT"
VERDICT_APPROVE = "APPROVE_FOR_PACKETIZATION"

_REGRESSION_GATE_MIN_FAILURES = 3
_SAFETY_BLOCKED_MODES = frozenset({"ESCALATION_MISSED", "POLICY_VIOLATION"})


def _now_epoch() -> float:
    if get_clock is not None:
        try:
            return float(get_clock().now_epoch())
        except Exception:  # guardian: allow-broad-exception
            pass
    return time.time()


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()[:16]}"


@dataclass(frozen=True)
class GauntletCheckResult:
    check_name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class GauntletResult:
    result_id: str
    candidate_id: str
    cluster_key: str
    verdict: str
    checks: tuple[GauntletCheckResult, ...]
    failure_reason: str
    evaluated_at: float


class PromotionGauntlet:
    def evaluate(self, candidate: "PromotionCandidate", cluster: "RcaCluster") -> GauntletResult:
        checks: list[GauntletCheckResult] = []
        replay_ok = len(candidate.replay_references) >= 1
        checks.append(
            GauntletCheckResult(
                "shadow_replay_available", replay_ok, f"{len(candidate.replay_references)} replay ref(s)"
            )
        )
        regression_ok = getattr(cluster, "failure_count", 0) >= _REGRESSION_GATE_MIN_FAILURES
        checks.append(
            GauntletCheckResult(
                "regression_gate_pass",
                regression_ok,
                f"failures={getattr(cluster, 'failure_count', 0)} min={_REGRESSION_GATE_MIN_FAILURES}",
            )
        )
        safety_ok = getattr(cluster, "failure_mode", "UNKNOWN") not in _SAFETY_BLOCKED_MODES
        checks.append(
            GauntletCheckResult(
                "safety_policy_ready",
                safety_ok,
                f"mode={getattr(cluster, 'failure_mode', 'UNKNOWN')} blocked={not safety_ok}",
            )
        )
        rollback_ok = len(candidate.suggested_changes) >= 1
        checks.append(
            GauntletCheckResult(
                "rollback_metadata_present",
                rollback_ok,
                f"{len(candidate.suggested_changes)} change suggestion(s)",
            )
        )
        dest_ok = candidate.classification == "PROPOSE"
        checks.append(
            GauntletCheckResult(
                "destination_class_ready",
                dest_ok,
                f"classification={candidate.classification}",
            )
        )
        verdict, failure_reason = _derive_verdict(checks, cluster)
        return GauntletResult(
            result_id=_stable_id(
                "gr",
                {
                    "candidate_id": candidate.candidate_id,
                    "cluster_key": candidate.cluster_key,
                    "verdict": verdict,
                    "failure_reason": failure_reason,
                },
            ),
            candidate_id=candidate.candidate_id,
            cluster_key=candidate.cluster_key,
            verdict=verdict,
            checks=tuple(checks),
            failure_reason=failure_reason,
            evaluated_at=_now_epoch(),
        )


def _derive_verdict(checks: list[GauntletCheckResult], cluster: "RcaCluster") -> tuple[str, str]:
    by_name = {check.check_name: check for check in checks}
    if not by_name["destination_class_ready"].passed:
        return VERDICT_HOLD, "Classification is HOLD — cluster below promotion threshold"
    if not by_name["shadow_replay_available"].passed:
        return VERDICT_HOLD, "No shadow replay references available; evidence unverifiable"
    if not by_name["safety_policy_ready"].passed:
        return VERDICT_REJECT, f"Safety/policy blocked: failure_mode={cluster.failure_mode}"
    if not by_name["regression_gate_pass"].passed:
        return VERDICT_REJECT, (
            f"Regression gate: {cluster.failure_count} failures below minimum {_REGRESSION_GATE_MIN_FAILURES}"
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
