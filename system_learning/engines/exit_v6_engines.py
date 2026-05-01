"""Exit & Eval v6 + L2 v4 + remaining L5 v5 engines.

Covers the KPIs declared in :mod:`system_learning.engines.v7_kpi_board`:

Exit v6
-------
- ``X3_DISPOSITION_UNIQUENESS`` — every committed run has exactly one X3 disposition.
- ``SILENT_FALLBACK_COUNT`` — count of un-disposed fallbacks (must be 0).
- ``UNAUTHORIZED_L4_WRITE_ATTEMPTS`` — count of writes attempted outside the UWG ink-path (must be 0).
- ``UNKNOWN_TO_X3B_ROUTING_CORRECTNESS`` — UNKNOWN dispositions routed to X3B.
- ``COMMIT_PATH_CLEARANCE_COMPLETENESS`` — commit-path runs with full clearance receipts.
- ``ANSWER_ONLY_CLEARANCE_COMPLETENESS`` — answer-only runs with answer-clearance receipts.
- ``SAFE_ABSTAIN_RATE`` — ratio of safe-abstain dispositions on ambiguous tasks.
- ``COMMITTED_ARTIFACT_UWG_RECEIPT_COMPLETENESS`` — every committed artifact has a UWG receipt.

L2 v4
-----
- ``PASS_K_COMMIT_RELIABILITY`` — pass@k success rate for commit-class executions.
- ``PER_TRIAL_ISOLATION_VIOLATIONS`` — k-trial executions where isolation broke.
- ``BOUNDED_WORK_OVERRUN_RATE`` — execution-budget overruns.
- ``CONFIDENCE_ROUTING_MISROUTE_RATE`` — low-confidence routes that should have escalated.

L5 v5 supplements
-----------------
- ``GUARDRAIL_BANK_PASS_RATE`` — ratio of (G_AI / G_FW / G_PA) checks that pass.
- ``STANDARDS_FINGERPRINT_ATTACHMENT_RATE`` — packets carrying a standards fingerprint.
- ``SHADOW_BYPASS_ATTEMPTS_DETECTED`` — shadow-mode bypass attempts (count, EQ 0).
- ``GUARD_MODEL_REVIEW_AGREEMENT_RATE`` — guard model vs human reviewer agreement.

All engines are in-memory counter classes that publish their KPI via
``UnifiedKPIBoard`` through a ``publish_kpi_sample(board)`` method. KPI emission
is fail-safe — recording failures must never break the host engine.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


def _import_v7_kpi():
    from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
        V7KPIName,
        V7KPISample,
    )
    return V7KPIName, V7KPISample


# =====================================================================
# Exit v6 — disposition + clearance receipts
# =====================================================================


class X3Disposition(str, Enum):
    """Exit v6 disposition labels (X3A / X3B / X3C)."""

    COMMIT = "X3A_COMMIT"
    ANSWER_ONLY = "X3A_ANSWER_ONLY"
    UNKNOWN = "X3B_UNKNOWN"
    SAFE_ABSTAIN = "X3C_SAFE_ABSTAIN"


@dataclass
class ExitDispositionTracker:
    """Track exit dispositions and emit ``X3_DISPOSITION_UNIQUENESS`` /
    ``SILENT_FALLBACK_COUNT`` / ``SAFE_ABSTAIN_RATE`` /
    ``UNKNOWN_TO_X3B_ROUTING_CORRECTNESS``."""

    _runs_seen: set[str] = field(default_factory=set)
    _runs_with_disposition: set[str] = field(default_factory=set)
    _runs_with_multiple_dispositions: set[str] = field(default_factory=set)
    _safe_abstain_count: int = 0
    _ambiguous_count: int = 0
    _unknown_routed_correct: int = 0
    _unknown_routed_total: int = 0

    def observe_run(self, run_id: str) -> None:
        """Mark a run as observed; useful for computing ``SILENT_FALLBACK_COUNT``."""
        self._runs_seen.add(run_id)

    def record_disposition(
        self,
        run_id: str,
        disposition: X3Disposition,
        *,
        was_ambiguous: bool = False,
        unknown_routed_to: str | None = None,
    ) -> None:
        """Record one X3 disposition for ``run_id``.

        - If a run sees multiple dispositions, that run is flagged for
          uniqueness violation.
        - If ``was_ambiguous`` and disposition is ``SAFE_ABSTAIN``, increment
          safe-abstain success counter.
        - If disposition is ``UNKNOWN`` and ``unknown_routed_to == "X3B"``,
          increment unknown-routing correct counter.
        """
        if run_id in self._runs_with_disposition:
            self._runs_with_multiple_dispositions.add(run_id)
        else:
            self._runs_with_disposition.add(run_id)
        self._runs_seen.add(run_id)

        if was_ambiguous:
            self._ambiguous_count += 1
            if disposition is X3Disposition.SAFE_ABSTAIN:
                self._safe_abstain_count += 1

        if disposition is X3Disposition.UNKNOWN:
            self._unknown_routed_total += 1
            if unknown_routed_to == "X3B":
                self._unknown_routed_correct += 1

    @property
    def silent_fallback_count(self) -> int:
        """Runs observed without any disposition recorded."""
        return len(self._runs_seen - self._runs_with_disposition)

    @property
    def disposition_uniqueness_rate(self) -> float:
        """Ratio of disposed runs that have exactly one disposition."""
        n = len(self._runs_with_disposition)
        if n == 0:
            return 1.0
        return 1.0 - (len(self._runs_with_multiple_dispositions) / n)

    def reset(self) -> None:
        self._runs_seen.clear()
        self._runs_with_disposition.clear()
        self._runs_with_multiple_dispositions.clear()
        self._safe_abstain_count = 0
        self._ambiguous_count = 0
        self._unknown_routed_correct = 0
        self._unknown_routed_total = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7_kpi()
            ts = time.time()
            board.record(V7KPISample(
                name=V7KPIName.X3_DISPOSITION_UNIQUENESS,
                value=self.disposition_uniqueness_rate,
                timestamp=ts, source="exit_disposition_tracker",
                metadata={"disposed": len(self._runs_with_disposition),
                          "duplicates": len(self._runs_with_multiple_dispositions)},
            ))
            board.record(V7KPISample(
                name=V7KPIName.SILENT_FALLBACK_COUNT,
                value=float(self.silent_fallback_count),
                timestamp=ts, source="exit_disposition_tracker",
                metadata={"observed": len(self._runs_seen),
                          "disposed": len(self._runs_with_disposition)},
            ))
            safe_rate = (
                self._safe_abstain_count / self._ambiguous_count
                if self._ambiguous_count > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.SAFE_ABSTAIN_RATE,
                value=safe_rate,
                timestamp=ts, source="exit_disposition_tracker",
                metadata={"safe": self._safe_abstain_count,
                          "ambiguous": self._ambiguous_count},
            ))
            unknown_rate = (
                self._unknown_routed_correct / self._unknown_routed_total
                if self._unknown_routed_total > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.UNKNOWN_TO_X3B_ROUTING_CORRECTNESS,
                value=unknown_rate,
                timestamp=ts, source="exit_disposition_tracker",
                metadata={"correct": self._unknown_routed_correct,
                          "total": self._unknown_routed_total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break disposition tracking
            logger.warning("v7_kpi_exit_disposition_failed: %s", exc)


@dataclass
class ClearanceReceiptTracker:
    """Track commit-path / answer-only clearance receipts and UWG receipts.

    Emits:
    - ``COMMIT_PATH_CLEARANCE_COMPLETENESS``
    - ``ANSWER_ONLY_CLEARANCE_COMPLETENESS``
    - ``COMMITTED_ARTIFACT_UWG_RECEIPT_COMPLETENESS``
    - ``UNAUTHORIZED_L4_WRITE_ATTEMPTS``
    """

    _commit_runs: int = 0
    _commit_runs_with_clearance: int = 0
    _answer_only_runs: int = 0
    _answer_only_with_clearance: int = 0
    _committed_artifacts: int = 0
    _committed_artifacts_with_uwg: int = 0
    _unauthorized_writes: int = 0

    def record_commit_run(self, *, has_clearance_receipt: bool) -> None:
        self._commit_runs += 1
        if has_clearance_receipt:
            self._commit_runs_with_clearance += 1

    def record_answer_only_run(self, *, has_clearance_receipt: bool) -> None:
        self._answer_only_runs += 1
        if has_clearance_receipt:
            self._answer_only_with_clearance += 1

    def record_committed_artifact(self, *, has_uwg_receipt: bool) -> None:
        self._committed_artifacts += 1
        if has_uwg_receipt:
            self._committed_artifacts_with_uwg += 1

    def record_unauthorized_write_attempt(self) -> None:
        self._unauthorized_writes += 1

    def reset(self) -> None:
        self._commit_runs = 0
        self._commit_runs_with_clearance = 0
        self._answer_only_runs = 0
        self._answer_only_with_clearance = 0
        self._committed_artifacts = 0
        self._committed_artifacts_with_uwg = 0
        self._unauthorized_writes = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7_kpi()
            ts = time.time()

            commit_rate = (
                self._commit_runs_with_clearance / self._commit_runs
                if self._commit_runs > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.COMMIT_PATH_CLEARANCE_COMPLETENESS,
                value=commit_rate, timestamp=ts,
                source="clearance_receipt_tracker",
                metadata={"with_clearance": self._commit_runs_with_clearance,
                          "total": self._commit_runs},
            ))

            answer_rate = (
                self._answer_only_with_clearance / self._answer_only_runs
                if self._answer_only_runs > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.ANSWER_ONLY_CLEARANCE_COMPLETENESS,
                value=answer_rate, timestamp=ts,
                source="clearance_receipt_tracker",
                metadata={"with_clearance": self._answer_only_with_clearance,
                          "total": self._answer_only_runs},
            ))

            uwg_rate = (
                self._committed_artifacts_with_uwg / self._committed_artifacts
                if self._committed_artifacts > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.COMMITTED_ARTIFACT_UWG_RECEIPT_COMPLETENESS,
                value=uwg_rate, timestamp=ts,
                source="clearance_receipt_tracker",
                metadata={"with_uwg": self._committed_artifacts_with_uwg,
                          "total": self._committed_artifacts},
            ))

            board.record(V7KPISample(
                name=V7KPIName.UNAUTHORIZED_L4_WRITE_ATTEMPTS,
                value=float(self._unauthorized_writes), timestamp=ts,
                source="clearance_receipt_tracker",
                metadata={"count": self._unauthorized_writes},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break clearance tracking
            logger.warning("v7_kpi_clearance_receipt_failed: %s", exc)


# =====================================================================
# L2 v4 — pass@k, isolation, bounded work, confidence routing
# =====================================================================


@dataclass
class L2ExecuteV4Tracker:
    """Track L2 v4 execute KPIs.

    Emits:
    - ``PASS_K_COMMIT_RELIABILITY``
    - ``PER_TRIAL_ISOLATION_VIOLATIONS``
    - ``BOUNDED_WORK_OVERRUN_RATE``
    - ``CONFIDENCE_ROUTING_MISROUTE_RATE``
    """

    _pass_k_total: int = 0
    _pass_k_succeeded: int = 0
    _isolation_violations: int = 0
    _bounded_work_runs: int = 0
    _bounded_work_overruns: int = 0
    _confidence_routes: int = 0
    _confidence_misroutes: int = 0

    def record_pass_k_run(self, *, succeeded: bool) -> None:
        self._pass_k_total += 1
        if succeeded:
            self._pass_k_succeeded += 1

    def record_isolation_violation(self) -> None:
        self._isolation_violations += 1

    def record_bounded_work_run(self, *, overran: bool) -> None:
        self._bounded_work_runs += 1
        if overran:
            self._bounded_work_overruns += 1

    def record_confidence_route(self, *, misrouted: bool) -> None:
        self._confidence_routes += 1
        if misrouted:
            self._confidence_misroutes += 1

    def reset(self) -> None:
        self._pass_k_total = 0
        self._pass_k_succeeded = 0
        self._isolation_violations = 0
        self._bounded_work_runs = 0
        self._bounded_work_overruns = 0
        self._confidence_routes = 0
        self._confidence_misroutes = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7_kpi()
            ts = time.time()

            pass_rate = (
                self._pass_k_succeeded / self._pass_k_total
                if self._pass_k_total > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.PASS_K_COMMIT_RELIABILITY,
                value=pass_rate, timestamp=ts, source="l2_execute_v4_tracker",
                metadata={"passed": self._pass_k_succeeded,
                          "total": self._pass_k_total},
            ))
            board.record(V7KPISample(
                name=V7KPIName.PER_TRIAL_ISOLATION_VIOLATIONS,
                value=float(self._isolation_violations), timestamp=ts,
                source="l2_execute_v4_tracker",
                metadata={"count": self._isolation_violations},
            ))
            overrun_rate = (
                self._bounded_work_overruns / self._bounded_work_runs
                if self._bounded_work_runs > 0 else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.BOUNDED_WORK_OVERRUN_RATE,
                value=overrun_rate, timestamp=ts,
                source="l2_execute_v4_tracker",
                metadata={"overruns": self._bounded_work_overruns,
                          "total": self._bounded_work_runs},
            ))
            misroute_rate = (
                self._confidence_misroutes / self._confidence_routes
                if self._confidence_routes > 0 else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.CONFIDENCE_ROUTING_MISROUTE_RATE,
                value=misroute_rate, timestamp=ts,
                source="l2_execute_v4_tracker",
                metadata={"misrouted": self._confidence_misroutes,
                          "total": self._confidence_routes},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break L2 v4 tracking
            logger.warning("v7_kpi_l2_execute_v4_failed: %s", exc)


# =====================================================================
# L5 v5 supplements — guardrail bank, standards fingerprint, shadow bypass,
# guard model agreement
# =====================================================================


@dataclass
class L5GovernanceV5Tracker:
    """Track remaining L5 v5 KPIs.

    Emits:
    - ``GUARDRAIL_BANK_PASS_RATE``
    - ``STANDARDS_FINGERPRINT_ATTACHMENT_RATE``
    - ``SHADOW_BYPASS_ATTEMPTS_DETECTED``
    - ``GUARD_MODEL_REVIEW_AGREEMENT_RATE``
    """

    _guardrail_total: int = 0
    _guardrail_passed: int = 0
    _packets_total: int = 0
    _packets_with_fingerprint: int = 0
    _shadow_bypass_attempts: int = 0
    _guard_reviews_total: int = 0
    _guard_reviews_agreed: int = 0

    def record_guardrail_check(self, *, passed: bool) -> None:
        self._guardrail_total += 1
        if passed:
            self._guardrail_passed += 1

    def record_packet(self, *, has_standards_fingerprint: bool) -> None:
        self._packets_total += 1
        if has_standards_fingerprint:
            self._packets_with_fingerprint += 1

    def record_shadow_bypass_attempt(self) -> None:
        self._shadow_bypass_attempts += 1

    def record_guard_review(self, *, agrees_with_human: bool) -> None:
        self._guard_reviews_total += 1
        if agrees_with_human:
            self._guard_reviews_agreed += 1

    def reset(self) -> None:
        self._guardrail_total = 0
        self._guardrail_passed = 0
        self._packets_total = 0
        self._packets_with_fingerprint = 0
        self._shadow_bypass_attempts = 0
        self._guard_reviews_total = 0
        self._guard_reviews_agreed = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7_kpi()
            ts = time.time()

            gb_rate = (
                self._guardrail_passed / self._guardrail_total
                if self._guardrail_total > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.GUARDRAIL_BANK_PASS_RATE,
                value=gb_rate, timestamp=ts, source="l5_governance_v5_tracker",
                metadata={"passed": self._guardrail_passed,
                          "total": self._guardrail_total},
            ))

            sf_rate = (
                self._packets_with_fingerprint / self._packets_total
                if self._packets_total > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.STANDARDS_FINGERPRINT_ATTACHMENT_RATE,
                value=sf_rate, timestamp=ts, source="l5_governance_v5_tracker",
                metadata={"with_fingerprint": self._packets_with_fingerprint,
                          "total": self._packets_total},
            ))

            board.record(V7KPISample(
                name=V7KPIName.SHADOW_BYPASS_ATTEMPTS_DETECTED,
                value=float(self._shadow_bypass_attempts), timestamp=ts,
                source="l5_governance_v5_tracker",
                metadata={"count": self._shadow_bypass_attempts},
            ))

            gm_rate = (
                self._guard_reviews_agreed / self._guard_reviews_total
                if self._guard_reviews_total > 0 else 1.0
            )
            board.record(V7KPISample(
                name=V7KPIName.GUARD_MODEL_REVIEW_AGREEMENT_RATE,
                value=gm_rate, timestamp=ts, source="l5_governance_v5_tracker",
                metadata={"agreed": self._guard_reviews_agreed,
                          "total": self._guard_reviews_total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break L5 v5 tracking
            logger.warning("v7_kpi_l5_governance_v5_failed: %s", exc)


__all__ = [
    "X3Disposition",
    "ExitDispositionTracker",
    "ClearanceReceiptTracker",
    "L2ExecuteV4Tracker",
    "L5GovernanceV5Tracker",
]
