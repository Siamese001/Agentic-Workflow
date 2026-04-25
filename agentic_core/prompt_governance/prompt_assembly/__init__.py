"""Prompt Assembly stage contracts (PA.0 .. PA.7).

Implements the gap-closure contracts described in
``docs/reference/03_L0_Routing/Prompt Assembly/Prompt_Assembly_detailed.md``.

Each module is a pure-data / pure-function unit. No side effects at import.
The existing :class:`agentic_core.prompt_governance.contracts.PromptBOM` and
:class:`agentic_core.L2_execution.reasoning.compiled_artifact.CompiledPromptArtifact`
remain SSOT for the BOM and final signed artifact respectively; this
sub-package only adds the *stage* contracts (boundary, budget, dispatch,
classifier, events, pipeline orchestrator).
"""

from __future__ import annotations

from .observability_events import (
    PA_EVENT_TYPES,
    CompiledPromptArtifactSigned,
    PromptAssemblyBlocked,
    PromptAssemblyDispatched,
    PromptAssemblyEvent,
    PromptAssemblyStarted,
    PromptBOMResolved,
    PromptBudgetCompleted,
    PromptRenderedForProvider,
    PromptSecurityPassCompleted,
    PromptSlotValidationCompleted,
)
from .pa0_boundary import (
    BoundaryCheckResult,
    BoundaryFailReason,
    BoundaryStatus,
    boundary_check,
)
from .pa3_c0_classifier import (
    C0ChunkRecord,
    C0ClassifierResult,
    C0Disposition,
    classify_c0_chunk,
    classify_c0_chunks,
)
from .pa5_budget import (
    BUDGET_TRIM_ORDER,
    BudgetClass,
    BudgetReport,
    OverflowStatus,
    SlotBudgetEntry,
    build_budget_report,
    deterministic_trim,
)
from .pa7_dispatch_states import (
    DispatchBlockReason,
    DispatchDisposition,
    DispatchOutcome,
    build_dispatch_outcome,
)
from .pipeline import (
    PromptAssemblyPipelineResult,
    run_prompt_assembly_pipeline,
)

__all__ = [
    # PA.0
    "BoundaryCheckResult",
    "BoundaryFailReason",
    "BoundaryStatus",
    "boundary_check",
    # PA.3 C0 classifier
    "C0ChunkRecord",
    "C0ClassifierResult",
    "C0Disposition",
    "classify_c0_chunk",
    "classify_c0_chunks",
    # PA.5 Budget
    "BUDGET_TRIM_ORDER",
    "BudgetClass",
    "BudgetReport",
    "OverflowStatus",
    "SlotBudgetEntry",
    "build_budget_report",
    "deterministic_trim",
    # PA.7 Dispatch
    "DispatchBlockReason",
    "DispatchDisposition",
    "DispatchOutcome",
    "build_dispatch_outcome",
    # Observability
    "CompiledPromptArtifactSigned",
    "PA_EVENT_TYPES",
    "PromptAssemblyBlocked",
    "PromptAssemblyDispatched",
    "PromptAssemblyEvent",
    "PromptAssemblyStarted",
    "PromptBOMResolved",
    "PromptBudgetCompleted",
    "PromptRenderedForProvider",
    "PromptSecurityPassCompleted",
    "PromptSlotValidationCompleted",
    # Pipeline
    "PromptAssemblyPipelineResult",
    "run_prompt_assembly_pipeline",
]
