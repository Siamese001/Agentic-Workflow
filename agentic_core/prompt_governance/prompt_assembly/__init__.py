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

from .input_contracts import (
    C0EvidenceContract,
    GovernanceArtifacts,
    L0RouteContract,
    L1PlanContract,
    UpstreamInputBundle,
    UserExecutionMetadata,
    upstream_bundle_from_dicts,
)
from .invariants import (
    InvariantReport,
    InvariantResult,
    check_invariants,
)
from .l2_handoff import (
    L2_MUST,
    L2_MUST_NOT,
    L2HandoffValidationResult,
    validate_l2_handoff,
)
from .metrics import (
    METRIC_NAMES,
    PA_METRICS,
    MetricDefinition,
    MetricType,
    PAMetricRegistry,
)
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
from .pa1_bom_resolver import (
    C0GroundedContextBlock,
    D0FenceBlock,
    E0ExemplarBlock,
    ExecutionMetadataBlock,
    H0HealingHintBlock,
    I0InstructionBlock,
    M0MetaControlBlock,
    R0SchemaBinding,
    S0Block,
    ToolBindingManifest,
    U0NeutralizedTaskBlock,
    Y0LearningPriorBlock,
    resolve_bom,
)
from .pa1_bom_resolver import (
    PromptBOMResolved as PromptBOMResolvedBOM,
)
from .pa2_slot_composition import (
    OVERRIDE_RULES,
    SLOT_AUTHORITY_RANK,
    SLOT_ORDER,
    AuthorityStack,
    CompositionResult,
    OverrideRule,
    SlotEntry,
    compose_slots,
    detect_authority_violations,
)
from .pa3_c0_classifier import (
    C0ChunkRecord,
    C0ClassifierResult,
    C0Disposition,
    classify_c0_chunk,
    classify_c0_chunks,
)
from .pa3_h0_healer import (
    DEFAULT_MAX_RETRIES,
    H0ReentryResult,
    validate_h0_reentry,
)
from .pa3_u0_airlock import (
    REJECT_THRESHOLD,
    U0AirlockResult,
    run_u0_airlock,
)
from .pa4_validation import (
    PA4ValidationReport,
    ValidationCheckResult,
    validate_pa4,
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
from .pa6_provider_rendering import (
    PROVIDER_LANES,
    RenderedPayload,
    render_anthropic,
    render_for_provider,
    render_gemini,
    render_local,
    render_openai_chat,
    render_openai_reasoning,
)
from .pa7_dispatch_states import (
    DispatchBlockReason,
    DispatchDisposition,
    DispatchOutcome,
    build_dispatch_outcome,
)
from .pa7_signature import (
    SIGNATURE_VERSION,
    SignedManifest,
    canonicalize_manifest,
    compute_manifest_hash,
    compute_replay_key,
    sign_manifest,
    verify_signature,
)
from .pipeline import (
    PromptAssemblyPipelineResult,
    run_prompt_assembly_pipeline,
)
from .trace_spans import (
    PA_PARENT_SPAN_NAME,
    PA_SPAN_DEFINITIONS,
    SPAN_NAMES,
    SpanCollector,
    SpanDefinition,
    SpanRecord,
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
