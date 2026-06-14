"""L3 runtime exit-evaluation framework (v4).

Implements the X1A-X1G gate chain described in
``docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v4.md``.

Produces a sealed-folder envelope consumed by
``agentic_core.L3_orchestration.exit_control.classify_exit`` (ADR-023 step [5]
HITL dispatch). This module owns evaluation (X1); ``exit_control`` owns
disposition dispatch (X3).

Public API:

- ``Rubric`` / ``Dimension`` / ``GraderClass`` — rubric contract
- ``Grader`` base and concrete graders (``SchemaGrader``, ``CitationGrader``,
  ``LLMJudgeGrader``)
- ``compose`` — binary/weighted/hybrid aggregation
- ``Gate`` / ``GateResult`` — single-gate evaluation
- ``EvaluationPipeline`` — run X1A-X1G, produce envelope + BUS rows
- ``Disposition`` / ``ReasonCode`` — disposition taxonomy
- ``PassKStore`` — consistency (pass^k) bucket store
- ``BreakGlassAuthority`` — X3E emergency override

Scope: this is the **evaluation plane**, not the dispatch plane. Gates here
MUST NOT mutate durable state. See v4 §Invariants.
"""

from agentic_core.L3_orchestration.exit_eval.break_glass import (
    BreakGlassAuthority,
    BreakGlassError,
    BreakGlassInvocation,
    BreakGlassToken,
)
from agentic_core.L3_orchestration.exit_eval.bus import BusEmitter, BusRow
from agentic_core.L3_orchestration.exit_eval.composition import (
    AggregateResult,
    CompositionMode,
    compose,
)
from agentic_core.L3_orchestration.exit_eval.consistency import (
    ConsistencyCheck,
    PassKStore,
    TrialRecord,
)
from agentic_core.L3_orchestration.exit_eval.consistency_sqlite import (
    SqlitePassKStore,
)
from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    DimensionResult,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.disposition import (
    Disposition,
    DispositionEnvelope,
    ReasonCode,
)
from agentic_core.L3_orchestration.exit_eval.gates import (
    Gate,
    GateContext,
    GateResult,
    build_standard_pipeline,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import (
    Grader,
    GraderError,
    GraderOutput,
)
from agentic_core.L3_orchestration.exit_eval.graders.adversarial import (
    JailbreakGrader,
    PromptInjectionGrader,
    RobustnessGrader,
    SystemPromptLeakGrader,
)
from agentic_core.L3_orchestration.exit_eval.graders.code_based import (
    CitationGrader,
    SchemaGrader,
)
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    JudgeProtocol,
    LLMJudgeGrader,
)
from agentic_core.L3_orchestration.exit_eval.pipeline import (
    ConsistencyPolicy,
    EvaluationPipeline,
    EvaluationResult,
)
from agentic_core.L3_orchestration.exit_eval.rubric import Rubric, load_rubric

__all__ = [
    "AggregateResult",
    "BreakGlassAuthority",
    "BreakGlassError",
    "BreakGlassInvocation",
    "BreakGlassToken",
    "BusEmitter",
    "BusRow",
    "CitationGrader",
    "CompositionMode",
    "ConsistencyCheck",
    "ConsistencyPolicy",
    "Dimension",
    "DimensionResult",
    "Disposition",
    "DispositionEnvelope",
    "EvaluationPipeline",
    "EvaluationResult",
    "Gate",
    "GateContext",
    "GateResult",
    "Grader",
    "GraderClass",
    "GraderError",
    "GraderOutput",
    "JailbreakGrader",
    "JudgeProtocol",
    "LLMJudgeGrader",
    "PassKStore",
    "PromptInjectionGrader",
    "ReasonCode",
    "RobustnessGrader",
    "Rubric",
    "SchemaGrader",
    "SqlitePassKStore",
    "SystemPromptLeakGrader",
    "TrialRecord",
    "RedisPassKStore",
    "build_evaluation_pipeline_with_tracing",
    "build_span_sink",
    "build_standard_pipeline",
    "compose",
    "load_rubric",
]


def __getattr__(name: str):
    """Lazy attribute loader.

    Importing the full exit_eval package should not force OTel or Redis
    client libraries to load. Resolving RedisPassKStore / build_span_sink
    on first access keeps the import surface minimal.
    """
    if name == "RedisPassKStore":
        from agentic_core.L3_orchestration.exit_eval.consistency_redis import (
            RedisPassKStore as _impl,
        )

        return _impl
    if name == "build_evaluation_pipeline_with_tracing":
        from agentic_core.L3_orchestration.exit_eval.factory import (
            build_evaluation_pipeline_with_tracing as _impl,
        )

        return _impl
    if name == "build_span_sink":
        from agentic_core.L3_orchestration.exit_eval.otel_sdk_sink import (
            build_span_sink as _impl,
        )

        return _impl
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
