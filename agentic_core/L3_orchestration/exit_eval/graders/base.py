"""Grader base class and shared types.

A Grader takes the evaluation context for one dimension and produces a
``GraderOutput`` (score + abstain flag + evidence). Gates translate
``GraderOutput`` into ``DimensionResult`` by applying the dimension's
threshold.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    DimensionResult,
    GraderClass,
)


class GraderError(Exception):
    """Unrecoverable grader failure.

    By H8 fail-mode matrix, a code-based grader exception routes the gate
    to X3A (DENY) with ``GRADER_EXCEPTION`` — never silently passes.
    """


@dataclass(frozen=True)
class GraderOutput:
    """Raw grader output before threshold application."""

    score: float
    abstain: bool = False
    evidence: dict[str, Any] = field(default_factory=dict)


class Grader(ABC):
    """Abstract base for all graders.

    Implementations MUST declare their ``grader_class``. Hard gates MUST be
    graded by ``CODE_BASED`` graders only (enforced at gate wiring time).
    """

    grader_class: GraderClass

    @abstractmethod
    def grade(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> GraderOutput:
        """Produce a raw score for ``dimension`` under ``context``.

        Raises:
            GraderError: for deterministic failures. Callers fail-close.
        """

    def score_to_result(
        self,
        dimension: Dimension,
        output: GraderOutput,
    ) -> DimensionResult:
        """Translate raw output to a threshold-aware DimensionResult.

        Rules:

        - If output is ``abstain`` and dimension permits abstain, the
          result is ``passed=False`` with ``abstain=True``; callers must
          route to HITL with ``JUDGE_ABSTAINED``, not deny.
        - If output is ``abstain`` but dimension forbids abstain, this is
          a hard error — raise ``GraderError``. A grader that abstains on
          a non-abstainable dimension is a wiring bug.
        - Otherwise ``passed = output.score >= dimension.threshold``.
        """
        if output.abstain:
            if not dimension.abstain_allowed:
                raise GraderError(f"grader abstained on non-abstainable dimension {dimension.name!r}")
            return DimensionResult(
                name=dimension.name,
                score=output.score,
                weight=dimension.weight,
                threshold=dimension.threshold,
                passed=False,
                grader_class=dimension.grader_class,
                abstain=True,
                is_hard_gate=dimension.is_hard_gate,
                evidence=dict(output.evidence),
            )

        lo, hi = dimension.scale
        clamped = max(lo, min(hi, output.score))
        passed = clamped >= dimension.threshold
        return DimensionResult(
            name=dimension.name,
            score=clamped,
            weight=dimension.weight,
            threshold=dimension.threshold,
            passed=passed,
            grader_class=dimension.grader_class,
            abstain=False,
            is_hard_gate=dimension.is_hard_gate,
            evidence=dict(output.evidence),
        )


__all__ = ["Grader", "GraderError", "GraderOutput"]
