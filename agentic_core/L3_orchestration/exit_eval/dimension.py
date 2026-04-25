"""Dimension and grader-class types.

A *dimension* is one scorable facet of a rubric (e.g. ``groundedness``,
``tool_selection_accuracy``). A *rubric* is a named collection of dimensions
owned by a single gate.

See ``grader_composition_spec.md`` §2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class GraderClass(str, Enum):
    """Anthropic's three-class grader taxonomy.

    ``CODE_BASED`` — deterministic functions; the only class permitted for
    hard sub-gates that carry safety invariants.

    ``MODEL_BASED`` — LLM-as-judge; MUST support ``abstain_allowed``.

    ``HUMAN`` — SME review; used for offline calibration only, never at
    runtime (runtime human intervention is HITL, a separate plane).
    """

    CODE_BASED = "code_based"
    MODEL_BASED = "model_based"
    HUMAN = "human"


@dataclass(frozen=True)
class Dimension:
    """One scorable rubric dimension.

    Attributes:
        name: Stable identifier within a rubric.
        grader_class: Which grader class scores this dimension.
        scale: (min, max) of the raw score before threshold comparison.
        weight: Contribution to weighted composition. Ignored for binary
            composition. Must be > 0 when composition uses weights.
        is_hard_gate: If True, dimension is a binary sub-gate — a score
            below ``threshold`` denies the run regardless of composition.
        threshold: Pass threshold for hard gates and for weighted-mode
            per-dimension reporting.
        abstain_allowed: Model-based only — permits UNKNOWN judge output
            routing the run to HITL with ``JUDGE_ABSTAINED`` rather than a
            false pass/fail. Hard constitutional requirement per v4 §X1D
            and grader_composition_spec §5.1.
    """

    name: str
    grader_class: GraderClass
    scale: tuple[float, float] = (0.0, 1.0)
    weight: float = 1.0
    is_hard_gate: bool = False
    threshold: float = 0.0
    abstain_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Dimension.name must be non-empty")
        if self.scale[0] >= self.scale[1]:
            raise ValueError(f"Dimension {self.name}: scale[0] must be < scale[1], got {self.scale}")
        if self.weight < 0:
            raise ValueError(f"Dimension {self.name}: weight must be >= 0")
        lo, hi = self.scale
        if not (lo <= self.threshold <= hi):
            raise ValueError(f"Dimension {self.name}: threshold {self.threshold} outside scale {self.scale}")
        if self.abstain_allowed and self.grader_class is not GraderClass.MODEL_BASED:
            # Abstain only meaningful for LLM judges; code graders either
            # succeed, fail, or raise. Humans don't grade at runtime.
            raise ValueError(f"Dimension {self.name}: abstain_allowed requires MODEL_BASED grader")


@dataclass(frozen=True)
class DimensionResult:
    """The scored outcome for one dimension on one run."""

    name: str
    score: float
    weight: float
    threshold: float
    passed: bool
    grader_class: GraderClass
    abstain: bool = False
    is_hard_gate: bool = False
    # Optional free-form evidence the grader produces for HITL packets.
    evidence: dict[str, object] = field(default_factory=dict)

    def to_bus_row(self) -> dict[str, object]:
        """Serialize for BUS P dimension_vector entries."""
        return {
            "name": self.name,
            "score": self.score,
            "weight": self.weight,
            "threshold": self.threshold,
            "passed": self.passed,
            "grader_class": self.grader_class.value,
            "abstain": self.abstain,
        }


__all__ = ["Dimension", "DimensionResult", "GraderClass"]
