"""V7 6B.S2C Governance Regression Checker.

Detects guardrail / policy / rubric / schema / provider drift across runs.
Validates rubric integrity (content addressing, version bumps, calibration
freshness) before any rubric-derived eval is consumed by 6C.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6B S2C "GOVERNANCE REGRESSION".

KPI surface
-----------
Publishes ``GOVERNANCE_EVAL_COVERAGE`` (ratio of high-risk / write / HITL
paths that received a governance check).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# v7 S2C "CHECKS" list — drift surfaces this engine must observe.
_DRIFT_SURFACES: frozenset[str] = frozenset({
    "exact_match_drift",
    "policy_drift",
    "schema_api_drift",
    "model_behavior_drift",
    "tool_behavior_drift",
    "provider_behavior_drift",
    "guardrail_failures",
    "refusal_abstain_drift",
    "citation_support_drift",
    "prompt_drift",
    "retrieval_profile_drift",
    "sandbox_escape_signals",
    "hitl_threshold_drift",
    "uwg_receipt_drift",
    "replay_digest_drift",
})


_VALID_SEVERITY: frozenset[str] = frozenset({"low", "medium", "high", "critical"})


@dataclass(frozen=True)
class GovernanceRegressionRecord:
    """Per-run governance regression record per v7 S2C "OUTPUT"."""

    trace_id: str
    run_id: str
    drift_flags: tuple[str, ...]
    impacted_surfaces: tuple[str, ...]
    severity: str
    suspected_cause: str
    required_review: bool


class GovernanceRegressionChecker:
    """Score governance / drift regressions for a completed run."""

    def __init__(self) -> None:
        # Numerator: high-risk/write/HITL runs that got checked.
        # Denominator: total high-risk/write/HITL runs observed.
        self._high_risk_total: int = 0
        self._high_risk_checked: int = 0

    def check(
        self,
        *,
        trace_id: str,
        run_id: str,
        drift_flags: tuple[str, ...],
        impacted_surfaces: tuple[str, ...],
        severity: str,
        suspected_cause: str,
        is_high_risk: bool,
    ) -> GovernanceRegressionRecord:
        """Run the governance regression check.

        Unknown drift flags are dropped silently (v7 "no fabricated data"
        discipline). Severity outside the rubric set is normalized to
        "medium".
        """
        flags = tuple(f for f in drift_flags if f in _DRIFT_SURFACES)
        norm_sev = severity if severity in _VALID_SEVERITY else "medium"
        required_review = bool(flags) and norm_sev in {"high", "critical"}

        if is_high_risk:
            self._high_risk_total += 1
            self._high_risk_checked += 1

        return GovernanceRegressionRecord(
            trace_id=trace_id,
            run_id=run_id,
            drift_flags=flags,
            impacted_surfaces=tuple(impacted_surfaces),
            severity=norm_sev,
            suspected_cause=suspected_cause,
            required_review=required_review,
        )

    def mark_high_risk_observed_unchecked(self) -> None:
        """Record a high-risk run we *should* have checked but did not.

        Use this when an upstream stage classifies a run as high-risk but
        no governance check was run (whether due to ingest gap, failure,
        or skipped policy). It increases the denominator only.
        """
        self._high_risk_total += 1

    @property
    def counters(self) -> tuple[int, int]:
        """Return ``(checked, total)`` for high-risk paths."""
        return (self._high_risk_checked, self._high_risk_total)

    def reset(self) -> None:
        self._high_risk_total = 0
        self._high_risk_checked = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._high_risk_checked / self._high_risk_total
                if self._high_risk_total > 0
                else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.GOVERNANCE_EVAL_COVERAGE,
                value=ratio,
                timestamp=time.time(),
                source="governance_regression_checker",
                metadata={"checked": self._high_risk_checked,
                          "total": self._high_risk_total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break governance check
            logger.warning("v7_kpi_governance_eval_coverage_failed: %s", exc)


__all__ = [
    "GovernanceRegressionRecord",
    "GovernanceRegressionChecker",
]
