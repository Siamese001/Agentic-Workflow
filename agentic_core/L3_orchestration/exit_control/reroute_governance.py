"""Exit Eval reroute governance — ceiling + judge disagreement + replay SLO.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W10.

Closes opportunities 8.1 (reroute-loop ceiling), 8.2 (judge ensemble
disagreement metric), 8.3 (replay-certification SLO — block UWG, not warn).

Three surfaces:

1. :class:`RerouteCeiling` — caps reroute count per request. Beyond the
   cap, the next attempt forces R5 + audit row.
2. :func:`judge_disagreement_rate` — rubric-judge vs span-grader disagree
   per row. Returns the global rate; high values trigger a calibration
   alarm.
3. :func:`replay_cert_blocks` — given replay-certification failures,
   returns the set of decision_ids that MUST NOT be committed via UWG.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field


class RerouteCeilingExceededError(RuntimeError):
    """Raised when a request asks for an N+1 reroute past the ceiling."""


@dataclass
class RerouteCeiling:
    """Per-request reroute counter with a hard ceiling.

    Threshold default = 2 (initial route + 2 reroutes = 3 dispatches max).
    """

    max_reroutes: int = 2
    _counts: dict[str, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        if self.max_reroutes < 0:
            raise ValueError("max_reroutes must be >= 0")

    def attempt_reroute(self, request_id: str) -> int:
        """Register one reroute attempt for ``request_id``.

        W5.8 (closed-loop-router-fleet-rollout-d8f2a3 NEXT_STEP): every
        attempt is durably recorded to router_l3_reroute ledger
        (allow|ceiling_exceeded). Fail-soft.

        Returns:
            The new reroute count (1-indexed).

        Raises:
            RerouteCeilingExceededError: When this attempt would exceed
                ``max_reroutes``.
        """
        with self._lock:
            current = self._counts.get(request_id, 0)
            if current >= self.max_reroutes:
                _record_reroute_decision(
                    request_id=request_id,
                    current_count=current,
                    max_reroutes=self.max_reroutes,
                    allowed=False,
                )
                raise RerouteCeilingExceededError(
                    f"request_id={request_id!r} exceeded reroute ceiling "
                    f"({self.max_reroutes}); force R5",
                )
            self._counts[request_id] = current + 1
            new_count = self._counts[request_id]
        _record_reroute_decision(
            request_id=request_id,
            current_count=new_count,
            max_reroutes=self.max_reroutes,
            allowed=True,
        )
        return new_count

    def reroute_count(self, request_id: str) -> int:
        with self._lock:
            return self._counts.get(request_id, 0)

    def reset(self, request_id: str | None = None) -> None:
        with self._lock:
            if request_id is None:
                self._counts.clear()
            else:
                self._counts.pop(request_id, None)


def judge_disagreement_rate(
    rubric_verdicts: list[bool],
    span_grader_verdicts: list[bool],
) -> float:
    """Fraction of rows where the two judges disagree.

    Both lists must be the same length (one verdict per evaluated row).
    Empty input → 0.0.
    """
    if len(rubric_verdicts) != len(span_grader_verdicts):
        raise ValueError(
            f"length mismatch: rubric={len(rubric_verdicts)}, "
            f"span_grader={len(span_grader_verdicts)}",
        )
    if not rubric_verdicts:
        return 0.0
    disagreements = sum(
        1
        for r, s in zip(rubric_verdicts, span_grader_verdicts, strict=True)
        if r != s
    )
    return disagreements / len(rubric_verdicts)


@dataclass(frozen=True)
class ReplayCertResult:
    decision_id: str
    expected_digest: str
    observed_digest: str

    @property
    def passed(self) -> bool:
        return self.expected_digest == self.observed_digest


def replay_cert_blocks(results: list[ReplayCertResult]) -> set[str]:
    """Return the decision_ids whose replay-cert failed.

    Per opportunity 8.3, replay-cert failure must HARD-BLOCK the UWG path,
    not just warn. Caller passes the set into the UWG admission gate.
    """
    return {r.decision_id for r in results if not r.passed}


@dataclass
class JudgeDisagreementSummary:
    n_rows: int
    rate: float
    threshold: float
    alarm: bool


def evaluate_judge_disagreement(
    rubric_verdicts: list[bool],
    span_grader_verdicts: list[bool],
    *,
    alarm_threshold: float = 0.15,
) -> JudgeDisagreementSummary:
    """Compute disagreement rate and decide whether the alarm fires."""
    if not 0.0 <= alarm_threshold <= 1.0:
        raise ValueError("alarm_threshold out of [0,1]")
    rate = judge_disagreement_rate(rubric_verdicts, span_grader_verdicts)
    return JudgeDisagreementSummary(
        n_rows=len(rubric_verdicts),
        rate=rate,
        threshold=alarm_threshold,
        alarm=rate > alarm_threshold,
    )


# =====================================================================
# Constitutional §29 — closed-loop wiring (W5.8)
# =====================================================================
import logging as _logging  # noqa: E402

_REROUTE_LOGGER = _logging.getLogger(__name__)
_REROUTE_HELPER = None  # type: ignore[var-annotated]


def _get_reroute_helper():
    """Lazy singleton for the L3/reroute RouterClosedLoopHelper."""
    global _REROUTE_HELPER  # noqa: PLW0603
    if _REROUTE_HELPER is not None:
        return _REROUTE_HELPER
    try:
        from tools.ledgers.router_helper import RouterClosedLoopHelper  # noqa: PLC0415

        _REROUTE_HELPER = RouterClosedLoopHelper(
            layer="L3",
            router="reroute",
            ledger_name="router_l3_reroute",
            repo_area="agentic_core/L3_orchestration/exit_control/reroute_governance.py",
        )
        return _REROUTE_HELPER
    except ImportError:  # guardian: allow-log-and-swallow -- helper unavailable must not break reroute ceiling
        _REROUTE_LOGGER.debug("RouterClosedLoopHelper unavailable for L3/reroute", exc_info=True)
        return None


def _record_reroute_decision(
    *,
    request_id: str,
    current_count: int,
    max_reroutes: int,
    allowed: bool,
) -> None:
    """Record reroute attempt + bind outcome.

    Decision-and-outcome-in-one-shot pattern. The "outcome" is whether the
    attempt was allowed (the ceiling was not exceeded). Fail-soft.
    """
    helper = _get_reroute_helper()
    if helper is None:
        return
    try:
        # Predict-success = headroom remaining: 1.0 when far from ceiling, 0 when at it.
        headroom = max(0, max_reroutes - current_count)
        predicted_p = float(headroom) / max(1, max_reroutes) if max_reroutes > 0 else 1.0
        eu_score = float(headroom)

        handle = helper.record_decision(
            selected="allow" if allowed else "ceiling_exceeded",
            cell={"max_reroutes": int(max_reroutes)},
            predicted_p_success=predicted_p,
            eu_score=eu_score,
            decision_id=str(request_id) or None,  # uuid fallback if empty
            prediction_extras={
                "request_id": str(request_id),
                "current_count": int(current_count),
                "max_reroutes": int(max_reroutes),
            },
        )
        helper.bind_outcome(handle, success=bool(allowed))
    except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- ledger emission is best-effort; reroute ceiling must never break
        _REROUTE_LOGGER.debug("reroute_governance ledger emit failed", exc_info=True)


__all__ = [
    "JudgeDisagreementSummary",
    "ReplayCertResult",
    "RerouteCeiling",
    "RerouteCeilingExceededError",
    "evaluate_judge_disagreement",
    "judge_disagreement_rate",
    "replay_cert_blocks",
]
