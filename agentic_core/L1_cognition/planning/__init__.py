"""L1 Reasoning + Plan Generation — v6 doctrine implementation.

This package implements the canonical six-stage L1 pipeline as specified in
``docs/reference/02_L1_Reasoning/`` (parent + 02.1 .. 02.6).

The v6 layer is **additive** over the existing v4/v5 implementation in
``agentic_core.L1_cognition.{types,reasoning,enforcement}``. It wraps the
existing typed surfaces (IntentFrame, PlanBundle, L1PlanContractV2, the
semantic validators, the self-repair loop) and adds:

  * the v6 typed packet contracts (ParsedIntentPacket, PlanBundlePacket,
    PlanningReasoningPacket, DraftPlanPacket, ValidatedPlanPacket,
    L1PlanHandoffPacket)
  * six stage entrypoints (parse_intent_frame .. emit_l1_plan_contract)
  * deterministic replay digests
  * OTEL span emitters for every stage's input.accepted / core.completed /
    output.emitted lifecycle
  * an end-to-end ``run_l1_planning(...)`` pipeline orchestrator
  * negative-boundary invariants (no retrieval / no route / no execution
    / no write) asserted both by the contracts and by the test suite

L1 layer authority is preserved end-to-end: nothing in this package
retrieves evidence, selects an authoritative route, executes tools, or
writes durable state. The output is always advisory — an
:class:`L1PlanContract` for L0 to consume.
"""

from __future__ import annotations

from agentic_core.L1_cognition.planning.contracts import (
    ActionExpectation,
    AmbiguitySeverity,
    ClarifyAbstainFallbackMarker,
    L1ContractViolation,
    DependencySketch,
    DownstreamPlanningNotes,
    DraftPlan,
    DraftPlanInput,
    DraftPlanPacket,
    FinalPlanReadinessReceipt,
    FirstSafetyAuthorityReading,
    IntentFrameSnapshot,
    InternalPlanState,
    JobClassFrame,
    L1HandoffReceipt,
    L1PlanContract,
    L1PlanContractInput,
    L1PlanHandoffPacket,
    L1SelfRepairLedger,
    L1TelemetryKeySet,
    LowestViableAgencyReceipt,
    NonAuthorityAssertion,
    ParsedIntentPacket,
    ParsedRequestInput,
    ParsedRequestReceipt,
    PlanBundleSnapshot,
    PlanBundlePacket,
    PlanConsistencyAudit,
    PlanDigest,
    PlanReplayManifest,
    PlanValidationInput,
    PlanValidationReport,
    PlanningPriorGapReport,
    PlanningPriorReadInput,
    PlanningPriorReadPlan,
    PlanningReasoningInput,
    PlanningReasoningPacket,
    PlanningReasoningTraceSummary,
    PlanningReferenceManifest,
    PlanningRefinementPass,
    PlanningLoopBudgetReceipt,
    PriorUseReceipt,
    ProposedRouteHint,
    QuerySpec,
    RequestDetailInventory,
    ReasoningQualitySignals,
    RouteHintSet,
    SupportExpectation,
    TaskSpec,
    ValidatedPlanPacket,
    WorkUnit,
    WorkUnitSet,
    WorkUnitType,
)
from agentic_core.L1_cognition.planning.intent_frame import parse_intent_frame
from agentic_core.L1_cognition.planning.planning_priors import (
    PlanningPriorReader,
    StaticPlanningPriorReader,
    build_plan_bundle,
)
from agentic_core.L1_cognition.planning.reasoning_loop import run_l1_reasoning_loop
from agentic_core.L1_cognition.planning.draft_plan import write_draft_plan
from agentic_core.L1_cognition.planning.plan_validation import (
    validate_and_repair_l1_plan,
)
from agentic_core.L1_cognition.planning.plan_contract_handoff import (
    emit_l1_plan_contract,
)
from agentic_core.L1_cognition.planning.pipeline import run_l1_planning
from agentic_core.L1_cognition.planning.otel import (
    InMemorySpanSink,
    L1SpanEvent,
    SpanSink,
    STAGE_IDS,
)
from agentic_core.L1_cognition.planning.digests import (
    DETERMINISTIC_DIGEST_ALGORITHM,
    canonical_payload,
    stable_digest,
)

__all__ = [
    # Stage 02.1
    "ParsedRequestInput",
    "ParsedRequestReceipt",
    "ParsedIntentPacket",
    "RequestDetailInventory",
    "JobClassFrame",
    "FirstSafetyAuthorityReading",
    "IntentFrameSnapshot",
    "parse_intent_frame",
    # Stage 02.2
    "PlanningPriorReadInput",
    "PlanningPriorReadPlan",
    "PlanningReferenceManifest",
    "PlanningPriorGapReport",
    "PriorUseReceipt",
    "PlanBundleSnapshot",
    "PlanBundlePacket",
    "PlanningPriorReader",
    "StaticPlanningPriorReader",
    "build_plan_bundle",
    # Stage 02.3
    "PlanningReasoningInput",
    "PlanningReasoningPacket",
    "PlanningReasoningTraceSummary",
    "PlanningRefinementPass",
    "PlanningLoopBudgetReceipt",
    "InternalPlanState",
    "ReasoningQualitySignals",
    "run_l1_reasoning_loop",
    # Stage 02.4
    "DraftPlan",
    "DraftPlanInput",
    "DraftPlanPacket",
    "WorkUnit",
    "WorkUnitSet",
    "WorkUnitType",
    "DependencySketch",
    "RouteHintSet",
    "ProposedRouteHint",
    "SupportExpectation",
    "ActionExpectation",
    "DownstreamPlanningNotes",
    "write_draft_plan",
    # Stage 02.5
    "PlanValidationInput",
    "PlanValidationReport",
    "PlanConsistencyAudit",
    "LowestViableAgencyReceipt",
    "L1SelfRepairLedger",
    "ClarifyAbstainFallbackMarker",
    "FinalPlanReadinessReceipt",
    "ValidatedPlanPacket",
    "AmbiguitySeverity",
    "validate_and_repair_l1_plan",
    # Stage 02.6
    "L1PlanContractInput",
    "L1PlanContract",
    "PlanReplayManifest",
    "L1HandoffReceipt",
    "DownstreamPlanningNotes",
    "NonAuthorityAssertion",
    "L1TelemetryKeySet",
    "L1PlanHandoffPacket",
    "PlanDigest",
    "QuerySpec",
    "TaskSpec",
    "emit_l1_plan_contract",
    # Pipeline
    "run_l1_planning",
    # OTEL helpers
    "InMemorySpanSink",
    "L1SpanEvent",
    "SpanSink",
    "STAGE_IDS",
    # Digest helpers
    "DETERMINISTIC_DIGEST_ALGORITHM",
    "canonical_payload",
    "stable_digest",
    # Errors
    "L1ContractViolation",
]
