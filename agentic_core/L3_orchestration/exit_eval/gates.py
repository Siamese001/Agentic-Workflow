"""Gate — bind a rubric to graders and evaluate one run.

A Gate is the runtime unit that scores one run against one rubric. Given
per-dimension graders and a context, it produces:

- A ``GateResult`` carrying aggregate + per-dimension results.
- A stream of reason codes (empty if the gate passed).
- A BUS P row ready for emission.

Gates DO NOT dispatch (X3A/B/C/D/E); they only evaluate. The pipeline
collects gate results and produces the final disposition envelope.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from agentic_core.L3_orchestration.exit_eval.bus import BusRow
from agentic_core.L3_orchestration.exit_eval.composition import (
    AggregateResult,
    CompositionMode,
    compose,
)
from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    DimensionResult,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.disposition import ReasonCode
from agentic_core.L3_orchestration.exit_eval.graders.base import (
    Grader,
    GraderError,
)
from agentic_core.L3_orchestration.exit_eval.rubric import Rubric


class GateWiringError(ValueError):
    """Raised when a gate is constructed with an invalid grader mapping."""


@dataclass(frozen=True)
class GateContext:
    """Evaluation context passed to graders.

    Graders may read any key; unknown keys are ignored. The wrapper is
    immutable so graders cannot mutate peer context.
    """

    run_id: str
    track: str
    trajectory_class: str
    payload: Mapping[str, Any]

    def for_dimension(self, dimension: Dimension) -> Mapping[str, Any]:
        """Return the payload. Subclasses may override to restrict per-dim."""
        return self.payload


@dataclass(frozen=True)
class GateResult:
    """Outcome of one gate on one run."""

    gate: str
    rubric_version: str
    composition: CompositionMode
    aggregate: AggregateResult
    dimension_results: tuple[DimensionResult, ...]
    reason_codes: tuple[ReasonCode, ...]
    # Any dimension-level exception (H8) is surfaced; gate passed=False.
    error: str | None = None

    @property
    def passed(self) -> bool:
        return self.aggregate.passed and self.error is None

    @property
    def abstained(self) -> bool:
        return any(d.abstain for d in self.dimension_results)

    def to_bus_row(
        self,
        *,
        run_id: str,
        track: str,
        trajectory_class: str,
        extras: dict[str, Any] | None = None,
    ) -> BusRow:
        return BusRow(
            run_id=run_id,
            gate=self.gate,
            rubric_version=self.rubric_version,
            composition=self.composition.value,
            aggregate_score=self.aggregate.aggregate_score,
            aggregate_threshold=self.aggregate.aggregate_threshold,
            passed=self.passed,
            abstain=self.abstained,
            dimension_vector=tuple(d.to_bus_row() for d in self.dimension_results),
            reason_codes=tuple(rc.value for rc in self.reason_codes),
            track=track,
            trajectory_class=trajectory_class,
            extras=dict(extras or {}),
        )


# Mapping of reason codes per gate for dimension-level failures. Kept in
# one place so dimension names stay consistent with v4 §Failure reason
# codes.
_DIMENSION_REASON_MAP: dict[str, dict[str, ReasonCode]] = {
    "X1A": {"policy_match": ReasonCode.POLICY_CONFLICT},
    "X1B": {
        "schema_complete": ReasonCode.SCHEMA_VIOLATION,
        "format_fit": ReasonCode.FORMAT_MISMATCH,
        "instruction_following_sys_over_user": ReasonCode.INSTRUCTION_BYPASS,
    },
    "X1C": {
        "sandbox_ok": ReasonCode.SANDBOX_BREACH,
        "mutation_authorized": ReasonCode.UNAUTHORIZED_MUTATION,
        "env_clean": ReasonCode.ENV_CONTAMINATED,
        "no_prior_trial_leakage": ReasonCode.TRIAL_STATE_LEAK,
    },
    "X1D": {
        "groundedness": ReasonCode.UNGROUNDED,
        "citation_support": ReasonCode.CITATION_INVALID,
        "faithfulness": ReasonCode.LOW_FAITHFULNESS,
    },
    "X1E": {
        "tool_selection_accuracy": ReasonCode.WRONG_TOOL,
        "arg_precision": ReasonCode.ARG_EXTRACTION_FAIL,
        "step_efficiency": ReasonCode.STEP_INEFFICIENT,
        "reasoning_coherence": ReasonCode.REASONING_INCOHERENT,
        "handoff_correctness": ReasonCode.HANDOFF_MISROUTED,
    },
    "X1F": {
        "prompt_injection_resistance": ReasonCode.PROMPT_INJECTION_DETECTED,
        "system_prompt_leakage": ReasonCode.SYSTEM_PROMPT_LEAK,
        "jailbreak_detection": ReasonCode.JAILBREAK_DETECTED,
        "bias_fairness": ReasonCode.BIAS_DELTA_EXCEEDED,
        "robustness": ReasonCode.ADVERSARIAL_CRASH,
    },
    # X1G is handled by the consistency module, not a dimension-graded gate.
}


class Gate:
    """One evaluation gate bound to a rubric and its graders.

    Wiring rule (spec §1, enforced here): hard-gate dimensions MUST be
    graded by ``CODE_BASED`` graders. This prevents a model-based judge
    from ever owning a safety-critical binary decision. Violations raise
    ``GateWiringError`` at construction.
    """

    def __init__(
        self,
        rubric: Rubric,
        graders: Mapping[str, Grader],
    ) -> None:
        self._rubric = rubric
        self._graders = dict(graders)

        missing = {d.name for d in rubric.dimensions} - self._graders.keys()
        if missing:
            raise GateWiringError(f"Gate {rubric.gate}: missing graders for dimensions {sorted(missing)}")
        extra = self._graders.keys() - {d.name for d in rubric.dimensions}
        if extra:
            raise GateWiringError(f"Gate {rubric.gate}: unused graders provided for {sorted(extra)}")
        # Enforce hard-gate invariant.
        for dim in rubric.dimensions:
            if dim.is_hard_gate:
                grader = self._graders[dim.name]
                if grader.grader_class is not GraderClass.CODE_BASED:
                    raise GateWiringError(
                        f"Gate {rubric.gate}: hard-gate dimension {dim.name!r} "
                        f"must use CODE_BASED grader, got {grader.grader_class.value}"
                    )

    @property
    def rubric(self) -> Rubric:
        return self._rubric

    def evaluate(self, context: GateContext) -> GateResult:
        """Run all dimension graders and compose their results.

        Per H8 fail-mode matrix:

        - ``GraderError`` → gate fails with reason ``GRADER_EXCEPTION``.
          For model-based dimensions the exception message is inspected to
          classify ``JUDGE_TIMEOUT`` vs generic ``JUDGE_ERROR``.
        - Abstain on any dimension → gate fails (passed=False) and reason
          codes include ``JUDGE_ABSTAINED``. The pipeline then routes to
          X3B (HITL), not to deny.
        """
        dimension_results: list[DimensionResult] = []
        reason_codes: list[ReasonCode] = []

        for dim in self._rubric.dimensions:
            grader = self._graders[dim.name]
            try:
                raw = grader.grade(dim, context.for_dimension(dim))
                result = grader.score_to_result(dim, raw)
            except TimeoutError as exc:
                return GateResult(
                    gate=self._rubric.gate,
                    rubric_version=self._rubric.version,
                    composition=self._rubric.composition,
                    aggregate=_error_aggregate(self._rubric.composition),
                    dimension_results=tuple(dimension_results),
                    reason_codes=(ReasonCode.JUDGE_TIMEOUT,),
                    error=f"judge timeout on {dim.name}: {exc}",
                )
            except GraderError as exc:
                rc = _classify_grader_error(dim, exc)
                return GateResult(
                    gate=self._rubric.gate,
                    rubric_version=self._rubric.version,
                    composition=self._rubric.composition,
                    aggregate=_error_aggregate(self._rubric.composition),
                    dimension_results=tuple(dimension_results),
                    reason_codes=(rc,),
                    error=f"grader error on {dim.name}: {exc}",
                )

            dimension_results.append(result)
            if result.abstain:
                reason_codes.append(ReasonCode.JUDGE_ABSTAINED)
            elif not result.passed:
                dim_rc = _DIMENSION_REASON_MAP.get(self._rubric.gate, {}).get(dim.name)
                if dim_rc is not None:
                    reason_codes.append(dim_rc)

        aggregate = compose(
            dimension_results,
            mode=self._rubric.composition,
            aggregate_threshold=self._rubric.aggregate_threshold,
        )
        return GateResult(
            gate=self._rubric.gate,
            rubric_version=self._rubric.version,
            composition=self._rubric.composition,
            aggregate=aggregate,
            dimension_results=tuple(dimension_results),
            reason_codes=tuple(reason_codes),
        )


def _classify_grader_error(dim: Dimension, exc: GraderError) -> ReasonCode:
    msg = str(exc).lower()
    if "timeout" in msg:
        return ReasonCode.JUDGE_TIMEOUT
    if dim.grader_class is GraderClass.MODEL_BASED:
        return ReasonCode.JUDGE_ERROR
    return ReasonCode.GRADER_EXCEPTION


def _error_aggregate(mode: CompositionMode) -> AggregateResult:
    return AggregateResult(
        passed=False,
        mode=mode,
        aggregate_score=None,
        aggregate_threshold=None,
    )


def build_standard_pipeline(
    rubric_bundle: Mapping[str, Rubric],
    grader_bundle: Mapping[str, Mapping[str, Grader]],
) -> list[Gate]:
    """Construct X1A-X1F gates in canonical order.

    X1G (consistency) is NOT constructed here — it is driven by the
    consistency module, not a dimension-graded rubric.
    """
    order = ("X1A", "X1B", "X1C", "X1D", "X1E", "X1F")
    gates: list[Gate] = []
    for name in order:
        if name not in rubric_bundle:
            continue
        rubric = rubric_bundle[name]
        graders = grader_bundle.get(name)
        if graders is None:
            raise GateWiringError(f"build_standard_pipeline: no graders supplied for {name}")
        gates.append(Gate(rubric, graders))
    return gates


def iter_gate_reason_codes(results: Iterable[GateResult]) -> list[ReasonCode]:
    """Collect reason codes from a sequence of gate results in order."""
    codes: list[ReasonCode] = []
    for r in results:
        codes.extend(r.reason_codes)
    return codes


__all__ = [
    "Gate",
    "GateContext",
    "GateResult",
    "GateWiringError",
    "build_standard_pipeline",
    "iter_gate_reason_codes",
]
