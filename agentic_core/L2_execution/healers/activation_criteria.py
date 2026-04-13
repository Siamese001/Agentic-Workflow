"""Activation criteria checker and runtime rollback monitor for C3 heal-classifier.

check_activation_criteria() verifies all prerequisites before shadow→active
promotion is authorized.

RollbackMonitor enforces automatic fallback to heuristic routing at runtime
when any degradation metric exceeds its threshold.  Once latched, the monitor
stays latched; re-authorization requires a new wire_governed_scorer() call with
a fresh activation_record.json.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..types.heal_contract_types import ClassifierSource

if TYPE_CHECKING:
    from ..types.heal_contract_types import HealClassifierTelemetry


# ---------------------------------------------------------------------------
# Default thresholds (align with tools/heal_classifier/constants.py)
# ---------------------------------------------------------------------------

MIN_SHADOW_EVENTS: int = 500
MAX_DIVERGENCE_RATE: float = 0.30
MIN_REPAIR_SUCCESS_RATE: float = 0.60
MAX_OOD_RATE: float = 0.01
MAX_LATENCY_P99_US: int = 1000
MAX_FALLBACK_RATE_ACTIVE: float = 0.10
ROLLBACK_WINDOW: int = 200


# ---------------------------------------------------------------------------
# Criteria data contracts
# ---------------------------------------------------------------------------


@dataclass
class ActivationCriteria:
    """Configurable thresholds for shadow→active promotion and runtime rollback."""

    min_shadow_events: int = MIN_SHADOW_EVENTS
    max_divergence_rate: float = MAX_DIVERGENCE_RATE
    min_repair_success_rate: float = MIN_REPAIR_SUCCESS_RATE
    max_ood_rate: float = MAX_OOD_RATE
    max_latency_p99_us: int = MAX_LATENCY_P99_US
    max_fallback_rate: float = MAX_FALLBACK_RATE_ACTIVE


@dataclass
class CriteriaEvidence:
    """Snapshot of observed metrics used to evaluate activation readiness."""

    shadow_event_count: int
    divergence_rate: float
    repair_success_rate: float
    ood_rate: float
    latency_p99_us: int
    artifact_hash_valid: bool
    replay_binding_present: bool
    manual_review_passed: bool


@dataclass
class CriteriaResult:
    """Outcome of a criteria evaluation run."""

    passed: bool
    failures: list[str]


# ---------------------------------------------------------------------------
# Criteria evaluation
# ---------------------------------------------------------------------------


def check_activation_criteria(
    evidence: CriteriaEvidence,
    criteria: ActivationCriteria | None = None,
) -> CriteriaResult:
    """Verify all active-mode prerequisites.

    Every criterion must pass for CriteriaResult.passed to be True.
    All failures are collected and returned regardless of which criterion failed first.
    """
    if criteria is None:
        criteria = ActivationCriteria()

    failures: list[str] = []

    if evidence.shadow_event_count < criteria.min_shadow_events:
        failures.append(
            f"shadow_event_count={evidence.shadow_event_count} < min={criteria.min_shadow_events}"
        )

    if evidence.divergence_rate > criteria.max_divergence_rate:
        failures.append(
            f"divergence_rate={evidence.divergence_rate:.3f} > max={criteria.max_divergence_rate:.3f}"
        )

    if evidence.repair_success_rate < criteria.min_repair_success_rate:
        failures.append(
            f"repair_success_rate={evidence.repair_success_rate:.3f} < "
            f"min={criteria.min_repair_success_rate:.3f}"
        )

    if evidence.ood_rate > criteria.max_ood_rate:
        failures.append(f"ood_rate={evidence.ood_rate:.4f} > max={criteria.max_ood_rate:.4f}")

    if evidence.latency_p99_us > criteria.max_latency_p99_us:
        failures.append(f"latency_p99_us={evidence.latency_p99_us} > max={criteria.max_latency_p99_us}")

    if not evidence.artifact_hash_valid:
        failures.append("artifact_hash_valid=False")

    if not evidence.replay_binding_present:
        failures.append("replay_binding_present=False")

    if not evidence.manual_review_passed:
        failures.append("manual_review_passed=False")

    return CriteriaResult(passed=len(failures) == 0, failures=failures)


# ---------------------------------------------------------------------------
# Runtime rollback monitor
# ---------------------------------------------------------------------------


class RollbackMonitor:
    """Sliding window monitor for automatic rollback triggering.

    Tracks a rolling window of scored-signal telemetry events and latches
    when any degradation metric exceeds its threshold:
      - fallback_rate > max_fallback_rate (captures OOD, hash mismatch, latency, exceptions)
      - latency p99 > max_latency_p99_us
      - repair_success_rate < min_repair_success_rate (when enough outcomes known)

    The monitor requires at least max(10, window_size // 10) events before
    making any rollback decision (avoids false positives at startup).

    Once latched, the monitor stays latched.  Re-authorization requires a new
    wire_governed_scorer() call — there is no reset path.
    """

    def __init__(
        self,
        window_size: int = ROLLBACK_WINDOW,
        criteria: ActivationCriteria | None = None,
    ) -> None:
        self._window_size = window_size
        self._criteria = criteria or ActivationCriteria()
        self._events: collections.deque[dict] = collections.deque(maxlen=window_size)
        self._rollback_triggered: bool = False
        self._rollback_reason: str = ""

    def record(
        self,
        event: HealClassifierTelemetry,
        repair_succeeded: bool | None = None,
    ) -> None:
        """Record a telemetry event into the rolling window.

        Once latched, new events are silently ignored.
        """
        if self._rollback_triggered:
            return
        self._events.append(
            {
                "fallback": event.source == ClassifierSource.HEURISTIC_FALLBACK,
                "latency_us": event.inference_latency_us,
                "repair_succeeded": repair_succeeded,
            }
        )
        triggered, reason = self._evaluate()
        if triggered:
            self._rollback_triggered = True
            self._rollback_reason = reason

    def should_rollback(self) -> tuple[bool, str]:
        """Return (should_rollback, reason).  Reason is empty when safe."""
        if self._rollback_triggered:
            return True, self._rollback_reason
        return self._evaluate()

    def _evaluate(self) -> tuple[bool, str]:
        """Evaluate the current window.  Does not latch."""
        n = len(self._events)
        min_sample = max(10, self._window_size // 10)
        if n < min_sample:
            return False, ""

        c = self._criteria

        fallback_rate = sum(1 for e in self._events if e["fallback"]) / n
        if fallback_rate > c.max_fallback_rate:
            return True, f"fallback_rate={fallback_rate:.3f} > max={c.max_fallback_rate:.3f}"

        latencies = [e["latency_us"] for e in self._events if e["latency_us"] > 0]
        if latencies:
            p99_idx = max(0, int(len(latencies) * 0.99) - 1)
            p99 = sorted(latencies)[p99_idx]
            if p99 > c.max_latency_p99_us:
                return True, f"latency_p99={p99}us > max={c.max_latency_p99_us}us"

        repairs = [e["repair_succeeded"] for e in self._events if e["repair_succeeded"] is not None]
        if len(repairs) >= 10:
            success_rate = sum(1 for r in repairs if r) / len(repairs)
            if success_rate < c.min_repair_success_rate:
                return (
                    True,
                    f"repair_success={success_rate:.3f} < min={c.min_repair_success_rate:.3f}",
                )

        return False, ""

    @property
    def is_latched(self) -> bool:
        """True once rollback has been triggered."""
        return self._rollback_triggered

    @property
    def event_count(self) -> int:
        return len(self._events)

    def stats(self) -> dict:
        """Current window statistics for diagnostics."""
        n = len(self._events)
        if n == 0:
            return {"n": 0}
        return {
            "n": n,
            "fallback_rate": sum(1 for e in self._events if e["fallback"]) / n,
            "rollback_triggered": self._rollback_triggered,
            "rollback_reason": self._rollback_reason,
        }
