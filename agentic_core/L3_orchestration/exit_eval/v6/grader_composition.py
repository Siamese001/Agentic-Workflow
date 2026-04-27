"""v6 grader composition primitives — Wave 3 of exit-eval-v6 deferred-scope.

Implements the runtime types from
``docs/reference/05_Exit_Evaluation_and_Control/grader_composition_spec.md``:

- §1 Grader taxonomy (code_based | model_based | human)
- §2 Rubric structure (named dimensions with grader_class, scale, weight,
  is_hard_gate, threshold, abstain_allowed)
- §3 Composition modes (binary AND, weighted average, hybrid)
- §4 Partial credit (dimension_vector preserved on disposition)
- §5.1 Abstain protocol (UNKNOWN routes to X3B with JUDGE_ABSTAINED)
- §7 BUS-P grader output contract

Out of scope for Wave 3 (deferred to subsequent waves):
- §5.2 SME calibration cadence (kappa tracking, drift detection) — needs
  data store + scheduler subsystem
- §5.4 Multi-judge consensus orchestration — needs N-judge runner
- §6 Bypass-resistance harness — needs context-isolation runtime + injection
  classifier
- §6.3 Adversarial eval set — content authoring task, not code

This module gives the runtime contract every grader and every gate that
references a rubric must conform to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GraderClass(str, Enum):
    """grader_composition_spec §1 — three grader classes."""

    CODE_BASED = "code_based"
    """Deterministic functions: schema validators, regex matchers, API-ref
    lookups, numeric tolerance. Returns binary or small-int. Reproducible."""

    MODEL_BASED = "model_based"
    """LLM-as-judge against a rubric. Returns continuous [0,1] + optional
    UNKNOWN abstain. Non-deterministic; needs human calibration."""

    HUMAN = "human"
    """SME review. Offline calibration only — never used at runtime gating."""


class CompositionMode(str, Enum):
    """grader_composition_spec §3 — three composition modes."""

    BINARY = "binary"
    """All dimensions must meet their thresholds (AND). Use for hard gates."""

    WEIGHTED = "weighted"
    """Weighted average must meet aggregate_threshold. Soft-quality gates."""

    HYBRID = "hybrid"
    """Hard gates AND + weighted-soft AND aggregate_threshold."""


# §3 table — composition mode per gate
GATE_COMPOSITION_MODE: dict[str, CompositionMode] = {
    "X1A": CompositionMode.BINARY,
    "X1B": CompositionMode.HYBRID,
    "X1C": CompositionMode.BINARY,
    "X1D": CompositionMode.WEIGHTED,
    "X1E": CompositionMode.HYBRID,
    "X1F": CompositionMode.HYBRID,
    "X1G": CompositionMode.BINARY,  # pass^k >= theta
}


@dataclass(slots=True)
class RubricDimension:
    """grader_composition_spec §2 — one named dimension within a rubric.

    A rubric is a list of dimensions, each scored by its OWN isolated grader
    instance (do not reuse a single LLM call across dimensions — see §2 rule
    "Each dimension is scored by its own isolated grader instance").
    """

    name: str
    grader_class: GraderClass
    weight: float = 1.0  # used in weighted/hybrid composition
    is_hard_gate: bool = False  # true => binary sub-gate; failure denies
    threshold: float = 0.0  # pass threshold for hard gates and hybrid
    scale_min: float = 0.0
    scale_max: float = 1.0
    abstain_allowed: bool = False  # only allowed on model_based dimensions

    def __post_init__(self) -> None:
        # Discipline: abstain_allowed is only meaningful for model-based
        # dimensions per §5.1.
        if self.abstain_allowed and self.grader_class is not GraderClass.MODEL_BASED:
            raise ValueError(
                f"RubricDimension {self.name!r}: abstain_allowed only valid "
                f"for model_based; got {self.grader_class.value}"
            )
        # §2: code-based dimensions return binary or small-int set; thresholds
        # in [0,1] are still meaningful (e.g. 1.0 for "must pass").
        if not self.scale_min < self.scale_max:
            raise ValueError(
                f"RubricDimension {self.name!r}: scale_min ({self.scale_min}) "
                f"must be < scale_max ({self.scale_max})"
            )


@dataclass(slots=True)
class Rubric:
    """grader_composition_spec §2 — full rubric for one gate.

    Versioned (`version` + `rubric_id`) so X1A can pin a specific rubric
    version per §6.4 immutable rubric versioning.
    """

    rubric_id: str  # e.g. "X1D@v3"
    gate: str  # X1A..X1J
    version: int
    composition: CompositionMode
    dimensions: list[RubricDimension] = field(default_factory=list)
    aggregate_threshold: float = 0.0  # used when composition != binary

    def __post_init__(self) -> None:
        if not self.dimensions:
            raise ValueError(f"Rubric {self.rubric_id!r}: must have >=1 dimension")
        if self.composition is not CompositionMode.BINARY:
            if not 0.0 <= self.aggregate_threshold <= 1.0:
                raise ValueError(
                    f"Rubric {self.rubric_id!r}: aggregate_threshold must be in "
                    f"[0,1] for non-binary composition; got {self.aggregate_threshold}"
                )
        # Hybrid composition requires at least one hard-gate dimension.
        if self.composition is CompositionMode.HYBRID:
            hard_gates = [d for d in self.dimensions if d.is_hard_gate]
            if not hard_gates:
                raise ValueError(
                    f"Rubric {self.rubric_id!r}: hybrid composition requires "
                    f">=1 dimension with is_hard_gate=True"
                )


@dataclass(slots=True)
class DimensionScore:
    """grader_composition_spec §4 — per-dimension score emitted to BUS-P.

    Preserved on partial-credit and HITL packets so reviewers see WHICH
    dimension failed (rather than only a top-line classification).
    """

    name: str
    grader_class: GraderClass
    score: float
    weight: float
    threshold: float
    passed: bool
    abstain: bool = False  # True only when grader returned UNKNOWN
    rationale: str = ""  # optional grader rationale (judge-emitted)


# Default reason code emitted on §5.1 abstain.
ABSTAIN_REASON_CODE: str = "JUDGE_ABSTAINED"


def _normalize(score: float, dim: RubricDimension) -> float:
    """Map a raw dimension score into the [0,1] normalized space.

    Handles non-[0,1] scale_min/scale_max ranges per §2.
    """
    if dim.scale_max == dim.scale_min:
        return 0.0
    if score <= dim.scale_min:
        return 0.0
    if score >= dim.scale_max:
        return 1.0
    return (score - dim.scale_min) / (dim.scale_max - dim.scale_min)


@dataclass(slots=True)
class CompositionResult:
    """Result of evaluating a Rubric against a list of DimensionScore.

    This is the canonical output gate code feeds into the X1 GateVerdict.
    """

    passed: bool
    aggregate_score: float
    aggregate_threshold: float
    composition: CompositionMode
    abstain: bool  # true if any dim abstained
    failed_dimension_names: list[str]
    abstained_dimension_names: list[str]
    dimension_vector: list[DimensionScore]
    reason_codes: list[str]


def compose(rubric: Rubric, scores: list[DimensionScore]) -> CompositionResult:
    """Apply ``rubric.composition`` to ``scores`` and return CompositionResult.

    grader_composition_spec §3:

    - BINARY: AND over dimensions; aggregate = min(normalized score, ...)
    - WEIGHTED: weighted average of normalized scores; check >= aggregate_threshold
    - HYBRID: hard_gates AND + weighted_avg(soft) >= aggregate_threshold

    Per §5.1: any abstaining dimension flips ``abstain=True`` on the result.
    The aggregate may still pass numerically; the abstain flag is the signal
    to route to X3B with JUDGE_ABSTAINED.

    Args:
        rubric: the rubric defining dimensions, weights, thresholds
        scores: per-dimension scores (must cover every rubric dimension)

    Returns:
        CompositionResult with passed/aggregate/abstain/failed-list

    Raises:
        ValueError: if scores don't cover all rubric dimensions
    """
    by_name = {s.name: s for s in scores}
    missing = [d.name for d in rubric.dimensions if d.name not in by_name]
    if missing:
        raise ValueError(
            f"compose: scores missing for dimensions {missing!r}"
        )

    failed: list[str] = []
    abstained: list[str] = []
    norm_scores: list[tuple[RubricDimension, DimensionScore, float]] = []
    for dim in rubric.dimensions:
        s = by_name[dim.name]
        n = _normalize(s.score, dim)
        norm_scores.append((dim, s, n))
        if s.abstain:
            abstained.append(dim.name)
        # Hard gates fail when individually below threshold (regardless of weight)
        if dim.is_hard_gate and not s.passed:
            failed.append(dim.name)

    abstain_flag = bool(abstained)
    reason_codes: list[str] = []
    if abstain_flag:
        reason_codes.append(ABSTAIN_REASON_CODE)

    if rubric.composition is CompositionMode.BINARY:
        # AND over all dimensions; any failure denies
        all_passed = all(s.passed for s in scores if s.name in by_name)
        aggregate = min((n for _, _, n in norm_scores), default=0.0)
        binary_failed = [s.name for s in scores if not s.passed]
        return CompositionResult(
            passed=all_passed and not abstain_flag,
            aggregate_score=aggregate,
            aggregate_threshold=1.0,  # binary: implicit threshold is 1.0 per dim
            composition=rubric.composition,
            abstain=abstain_flag,
            failed_dimension_names=binary_failed,
            abstained_dimension_names=abstained,
            dimension_vector=list(scores),
            reason_codes=reason_codes,
        )

    if rubric.composition is CompositionMode.WEIGHTED:
        total_weight = sum(d.weight for d in rubric.dimensions)
        if total_weight == 0:
            raise ValueError(
                f"Rubric {rubric.rubric_id!r}: total weight is 0 in weighted composition"
            )
        weighted_sum = sum(d.weight * n for d, _, n in norm_scores)
        aggregate = weighted_sum / total_weight
        soft_passed = aggregate >= rubric.aggregate_threshold
        return CompositionResult(
            passed=soft_passed and not abstain_flag,
            aggregate_score=aggregate,
            aggregate_threshold=rubric.aggregate_threshold,
            composition=rubric.composition,
            abstain=abstain_flag,
            failed_dimension_names=failed,  # may be empty in pure weighted
            abstained_dimension_names=abstained,
            dimension_vector=list(scores),
            reason_codes=reason_codes,
        )

    # HYBRID: hard_gates AND + weighted soft avg
    hard_dims = [d for d in rubric.dimensions if d.is_hard_gate]
    soft_dims = [d for d in rubric.dimensions if not d.is_hard_gate]
    hard_pass = all(by_name[d.name].passed for d in hard_dims)

    if soft_dims:
        soft_total = sum(d.weight for d in soft_dims)
        if soft_total == 0:
            raise ValueError(
                f"Rubric {rubric.rubric_id!r}: soft total weight is 0 in hybrid"
            )
        soft_norm = {
            d.name: n
            for d, _, n in norm_scores
            if d.name in {sd.name for sd in soft_dims}
        }
        soft_avg = sum(d.weight * soft_norm[d.name] for d in soft_dims) / soft_total
    else:
        soft_avg = 1.0  # no soft dims → soft side trivially passes

    soft_pass = soft_avg >= rubric.aggregate_threshold
    return CompositionResult(
        passed=hard_pass and soft_pass and not abstain_flag,
        aggregate_score=soft_avg,
        aggregate_threshold=rubric.aggregate_threshold,
        composition=rubric.composition,
        abstain=abstain_flag,
        failed_dimension_names=failed,
        abstained_dimension_names=abstained,
        dimension_vector=list(scores),
        reason_codes=reason_codes,
    )


@dataclass(slots=True)
class BusPRow:
    """grader_composition_spec §7 — BUS-P emission row per gate per run.

    One row per gate per run. Append-only (per the spec). Consumers:
    runtime_to_regression_dataset_flow Wave 4 candidate pool, calibration
    drift detection (§5.2 deferred), partial-credit dashboards (§4).
    """

    run_id: str
    gate: str
    rubric_version: str  # e.g. X1D@v3
    composition: str  # CompositionMode value
    aggregate_score: float
    aggregate_threshold: float
    passed: bool
    abstain: bool
    dimension_vector: list[dict[str, Any]] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    track: str = "production"
    trajectory_class: str = ""

    @classmethod
    def from_composition(
        cls,
        *,
        run_id: str,
        rubric: Rubric,
        result: CompositionResult,
        track: str = "production",
        trajectory_class: str = "",
    ) -> "BusPRow":
        """Build a BUS-P row from a CompositionResult."""
        return cls(
            run_id=run_id,
            gate=rubric.gate,
            rubric_version=rubric.rubric_id,
            composition=result.composition.value,
            aggregate_score=round(result.aggregate_score, 4),
            aggregate_threshold=round(result.aggregate_threshold, 4),
            passed=result.passed,
            abstain=result.abstain,
            dimension_vector=[
                {
                    "name": d.name,
                    "grader_class": d.grader_class.value,
                    "score": d.score,
                    "weight": d.weight,
                    "threshold": d.threshold,
                    "passed": d.passed,
                    "abstain": d.abstain,
                }
                for d in result.dimension_vector
            ],
            reason_codes=list(result.reason_codes),
            track=track,
            trajectory_class=trajectory_class,
        )


__all__ = [
    "ABSTAIN_REASON_CODE",
    "BusPRow",
    "CompositionMode",
    "CompositionResult",
    "DimensionScore",
    "GATE_COMPOSITION_MODE",
    "GraderClass",
    "Rubric",
    "RubricDimension",
    "compose",
]
