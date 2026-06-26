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

from agentic_core.utils.runners.providers import (
    get_clock,
)  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency

if TYPE_CHECKING:
    from ops_scripts.reports.async_eval_packet import (
        AsyncEvalPacket,
        ShadowEvalPacket,
    )

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


__all__ = [
    "ShadowEvalResult",
    "ShadowEvalGrader",
    "OutcomeGrades",
    "TrajectoryGrades",
    "GovernanceRegressions",
    "ShadowGradeBundle",
    "ShadowPacketGrader",
    "bridge_to_shadow_eval_result",
]


# ---------------------------------------------------------------------------
# ShadowGradeBundle — multi-dimensional grading output for ShadowEvalPackets
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OutcomeGrades:
    """Outcome evaluation scores for a single ShadowEvalPacket.

    task_completion:   1.0 if terminal=SUCCESS, 0.0 otherwise.
    groundedness_score: Direct from quality_checks.
    citation_support:  support_coverage from quality_checks.
    abstain_correct:   Abstain decision matched expectation.
    escalation_correct: Escalation decision matched expectation.
    answer_relevance:  relevance_score from quality_checks.
    """

    task_completion: float = 0.0
    groundedness_score: float = 0.0
    citation_support: float = 0.0
    abstain_correct: bool = False
    escalation_correct: bool = False
    answer_relevance: float = 0.0


@dataclass(frozen=True)
class TrajectoryGrades:
    """Trajectory evaluation for a single ShadowEvalPacket.

    tool_selection_ok:   At least one exec_trace or answer_fit=True.
    arg_correctness:     schema_passed / (schema_passed + schema_failed) ratio.
    retry_thrash_ok:     retry_count < threshold (default 3).
    budget_ok:           budget_remaining > 0.
    policy_compliance:   rules_compliance_score.
    trajectory_integrity: replay_env_complete.
    """

    tool_selection_ok: bool = False
    arg_correctness: float = 1.0
    retry_thrash_ok: bool = True
    budget_ok: bool = True
    policy_compliance: float = 0.0
    trajectory_integrity: bool = False


@dataclass(frozen=True)
class GovernanceRegressions:
    """Governance regression flags for a single ShadowEvalPacket.

    exact_match_drift: schema_completion_score delta from baseline (negative = regression).
    schema_drift:      schema_checks_failed > 0.
    api_drift:         policy_hash changed vs baseline.
    rubric_drift:      policy_adherence_score shifted beyond threshold.
    gate_regression:   exit_disposition differs from baseline expected_disposition.
    """

    exact_match_drift: float = 0.0
    schema_drift: bool = False
    api_drift: bool = False
    rubric_drift: bool = False
    gate_regression: bool = False


@dataclass(frozen=True)
class ShadowGradeBundle:
    """Full multi-dimensional grading output for one ShadowEvalPacket.

    overall_grade values:
        "PASS" — no severity tags triggered
        "WARN" — minor issues (groundedness, drift, retry, budget)
        "FAIL" — critical issues (escalation missed, policy violation, gate regression)
    """

    packet_id: str
    run_id: str
    lane_id: str
    collection: str

    outcome_grades: OutcomeGrades
    trajectory_grades: TrajectoryGrades
    governance: GovernanceRegressions

    severity_tags: tuple[str, ...]
    normalized_score: float
    overall_grade: str
    grade_reasons: tuple[str, ...]
    graded_at: float


# ---------------------------------------------------------------------------
# Grading constants for ShadowPacketGrader
# ---------------------------------------------------------------------------

_RETRY_THRASH_THRESHOLD = 3
_RUBRIC_DRIFT_THRESHOLD = 0.15
_EXACT_MATCH_DRIFT_REGRESSION = -0.20

_FAIL_SEVERITY_TAGS = frozenset({"ESCALATION_MISSED", "POLICY_VIOLATION", "GATE_REGRESSION"})
_WARN_SEVERITY_TAGS = frozenset(
    {
        "TASK_INCOMPLETE",
        "ABSTAIN_MISSED",
        "GROUNDEDNESS_FAIL",
        "EXACT_MATCH_DRIFT",
        "SCHEMA_DRIFT",
        "API_DRIFT",
        "RUBRIC_DRIFT",
        "RETRY_THRASH",
        "BUDGET_EXHAUSTED",
        "TRAJECTORY_BROKEN",
    }
)


# ---------------------------------------------------------------------------
# ShadowPacketGrader — multi-dimensional grader for ShadowEvalPackets
# ---------------------------------------------------------------------------


class ShadowPacketGrader:
    """Grade ShadowEvalPackets across outcome, trajectory, and governance dimensions.

    Reads evaluation signals from packet.telemetry (populated by build_shadow_eval_packet).
    Future-run only.  No side effects.  No durable writes.
    """

    def grade(
        self,
        packet: "ShadowEvalPacket",
        baseline: dict[str, Any] | None = None,
    ) -> ShadowGradeBundle:
        """Grade one ShadowEvalPacket.

        Args:
            packet:   ShadowEvalPacket from build_shadow_eval_packet().
            baseline: Optional baseline dict for regression comparison.

        Returns:
            ShadowGradeBundle — sealed multi-dimensional grading output.
        """
        # Scope invariant: shadow grading is future-run only.
        if getattr(packet, "run_scope", None) != "FUTURE_RUN":
            raise ValueError(
                f"ShadowPacketGrader.grade: packet must have run_scope='FUTURE_RUN', "
                f"got {getattr(packet, 'run_scope', None)!r}"
            )
        telem = packet.telemetry
        reasons: list[str] = []
        severity_tags: list[str] = []

        outcome = _grade_outcomes(telem, reasons, severity_tags)
        trajectory = _grade_trajectory(telem, packet.exec_traces, reasons, severity_tags)
        governance = _grade_governance(telem, packet.exit_disposition, baseline, reasons, severity_tags)

        normalized = _compute_normalized_score(outcome, trajectory, governance)
        overall = _compute_overall_grade(severity_tags)

        return ShadowGradeBundle(
            packet_id=packet.packet_id,
            run_id=packet.run_id,
            lane_id=_extract_lane_id(packet),
            collection=_extract_collection(packet),
            outcome_grades=outcome,
            trajectory_grades=trajectory,
            governance=governance,
            severity_tags=tuple(severity_tags),
            normalized_score=round(normalized, 4),
            overall_grade=overall,
            grade_reasons=tuple(reasons),
            graded_at=get_clock().now_epoch(),
        )


def _grade_outcomes(
    telem: dict[str, Any],
    reasons: list[str],
    severity_tags: list[str],
) -> OutcomeGrades:
    terminal = telem.get("terminal_classification", "SUCCESS")
    task_completion = 1.0 if terminal == "SUCCESS" else 0.0
    if task_completion < 0.5:
        reasons.append(f"TASK_INCOMPLETE: terminal_classification={terminal}")
        severity_tags.append("TASK_INCOMPLETE")

    groundedness_score = float(telem.get("groundedness_score", 0.0))
    if groundedness_score < _ABSTAIN_THRESHOLD:
        reasons.append(f"GROUNDEDNESS_FAIL: score={groundedness_score:.3f}")
        severity_tags.append("GROUNDEDNESS_FAIL")

    citation_support = float(telem.get("support_coverage", 0.0))
    if citation_support < _CITATION_THRESHOLD:
        reasons.append(f"CITATION_BELOW_THRESHOLD: coverage={citation_support:.3f}")

    abstain_correct = bool(telem.get("abstain_correct", True))
    if not abstain_correct:
        reasons.append("ABSTAIN_MISMATCH: abstain_correct=False")
        severity_tags.append("ABSTAIN_MISSED")

    escalation_correct = bool(telem.get("escalation_correct", True))
    if not escalation_correct:
        reasons.append("ESCALATION_MISMATCH: escalation_correct=False")
        severity_tags.append("ESCALATION_MISSED")

    answer_relevance = float(telem.get("relevance_score", 0.0))

    return OutcomeGrades(
        task_completion=task_completion,
        groundedness_score=groundedness_score,
        citation_support=citation_support,
        abstain_correct=abstain_correct,
        escalation_correct=escalation_correct,
        answer_relevance=answer_relevance,
    )


def _grade_trajectory(
    telem: dict[str, Any],
    exec_traces: tuple[dict[str, Any], ...],
    reasons: list[str],
    severity_tags: list[str],
) -> TrajectoryGrades:
    tool_selection_ok = len(exec_traces) > 0 or bool(telem.get("answer_fit", False))
    if not tool_selection_ok:
        reasons.append("TOOL_SELECTION_MISSING: no exec_traces and answer_fit=False")

    schema_passed = int(telem.get("schema_checks_passed", 0))
    schema_failed = int(telem.get("schema_checks_failed", 0))
    total_schema = schema_passed + schema_failed
    arg_correctness = (schema_passed / total_schema) if total_schema > 0 else 1.0
    if schema_failed > 0:
        reasons.append(f"SCHEMA_FAILURES: failed={schema_failed} passed={schema_passed}")

    retry_count = int(telem.get("retry_count", 0))
    retry_thrash_ok = retry_count < _RETRY_THRASH_THRESHOLD
    if not retry_thrash_ok:
        reasons.append(f"RETRY_THRASH: retry_count={retry_count}")
        severity_tags.append("RETRY_THRASH")

    budget_remaining = float(telem.get("budget_remaining", 1.0))
    budget_ok = budget_remaining > 0.0
    if not budget_ok:
        reasons.append("BUDGET_EXHAUSTED: budget_remaining=0.0")
        severity_tags.append("BUDGET_EXHAUSTED")

    policy_compliance = float(telem.get("rules_compliance_score", 0.0))
    if policy_compliance < 0.5:
        reasons.append(f"POLICY_VIOLATION: compliance={policy_compliance:.3f}")
        severity_tags.append("POLICY_VIOLATION")

    trajectory_integrity = bool(telem.get("replay_env_complete", False))
    if not trajectory_integrity:
        reasons.append("TRAJECTORY_INTEGRITY: replay_env_complete=False")
        severity_tags.append("TRAJECTORY_BROKEN")

    return TrajectoryGrades(
        tool_selection_ok=tool_selection_ok,
        arg_correctness=arg_correctness,
        retry_thrash_ok=retry_thrash_ok,
        budget_ok=budget_ok,
        policy_compliance=policy_compliance,
        trajectory_integrity=trajectory_integrity,
    )


def _grade_governance(
    telem: dict[str, Any],
    exit_disposition: str,
    baseline: dict[str, Any] | None,
    reasons: list[str],
    severity_tags: list[str],
) -> GovernanceRegressions:
    bl = baseline or {}

    current_schema_score = float(telem.get("schema_completion_score", 0.0))
    baseline_schema = float(bl.get("exact_match_baseline_ratio", current_schema_score))
    exact_match_drift = round(current_schema_score - baseline_schema, 4)
    if exact_match_drift < _EXACT_MATCH_DRIFT_REGRESSION:
        reasons.append(f"EXACT_MATCH_DRIFT: {exact_match_drift:+.3f} vs baseline={baseline_schema:.3f}")
        severity_tags.append("EXACT_MATCH_DRIFT")

    schema_drift = int(telem.get("schema_checks_failed", 0)) > 0
    if schema_drift:
        reasons.append("SCHEMA_DRIFT: schema_checks_failed > 0")
        severity_tags.append("SCHEMA_DRIFT")

    current_policy_hash = telem.get("policy_hash", "")
    baseline_policy_hash = bl.get("policy_hash", current_policy_hash)
    api_drift = bool(current_policy_hash and current_policy_hash != baseline_policy_hash)
    if api_drift:
        reasons.append("API_DRIFT: policy_hash changed from baseline")
        severity_tags.append("API_DRIFT")

    current_adherence = float(telem.get("policy_adherence_score", 1.0))
    baseline_adherence = float(bl.get("policy_adherence_baseline", current_adherence))
    rubric_drift = abs(current_adherence - baseline_adherence) > _RUBRIC_DRIFT_THRESHOLD
    if rubric_drift:
        reasons.append(f"RUBRIC_DRIFT: adherence={current_adherence:.3f} baseline={baseline_adherence:.3f}")
        severity_tags.append("RUBRIC_DRIFT")

    baseline_disposition = bl.get("expected_disposition", "")
    gate_regression = bool(
        exit_disposition and baseline_disposition and exit_disposition != baseline_disposition
    )
    if gate_regression:
        reasons.append(f"GATE_REGRESSION: disposition={exit_disposition!r} expected={baseline_disposition!r}")
        severity_tags.append("GATE_REGRESSION")

    return GovernanceRegressions(
        exact_match_drift=exact_match_drift,
        schema_drift=schema_drift,
        api_drift=api_drift,
        rubric_drift=rubric_drift,
        gate_regression=gate_regression,
    )


def _compute_normalized_score(
    outcome: OutcomeGrades,
    trajectory: TrajectoryGrades,
    governance: GovernanceRegressions,
) -> float:
    """Weighted composite of outcome (35%), trajectory (40%), governance (25%)."""
    outcome_composite = (
        outcome.task_completion
        + outcome.groundedness_score
        + outcome.citation_support
        + float(outcome.abstain_correct)
        + float(outcome.escalation_correct)
        + outcome.answer_relevance
    ) / 6.0

    trajectory_composite = (
        float(trajectory.tool_selection_ok)
        + trajectory.arg_correctness
        + float(trajectory.retry_thrash_ok)
        + float(trajectory.budget_ok)
        + trajectory.policy_compliance
        + float(trajectory.trajectory_integrity)
    ) / 6.0

    regression_penalty = (
        float(governance.schema_drift)
        + float(governance.api_drift)
        + float(governance.rubric_drift)
        + float(governance.gate_regression)
        + max(0.0, -governance.exact_match_drift)
    ) / 5.0
    governance_composite = max(0.0, 1.0 - regression_penalty)

    return min(
        1.0,
        max(0.0, 0.35 * outcome_composite + 0.40 * trajectory_composite + 0.25 * governance_composite),
    )


def _compute_overall_grade(severity_tags: list[str]) -> str:
    tag_set = frozenset(severity_tags)
    if tag_set & _FAIL_SEVERITY_TAGS:
        return "FAIL"
    if tag_set & _WARN_SEVERITY_TAGS:
        return "WARN"
    return "PASS"


def _extract_lane_id(packet: "ShadowEvalPacket") -> str:
    if packet.exec_traces:
        trace = packet.exec_traces[0]
        return trace.get("lane_id", "") or trace.get("actor", "") or packet.run_id
    return packet.run_id


def _extract_collection(packet: "ShadowEvalPacket") -> str:
    return str(packet.telemetry.get("collection", "") or "")


# ---------------------------------------------------------------------------
# Bridge — ShadowGradeBundle → ShadowEvalResult for RcaAggregator ingestion
# ---------------------------------------------------------------------------


def bridge_to_shadow_eval_result(bundle: ShadowGradeBundle) -> ShadowEvalResult:
    """Convert a ShadowGradeBundle to a ShadowEvalResult for RcaAggregator ingestion.

    Allows ShadowPacketGrader output to flow through the existing aggregation pipeline
    without modifying RcaAggregator.
    """
    primary_tag = bundle.severity_tags[0] if bundle.severity_tags else ""

    return ShadowEvalResult(
        packet_id=bundle.packet_id,
        run_id=bundle.run_id,
        lane_id=bundle.lane_id,
        collection=bundle.collection,
        support_coverage=bundle.outcome_grades.citation_support,
        citation_completeness=bundle.outcome_grades.groundedness_score,
        exact_match_ratio=max(0.0, 1.0 + bundle.governance.exact_match_drift),
        exit_disposition="",
        weak_support_disposition="",
        groundedness_ok=bundle.outcome_grades.groundedness_score >= _ABSTAIN_THRESHOLD,
        abstain_correct=bundle.outcome_grades.abstain_correct,
        escalation_correct=bundle.outcome_grades.escalation_correct,
        weak_support_correct=not any(
            t in bundle.severity_tags for t in ("ABSTAIN_MISSED", "ESCALATION_MISSED")
        ),
        exact_match_drift=bundle.governance.exact_match_drift,
        baseline_ratio_used=0.0,
        lane_regression_tag=primary_tag,
        overall_grade=bundle.overall_grade,
        grade_reasons=bundle.grade_reasons,
        graded_at=bundle.graded_at,
    )
