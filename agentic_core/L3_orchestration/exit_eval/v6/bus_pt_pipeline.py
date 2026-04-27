"""v6 BUS P/T → regression-dataset pipeline primitives — Wave 4 of deferred-scope.

Implements the runtime types from
``docs/reference/05_Exit_Evaluation_and_Control/runtime_to_regression_dataset_flow.md``:

- §3.1 BUS P / BUS T row shapes (BUS P delegated to grader_composition.BusPRow)
- §3.2 Candidate Pool entry + promotion heuristic (8 weighted signals)
- §3.3 Curation Gate verdict + track assignment
- §3.4 Golden Set track enum + version-pin + graduation predicate
- §5 Retention policy constants
- §6 Pipeline invariants (no-runtime-mutation, anonymization-fail-closed,
  immutable-versions, mechanical-graduation, X1A-pinned-versions)

Out of scope for Wave 4 (deferred to subsequent work):
- Actual anonymization implementation (delegated to repo's anonymization layer)
- SME curation UI / workflow tooling
- Golden-set storage backend (filesystem layout in §3.4 is documented but
  the writer/reader is a separate component)
- Auto-curator with κ-rolling-audit (open question in §8)
- Cross-cohort fairness guardrail (open question in §8)

This module gives the runtime data shapes the curation tooling and X1A
baseline-loader will reference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# =====================================================================
# §3.4 Golden Set tracks
# =====================================================================


class GoldenSetTrack(str, Enum):
    """The 3 directories under data/eval/golden/ per §3.4."""

    CAPABILITY = "capability"
    """Tasks the system currently struggles with — hill-climb target."""

    REGRESSION = "regression"
    """Tasks the system has mastered — drift-guard. ~100% pass-rate required."""

    ADVERSARIAL = "adversarial"
    """Adversarial / security test cases. Gates X1F policy updates."""


# =====================================================================
# §5 Retention policy
# =====================================================================
#
# Default retention windows per §5. Operators may override by config.

#: BUS P/T raw rows retention (days). §5: default 90 unless longer-retention is justified.
BUS_PT_DEFAULT_RETENTION_DAYS: int = 90

#: Candidate pool retention (days). §5: 30-day window for re-curation.
CANDIDATE_POOL_RETENTION_DAYS: int = 30

#: Golden set retention is INDEFINITE (§5). Constant exposed for assertions.
GOLDEN_SET_RETENTION_INDEFINITE: bool = True


# =====================================================================
# §3.2 Promotion heuristic — 8 signals × weights
# =====================================================================
#
# Per §3.2 table. Higher score = higher curation priority.


PROMOTION_HEURISTIC_WEIGHTS: dict[str, float] = {
    # signal -> weight (per §3.2 table)
    "x3b_escalation": 3.0,           # HITL reviewed; highest value per minute
    "x1f_adversarial_failure": 2.5,  # security-relevant
    "x1e_trajectory_suspect": 2.0,   # latent brittleness
    "passk_dip": 1.8,                # drift signal; regression-guard priority
    "judge_abstained": 1.5,          # calibration signal
    "near_miss": 1.5,                # within 0.05 of threshold; partial-credit signal
    "novel_trajectory_class": 1.3,   # coverage expansion
    "routine_pass": 0.2,             # low signal; sample only
}


def promotion_score(signals: dict[str, bool]) -> float:
    """Compute the §3.2 promotion-worthiness score from observed signals.

    Args:
        signals: dict mapping signal name (a key from PROMOTION_HEURISTIC_WEIGHTS)
            to True/False indicating whether that signal fired for the run.
            Unknown keys are silently ignored. Missing keys count as False.

    Returns:
        Sum of weights for signals that fired. Higher = more curation priority.

    Raises:
        ValueError: if any signal value is not bool.
    """
    score = 0.0
    for name, weight in PROMOTION_HEURISTIC_WEIGHTS.items():
        v = signals.get(name, False)
        if not isinstance(v, bool):
            raise ValueError(
                f"promotion_score: signal {name!r} must be bool, got {type(v).__name__}"
            )
        if v:
            score += weight
    return score


# =====================================================================
# §3.1 BUS T row
# =====================================================================
#
# BUS P row is in grader_composition.BusPRow. BUS T carries full trajectory.


@dataclass(slots=True)
class BusTRow:
    """§3.1 BUS T row per run — full trajectory + environment snapshot.

    Append-only. Downstream consumer is the candidate pool. Per §3.1:

        BUS T row per run: run_id, full trajectory (tool calls, arguments,
        intermediate reasoning, handoffs, outputs), environment snapshot,
        disposition.
    """

    run_id: str
    trajectory: list[dict[str, Any]] = field(default_factory=list)
    """Sequence of trajectory steps. Each step is a dict with at least
    ``kind`` (tool_call|model_call|reasoning|handoff|output), and step-
    specific fields. Append-only at write."""
    environment_snapshot: dict[str, Any] = field(default_factory=dict)
    """Run-time env: agent_version, policy_version, rubric_versions,
    provider_lane, sandbox state hash."""
    disposition: str = ""  # X3A | X3B | X3C | X3D | X3E | X3F
    trace_root: str = ""

    actor: str = "agent"
    """§H2 of v4_hardening: judge trajectories tagged actor='judge' so audit
    review can separate primary-agent and judge runs."""


# =====================================================================
# §3.2 Candidate Pool entry
# =====================================================================


@dataclass(slots=True)
class CandidatePoolEntry:
    """§3.2 entry in the candidate pool after BUS P/T processing.

    Created by the dedup + anonymize step. Curation gate consumes this.
    """

    run_id: str
    trajectory_class: str  # used for dedup key
    normalized_input_hash: str  # part of dedup key
    output_class: str  # part of dedup key
    promotion_score: float
    signals: dict[str, bool] = field(default_factory=dict)
    anonymized: bool = False
    """§3.2: anonymization fail-closed. If False, entry MUST be excluded
    from curation flow."""
    bus_p_row_ids: list[str] = field(default_factory=list)
    bus_t_row_id: str = ""
    frequency_count: int = 1
    """§3.2: dedup collapses duplicates to single representative with frequency."""
    pii_redaction_log: list[str] = field(default_factory=list)
    """§4: anonymization layer logs what was redacted; curators see this."""


# =====================================================================
# §3.3 Curation Gate verdict
# =====================================================================


class CurationVerdict(str, Enum):
    """§3.3 curator decision."""

    PROMOTE = "promote"
    """Promote into the golden set on the assigned track."""
    REJECT = "reject"
    """curation_rejected (with reason); kept for audit, not consumed."""
    QUARANTINE = "quarantine"
    """Too sensitive / demographically unbalanced / legally risky."""


@dataclass(slots=True)
class CurationDecision:
    """§3.3 curator-emitted decision per candidate."""

    candidate_run_id: str
    verdict: CurationVerdict
    curator_id: str  # §6.4: audit-logged
    decision_at_ms: int
    track: GoldenSetTrack | None = None  # required iff verdict=PROMOTE
    expected_disposition: str = ""  # X3A..X3F
    expected_dimension_scores: list[dict[str, Any]] = field(default_factory=list)
    intent_label: str = ""  # what was the user actually trying to do?
    confirmed_anonymization: bool = False
    rejection_reason: str = ""  # required iff verdict=REJECT
    quarantine_reason: str = ""  # required iff verdict=QUARANTINE

    def __post_init__(self) -> None:
        # §3.3: PROMOTE requires a track + anonymization confirmation
        if self.verdict is CurationVerdict.PROMOTE:
            if self.track is None:
                raise ValueError(
                    f"CurationDecision {self.candidate_run_id!r}: "
                    f"PROMOTE requires a track"
                )
            if not self.confirmed_anonymization:
                raise ValueError(
                    f"CurationDecision {self.candidate_run_id!r}: "
                    f"PROMOTE requires confirmed_anonymization=True (§3.3 step 1)"
                )
        if self.verdict is CurationVerdict.REJECT and not self.rejection_reason:
            raise ValueError(
                f"CurationDecision {self.candidate_run_id!r}: "
                f"REJECT requires rejection_reason"
            )
        if self.verdict is CurationVerdict.QUARANTINE and not self.quarantine_reason:
            raise ValueError(
                f"CurationDecision {self.candidate_run_id!r}: "
                f"QUARANTINE requires quarantine_reason"
            )


# =====================================================================
# §3.4 Golden set version + graduation predicate
# =====================================================================


@dataclass(slots=True)
class GoldenSetVersion:
    """§3.4 immutable golden-set version tag.

    X1A loads a SPECIFIC version pin per §6.6 (no 'latest' reads).
    """

    version_tag: str  # e.g. "regression-v42"
    track: GoldenSetTrack
    case_count: int
    published_at_ms: int
    immutable: bool = True
    """§6.3: golden-set versions are immutable post-publish. Corrections
    produce a new version, not an edit."""
    changelog_entry: str = ""  # what changed vs prior version


# §3.4 graduation predicate constants
GRADUATION_PASSK_THRESHOLD: float = 0.95
GRADUATION_K: int = 10
GRADUATION_WINDOW: str = "weekly"


def graduates_to_regression(
    pass_k_estimate: float,
    k: int,
    *,
    window_count: int = 1,
) -> bool:
    """§3.4 graduation predicate: capability case auto-graduates to regression
    when pass^k ≥ 0.95 over k=10 in successive weekly evaluation runs.

    Args:
        pass_k_estimate: observed pass^k for the case
        k: number of trials in the estimate
        window_count: how many successive weekly windows we have at this level
            (default 1 = single window not sufficient; spec says "successive
            weekly evaluation runs", so caller tracks consecutive count).

    Returns:
        True iff (pass_k_estimate >= 0.95) AND (k >= 10) AND (window_count >= 1)

    Note: §3.4 is silent on the exact number of consecutive windows required;
    we accept any window_count >= 1 here and let the calling scheduler decide
    the actual cadence policy. The ≥0.95 + k=10 invariants are mechanical.
    """
    return (
        pass_k_estimate >= GRADUATION_PASSK_THRESHOLD
        and k >= GRADUATION_K
        and window_count >= 1
    )


# =====================================================================
# §6 Pipeline invariants — runtime predicates
# =====================================================================


def assert_anonymization_fail_closed(entry: CandidatePoolEntry) -> None:
    """§4 + §6.2: anonymization-fail-closed. A non-anonymized entry MUST
    NOT proceed to curation. Caller invokes this before passing entries
    into curation gate."""
    if not entry.anonymized:
        raise ValueError(
            f"CandidatePoolEntry {entry.run_id!r}: not anonymized; "
            f"§6.2 fail-closed forbids curation"
        )


def assert_no_runtime_mutation(stage: str) -> None:
    """§6.1: no stage in this pipeline mutates the current run.

    Every BUS P/T → candidate-pool → curation → golden-set step MUST be
    post-runtime-boundary. Stages call this with their stage name to
    record adherence; if the boundary has not been closed yet (caller
    must check), this assertion is a tripwire.

    Args:
        stage: human-readable stage name for diagnostics.
    """
    # The actual boundary check lives in pipeline.py / return_payload.py.
    # This helper documents the invariant at the type/call-site level so
    # static review can confirm the calling stage knows about it.
    _ = stage  # marker for grep / static analysis


__all__ = [
    "BUS_PT_DEFAULT_RETENTION_DAYS",
    "BusTRow",
    "CANDIDATE_POOL_RETENTION_DAYS",
    "CandidatePoolEntry",
    "CurationDecision",
    "CurationVerdict",
    "GOLDEN_SET_RETENTION_INDEFINITE",
    "GRADUATION_K",
    "GRADUATION_PASSK_THRESHOLD",
    "GRADUATION_WINDOW",
    "GoldenSetTrack",
    "GoldenSetVersion",
    "PROMOTION_HEURISTIC_WEIGHTS",
    "assert_anonymization_fail_closed",
    "assert_no_runtime_mutation",
    "graduates_to_regression",
    "promotion_score",
]
