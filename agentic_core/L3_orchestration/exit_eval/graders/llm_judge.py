"""Model-based (LLM-as-judge) grader.

Per grader_composition_spec §5:

- Every model-based dimension MUST support the abstain protocol (``UNKNOWN``
  return).
- Judges run in a context isolated from the agent's tool outputs (H2.1).
- Judge output is bundled with calibration metadata so drift can be
  detected downstream.

This module defines the ``JudgeProtocol`` interface. Concrete judge
implementations (which make actual LLM calls) live outside this framework;
they can be injected at wiring time. A fake judge is used in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, runtime_checkable

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import (
    Grader,
    GraderError,
    GraderOutput,
)


@dataclass(frozen=True)
class JudgeResponse:
    """Structured judge response.

    ``abstain=True`` means the judge explicitly returned UNKNOWN per the
    rubric prompt's abstain clause. ``abstain=False`` means the judge
    committed to a score.
    """

    score: float
    abstain: bool
    reasoning: str = ""


@runtime_checkable
class JudgeProtocol(Protocol):
    """Interface for concrete LLM-judge implementations.

    The protocol accepts the dimension being graded plus a sanitized
    context (agent output + reference + rubric instructions) and returns a
    structured response. Implementations MUST enforce §6.2 input sanitation
    (agent content wrapped in delimiters and labeled as data, not
    commands).

    Implementations MUST time-bound their calls — a judge timeout routes
    the run to HITL with ``JUDGE_TIMEOUT`` (H8), not to a silent pass.
    """

    def judge(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> JudgeResponse: ...


class LLMJudgeGrader(Grader):
    """Adapter wrapping a ``JudgeProtocol`` as a ``Grader``.

    Translates ``JudgeResponse`` to ``GraderOutput`` and enforces the
    abstain contract: a judge abstaining on a dimension that does not
    allow abstain is a hard wiring bug (raises ``GraderError`` at score
    translation time — see ``Grader.score_to_result``).

    By H2.1, if the injected ``JudgeProtocol`` is itself agentic (uses
    tools), the caller is responsible for enforcing the §H2 controls; this
    adapter does not inspect the judge's internals.
    """

    grader_class = GraderClass.MODEL_BASED

    def __init__(self, judge: JudgeProtocol) -> None:
        if not isinstance(judge, JudgeProtocol):
            # Treat non-conforming judges as hard wiring error, not silent fallback.
            raise GraderError("LLMJudgeGrader requires an object implementing JudgeProtocol")
        self._judge = judge

    def grade(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> GraderOutput:
        if dimension.grader_class is not GraderClass.MODEL_BASED:
            raise GraderError(
                f"LLMJudgeGrader on {dimension.name}: "
                f"dimension is {dimension.grader_class.value}, expected MODEL_BASED"
            )
        try:
            response = self._judge.judge(dimension, context)
        except (TimeoutError, GraderError):
            # TimeoutError is the canonical judge-timeout path; re-raise as
            # GraderError so the gate layer classifies it as JUDGE_TIMEOUT.
            raise
        except Exception as exc:  # guardian: allow-broad -- wrap any judge-side failure as GraderError for fail-closed routing
            raise GraderError(
                f"LLMJudgeGrader on {dimension.name}: judge raised {type(exc).__name__}: {exc}"
            ) from exc

        return GraderOutput(
            score=float(response.score),
            abstain=bool(response.abstain),
            evidence={"reasoning": response.reasoning},
        )


__all__ = ["JudgeProtocol", "JudgeResponse", "LLMJudgeGrader"]
