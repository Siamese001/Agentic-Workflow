"""
agentic_core/L6_observability/utils/evaluation/shadow_eval_grader.py

Shadow evaluation grader — grades AsyncEvalPackets against evidence governance rules.

Grades at minimum:
  - groundedness / citation support
  - abstain correctness
  - escalation correctness
  - weak-support disposition correctness
  - exact-match drift / regression signals
  - lane-level regression tags

Reuses the same threshold constants as evidence_eval_bridge.py.
Future-run only.  Read-only.  No durable writes.  No L4 access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agentic_core.L2_execution.utils.providers import get_clock

if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.async_eval_packet import AsyncEvalPacket

# Mirror of evidence_eval_bridge.py constants — must stay in sync with baseline JSON
_ABSTAIN_THRESHOLD = 0.30
_REFINE_THRESHOLD = 0.60
_CITATION_THRESHOLD = 0.50


@dataclass(frozen=True)
class ShadowEvalResult:
    """Grading output for one AsyncEvalPacket.

    overall_grade values:
        "PASS"  — all governance rules satisfied
        "WARN"  — abstain correctness or groundedness issue (non-critical)
        "FAIL"  — weak-support disposition wrong or escalation missed
    """

    packet_id: str
    run_id: str
    lane_id: str
    collection: str

    support_coverage: float
    citation_completeness: float
    exact_match_ratio: float
    exit_disposition: str
    weak_support_disposition: str

    groundedness_ok: bool
    abstain_correct: bool
    escalation_correct: bool
    weak_support_correct: bool

    exact_match_drift: float
    baseline_ratio_used: float

    lane_regression_tag: str
    overall_grade: str
    grade_reasons: tuple[str, ...]
    graded_at: float


class ShadowEvalGrader:
    """Grade AsyncEvalPackets against evidence governance rules.

    No side effects.  No durable writes.  Future-run only.
    """

    def grade(
        self,
        packet: "AsyncEvalPacket",
        baseline: dict[str, Any] | None = None,
    ) -> ShadowEvalResult:
        """Grade one packet.

        Args:
            packet:   AsyncEvalPacket to grade.
            baseline: Loaded evidence_governance_baseline.json (optional).

        Returns:
            ShadowEvalResult — sealed grading output.
        """
        reasons: list[str] = []

        # 1. Groundedness
        groundedness_ok = packet.grounded_replayable and packet.support_coverage >= _ABSTAIN_THRESHOLD
        if not groundedness_ok:
            reasons.append(
                f"GROUNDEDNESS_FAIL: grounded_replayable={packet.grounded_replayable}"
                f" coverage={packet.support_coverage:.3f}"
            )

        # 2. Abstain correctness
        should_abstain = not packet.grounded_replayable or packet.support_coverage < _ABSTAIN_THRESHOLD
        abstain_correct = (should_abstain and packet.weak_support_disposition == "abstain") or (
            not should_abstain and packet.weak_support_disposition != "abstain"
        )
        if not abstain_correct:
            reasons.append(
                f"ABSTAIN_MISMATCH: should_abstain={should_abstain} got={packet.weak_support_disposition}"
            )

        # 3. Escalation correctness
        should_escalate = packet.contradiction_present
        escalation_correct = (should_escalate and packet.weak_support_disposition == "escalate") or (
            not should_escalate and packet.weak_support_disposition != "escalate"
        )
        if not escalation_correct:
            reasons.append(
                f"ESCALATION_MISMATCH: contradiction={packet.contradiction_present}"
                f" got={packet.weak_support_disposition}"
            )

        # 4. Full weak-support disposition correctness
        expected = _expected_disposition(packet)
        weak_support_correct = packet.weak_support_disposition == expected
        if not weak_support_correct:
            reasons.append(f"WEAK_SUPPORT_WRONG: expected={expected} got={packet.weak_support_disposition}")

        # 5. Exact-match drift against baseline
        thresholds = (baseline or {}).get("thresholds", {})
        baseline_ratio = float(thresholds.get("exact_match_baseline_ratio", 0.0))
        exact_match_drift = round(packet.exact_match_ratio - baseline_ratio, 4)
        if exact_match_drift < -0.20:  # only negative drift (drop) signals regression
            reasons.append(f"EXACT_MATCH_DRIFT: {exact_match_drift:+.3f} vs baseline={baseline_ratio:.3f}")

        # 6. Lane regression tag
        lane_regression_tag = _regression_tag(
            groundedness_ok,
            abstain_correct,
            escalation_correct,
            weak_support_correct,
            exact_match_drift,
        )

        # Overall grade
        if not weak_support_correct or not escalation_correct:
            overall_grade = "FAIL"
        elif not abstain_correct or not groundedness_ok:
            overall_grade = "WARN"
        elif exact_match_drift < -0.20:  # only a drop from baseline is a regression
            overall_grade = "WARN"
        else:
            overall_grade = "PASS"

        return ShadowEvalResult(
            packet_id=packet.packet_id,
            run_id=packet.run_id,
            lane_id=packet.lane_id,
            collection=packet.collection,
            support_coverage=packet.support_coverage,
            citation_completeness=packet.citation_completeness,
            exact_match_ratio=packet.exact_match_ratio,
            exit_disposition=packet.exit_disposition,
            weak_support_disposition=packet.weak_support_disposition,
            groundedness_ok=groundedness_ok,
            abstain_correct=abstain_correct,
            escalation_correct=escalation_correct,
            weak_support_correct=weak_support_correct,
            exact_match_drift=exact_match_drift,
            baseline_ratio_used=baseline_ratio,
            lane_regression_tag=lane_regression_tag,
            overall_grade=overall_grade,
            grade_reasons=tuple(reasons),
            graded_at=get_clock().now_epoch(),
        )


def _expected_disposition(packet: "AsyncEvalPacket") -> str:
    """Reimplements classify_evidence_support() logic for grading (avoids import cycle)."""
    if packet.contradiction_present:
        return "escalate"
    if not packet.grounded_replayable or packet.support_coverage < _ABSTAIN_THRESHOLD:
        return "abstain"
    if packet.support_coverage < _REFINE_THRESHOLD or packet.citation_completeness < _CITATION_THRESHOLD:
        return "refine"
    return "proceed"


def _regression_tag(
    groundedness_ok: bool,
    abstain_correct: bool,
    escalation_correct: bool,
    weak_support_correct: bool,
    drift: float,
) -> str:
    if not escalation_correct:
        return "ESCALATION_MISSED"
    if not abstain_correct:
        return "ABSTAIN_MISSED"
    if not weak_support_correct:
        return "WEAK_SUPPORT_WRONG"
    if not groundedness_ok:
        return "GROUNDEDNESS_FAIL"
    if drift < -0.20:  # only drops from baseline are regression tags
        return "EXACT_MATCH_DRIFT"
    return ""


__all__ = ["ShadowEvalResult", "ShadowEvalGrader"]
