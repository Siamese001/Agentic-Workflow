"""L1 v6 typed contracts (stages 02.1 .. 02.6).

Doctrine reference: ``docs/reference/02_L1_Reasoning/`` parent + 02.1..02.6.

Each stage contributes a small family of frozen dataclasses describing
its input, working state, and output. The package's six stage modules
then expose pure-function entrypoints (``parse_intent_frame`` ..
``emit_l1_plan_contract``) that consume / produce these contracts.

Cross-cutting invariants enforced here:

* All contracts are ``@dataclass(frozen=True)`` — no mutation after
  construction.
* All contracts expose ``to_dict()`` for canonical serialisation.
* Identity fields (request_id, trace_root, policy_hash_observed,
  instruction_hash_observed, source_envelope_id) flow unchanged across
  every stage.
* The :class:`NonAuthorityAssertion` block on the final
  :class:`L1PlanContract` requires every "no_*" flag to be ``True`` for
  handoff. Violating that raises :class:`L1ContractViolation`.

The contracts wrap (and are projection-compatible with) the existing
``IntentFrame``, ``PlanBundle``, and ``L1PlanContractV2`` types in
``agentic_core.L1_cognition.types``. Where the v4/v5 types already
carry the data, this module reuses them rather than duplicating fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agentic_core.L1_cognition.types.intent_frame_types import (
    AmbiguityRegister,
    IntentFrame,
)
from agentic_core.L1_cognition.types.plan_bundle_types import (
    PlanBundle,
    RuleAwarePlanningFrame,
)
from agentic_core.L1_cognition.types.plan_contract_types import (
    L1PlanContractV2,
)
from agentic_core.L1_cognition.planning.digests import (
    DETERMINISTIC_DIGEST_ALGORITHM,
    stable_digest,
)


__all__ = [
    "L1ContractViolation",
    # Stage 02.1
    "ParsedRequestInput",
    "RequestDetailInventory",
    "JobClassFrame",
    "FirstSafetyAuthorityReading",
    "IntentFrameSnapshot",
    "ParsedRequestReceipt",
    "ParsedIntentPacket",
    # Stage 02.2
    "ReferenceClass",
    "PlanningPriorReadInput",
    "PlanningPriorReadPlan",
    "PlanningReferenceManifest",
    "PlanningPriorGapReport",
    "PriorUseReceipt",
    "PlanBundleSnapshot",
    "PlanBundlePacket",
    # Stage 02.3
    "PlanningReasoningInput",
    "InternalPlanState",
    "PlanningRefinementPass",
    "PassStatus",
    "PlanningLoopBudgetReceipt",
    "ReasoningQualitySignals",
    "PlanningReasoningTraceSummary",
    "PlanningReasoningPacket",
    # Stage 02.4
    "WorkUnitType",
    "WorkUnit",
    "WorkUnitSet",
    "DependencySketch",
    "ProposedRouteHint",
    "RouteHintSet",
    "SupportExpectation",
    "ActionExpectation",
    "DownstreamPlanningNotes",
    "DraftPlanInput",
    "DraftPlan",
    "DraftPlanPacket",
    # Stage 02.5
    "AmbiguitySeverity",
    "ValidationStatus",
    "RepairAction",
    "PlanValidationInput",
    "PlanValidationReport",
    "PlanConsistencyAudit",
    "LowestViableAgencyReceipt",
    "L1SelfRepairLedger",
    "ClarifyAbstainFallbackMarker",
    "FinalPlanReadinessReceipt",
    "ValidatedPlanPacket",
    # Stage 02.6
    "QuerySpec",
    "TaskSpec",
    "PlanReplayManifest",
    "NonAuthorityAssertion",
    "L1TelemetryKeySet",
    "L1HandoffReceipt",
    "L1PlanContract",
    "L1PlanContractInput",
    "L1PlanHandoffPacket",
    "PlanDigest",
    # Helper
    "freeze_intent_frame_snapshot",
    "freeze_plan_bundle_snapshot",
]


class L1ContractViolation(ValueError):
    """Raised when an L1 v6 typed contract fails validation."""


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def _require_str(value: Any, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise L1ContractViolation(f"{name} must be str, got {type(value).__name__}")
    if not allow_empty and not value.strip():
        raise L1ContractViolation(f"{name} must be a non-empty string")
    return value


def _require_tuple_of_str(value: Any, name: str) -> tuple[str, ...]:
    if isinstance(value, str) or not hasattr(value, "__iter__"):
        raise L1ContractViolation(f"{name} must be a tuple of str")
    out: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise L1ContractViolation(f"{name}[{idx}] must be str, got {type(item).__name__}")
        out.append(item)
    return tuple(out)


# ---------------------------------------------------------------------------
# Stage 02.1 — Intent Frame & Ambiguity Register
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedRequestInput:
    """02.1 § PHASE 1.1 — typed L1 input wrapper around U0's ValidatedRequest.

    ``validated_request`` may be any caller-supplied object whose
    canonical ``to_dict()`` projection is hash-stable. The L1 layer does
    not validate U0's invariants again; it only digests them.
    """

    request_id: str
    session_id: str
    trace_root: str
    caller_scope_baseline: str
    normalized_user_payload: str
    visible_conversation_context: tuple = ()
    user_constraints: tuple = ()
    system_constraints: tuple = ()
    known_artifact_refs: tuple = ()
    uploaded_object_refs: tuple = ()
    source_handles: tuple = ()
    request_freshness_hints: tuple = ()
    output_channel_expectations: tuple = ()
    policy_hash_observed: str = ""
    instruction_hash_observed: str = ""
    source_envelope_id: str = ""
    validated_request: Any = None
    rejected_request_summary: Any = None

    def __post_init__(self) -> None:
        _require_str(self.request_id, "request_id")
        _require_str(self.session_id, "session_id", allow_empty=True)
        _require_str(self.trace_root, "trace_root")
        _require_str(self.caller_scope_baseline, "caller_scope_baseline", allow_empty=True)
        _require_str(self.normalized_user_payload, "normalized_user_payload", allow_empty=True)
        if self.validated_request is None and self.rejected_request_summary is None:
            raise L1ContractViolation(
                "ParsedRequestInput requires validated_request or rejected_request_summary to be present."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "trace_root": self.trace_root,
            "caller_scope_baseline": self.caller_scope_baseline,
            "normalized_user_payload": self.normalized_user_payload,
            "visible_conversation_context": list(self.visible_conversation_context),
            "user_constraints": list(self.user_constraints),
            "system_constraints": list(self.system_constraints),
            "known_artifact_refs": list(self.known_artifact_refs),
            "uploaded_object_refs": list(self.uploaded_object_refs),
            "source_handles": list(self.source_handles),
            "request_freshness_hints": list(self.request_freshness_hints),
            "output_channel_expectations": list(self.output_channel_expectations),
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "source_envelope_id": self.source_envelope_id,
            "has_validated_request": self.validated_request is not None,
            "has_rejected_request_summary": self.rejected_request_summary is not None,
        }


@dataclass(frozen=True)
class RequestDetailInventory:
    """02.1 § PHASE 1.3 — concrete inventory of nouns and shape-hints."""

    entities: tuple = ()
    actors: tuple = ()
    systems: tuple = ()
    files: tuple = ()
    uploaded_objects: tuple = ()
    connectors: tuple = ()
    urls: tuple = ()
    dates: tuple = ()
    versions: tuple = ()
    exact_terms: tuple = ()
    numbers: tuple = ()
    variables: tuple = ()
    locations: tuple = ()
    source_names: tuple = ()
    requested_schema_or_table_shape: str = ""
    requested_ascii_or_diagram_shape: str = ""
    direct_quote_needed: bool = False
    citation_needed: bool = False
    artifact_output_needed: bool = False
    external_action_requested: bool = False

    def __post_init__(self) -> None:
        for name in (
            "entities",
            "actors",
            "systems",
            "files",
            "uploaded_objects",
            "connectors",
            "urls",
            "dates",
            "versions",
            "exact_terms",
            "numbers",
            "variables",
            "locations",
            "source_names",
        ):
            _require_tuple_of_str(getattr(self, name), name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entities": list(self.entities),
            "actors": list(self.actors),
            "systems": list(self.systems),
            "files": list(self.files),
            "uploaded_objects": list(self.uploaded_objects),
            "connectors": list(self.connectors),
            "urls": list(self.urls),
            "dates": list(self.dates),
            "versions": list(self.versions),
            "exact_terms": list(self.exact_terms),
            "numbers": list(self.numbers),
            "variables": list(self.variables),
            "locations": list(self.locations),
            "source_names": list(self.source_names),
            "requested_schema_or_table_shape": self.requested_schema_or_table_shape,
            "requested_ascii_or_diagram_shape": self.requested_ascii_or_diagram_shape,
            "direct_quote_needed": self.direct_quote_needed,
            "citation_needed": self.citation_needed,
            "artifact_output_needed": self.artifact_output_needed,
            "external_action_requested": self.external_action_requested,
        }


@dataclass(frozen=True)
class JobClassFrame:
    """02.1 § PHASE 1 — explicit work-class banding."""

    work_class: str  # one of the 11 allowed classes
    is_artifact_or_action: bool
    is_high_risk: bool

    _ALLOWED_WORK_CLASSES: frozenset = field(
        default=frozenset(
            {
                "summarize",
                "compare",
                "explain",
                "analyze",
                "plan",
                "act",
                "create",
                "edit",
                "retrieve",
                "decide",
                "escalate",
                # extra hooks accepted from underlying WorkClass enum.
                "factual",
                "creative",
                "mathematical",
                "code",
                "unknown",
            }
        ),
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        _require_str(self.work_class, "work_class")
        if self.work_class not in self._ALLOWED_WORK_CLASSES:
            raise L1ContractViolation(
                f"work_class must be one of {sorted(self._ALLOWED_WORK_CLASSES)}, got {self.work_class!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "work_class": self.work_class,
            "is_artifact_or_action": self.is_artifact_or_action,
            "is_high_risk": self.is_high_risk,
        }


@dataclass(frozen=True)
class FirstSafetyAuthorityReading:
    """02.1 § PHASE 1.5 — risk markers carried into planning.

    This is a v6 envelope around the existing
    :class:`agentic_core.L1_cognition.enforcement.first_safety_reading.FirstSafetyReading`.
    The mapping is direct field-by-field; we re-declare the shape here
    so 02.1's owned contracts do not depend on the enforcement package.
    """

    request_id: str
    read_only_request: bool = False
    reversible_action_request: bool = False
    durable_write_request: bool = False
    external_side_effect_request: bool = False
    high_impact_domain_hint: bool = False
    authority_override_attempt: bool = False
    prompt_injection_like_text_present: bool = False
    retrieved_content_quoted_by_user: bool = False
    human_or_tool_output_embedded_by_user: bool = False
    hitl_may_be_needed: bool = False
    uwg_may_be_needed: bool = False
    direct_refusal_may_be_needed: bool = False
    safe_direct_response_possible: bool = False
    risk_notes: tuple = ()

    def __post_init__(self) -> None:
        _require_str(self.request_id, "request_id")
        _require_tuple_of_str(self.risk_notes, "risk_notes")

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "read_only_request": self.read_only_request,
            "reversible_action_request": self.reversible_action_request,
            "durable_write_request": self.durable_write_request,
            "external_side_effect_request": self.external_side_effect_request,
            "high_impact_domain_hint": self.high_impact_domain_hint,
            "authority_override_attempt": self.authority_override_attempt,
            "prompt_injection_like_text_present": self.prompt_injection_like_text_present,
            "retrieved_content_quoted_by_user": self.retrieved_content_quoted_by_user,
            "human_or_tool_output_embedded_by_user": self.human_or_tool_output_embedded_by_user,
            "hitl_may_be_needed": self.hitl_may_be_needed,
            "uwg_may_be_needed": self.uwg_may_be_needed,
            "direct_refusal_may_be_needed": self.direct_refusal_may_be_needed,
            "safe_direct_response_possible": self.safe_direct_response_possible,
            "risk_notes": list(self.risk_notes),
        }


@dataclass(frozen=True)
class IntentFrameSnapshot:
    """Hashable read-only projection of :class:`IntentFrame`.

    The v6 packet contracts carry this snapshot rather than the live
    :class:`IntentFrame` so the deterministic digest is stable across
    re-imports and across calling processes.
    """

    request_id: str
    intent_frame_id: str
    normalized_goal: str
    user_visible_deliverable: str
    work_class: str
    audience: str
    output_target_kind: str
    freshness_class: str
    action_requirement: str
    artifact_requirement: str
    high_risk: bool
    constraints: tuple
    details: tuple
    ambiguity: dict
    success_condition: str

    @classmethod
    def from_intent_frame(
        cls, frame: IntentFrame, *, intent_frame_id: str | None = None
    ) -> "IntentFrameSnapshot":
        return cls(
            request_id=frame.request_id,
            intent_frame_id=intent_frame_id or f"if::{frame.request_id}",
            normalized_goal=frame.goal,
            user_visible_deliverable=frame.output_target_kind.value,
            work_class=frame.work_class.value,
            audience=frame.audience,
            output_target_kind=frame.output_target_kind.value,
            freshness_class=frame.freshness_class.value,
            action_requirement=frame.action_requirement.value,
            artifact_requirement=frame.artifact_requirement.value,
            high_risk=frame.high_risk,
            constraints=tuple(c.to_dict() for c in frame.constraints),
            details=tuple(frame.details),
            ambiguity=frame.ambiguity.to_dict(),
            success_condition=frame.success_condition,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "intent_frame_id": self.intent_frame_id,
            "normalized_goal": self.normalized_goal,
            "user_visible_deliverable": self.user_visible_deliverable,
            "work_class": self.work_class,
            "audience": self.audience,
            "output_target_kind": self.output_target_kind,
            "freshness_class": self.freshness_class,
            "action_requirement": self.action_requirement,
            "artifact_requirement": self.artifact_requirement,
            "high_risk": self.high_risk,
            "constraints": list(self.constraints),
            "details": list(self.details),
            "ambiguity": dict(self.ambiguity),
            "success_condition": self.success_condition,
        }


def freeze_intent_frame_snapshot(
    frame: IntentFrame, *, intent_frame_id: str | None = None
) -> IntentFrameSnapshot:
    """Module-level helper for the snapshot constructor."""
    return IntentFrameSnapshot.from_intent_frame(frame, intent_frame_id=intent_frame_id)


@dataclass(frozen=True)
class ParsedRequestReceipt:
    """02.1 § PHASE 1 — receipt of the parse with deterministic digest."""

    receipt_id: str
    request_id: str
    trace_root: str
    input_digest: str
    output_digest: str
    digest_algorithm: str = DETERMINISTIC_DIGEST_ALGORITHM

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "digest_algorithm": self.digest_algorithm,
        }


@dataclass(frozen=True)
class ParsedIntentPacket:
    """02.1 § PHASE 2 — output of :func:`parse_intent_frame`."""

    intent_frame: IntentFrameSnapshot
    request_detail_inventory: RequestDetailInventory
    job_class_frame: JobClassFrame
    ambiguity_register: dict
    first_safety_authority_reading: FirstSafetyAuthorityReading
    parsed_request_receipt: ParsedRequestReceipt
    user_intent_authority_separation_receipt: dict
    policy_hash_observed: str
    instruction_hash_observed: str
    source_envelope_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_frame": self.intent_frame.to_dict(),
            "request_detail_inventory": self.request_detail_inventory.to_dict(),
            "job_class_frame": self.job_class_frame.to_dict(),
            "ambiguity_register": dict(self.ambiguity_register),
            "first_safety_authority_reading": self.first_safety_authority_reading.to_dict(),
            "parsed_request_receipt": self.parsed_request_receipt.to_dict(),
            "user_intent_authority_separation_receipt": dict(self.user_intent_authority_separation_receipt),
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "source_envelope_id": self.source_envelope_id,
        }


# ---------------------------------------------------------------------------
# Stage 02.2 — Planning Priors & Rule Bundle
# ---------------------------------------------------------------------------


class ReferenceClass(str, Enum):
    """02.2 § PHASE 1 — closed list of allowed planning reference classes."""

    TASK_SCHEMAS = "task_schemas"
    ROUTE_HEURISTICS = "route_heuristics"
    OUTPUT_CONTRACTS = "output_contracts"
    ARTIFACT_TEMPLATES = "artifact_templates"
    VALIDATION_RUBRICS = "validation_rubrics"
    GROUNDING_CRITERIA = "grounding_criteria"
    CITATION_STANDARDS = "citation_standards"
    COMPLIANCE_BOUNDS = "compliance_bounds"
    ESCALATION_THRESHOLDS = "escalation_thresholds"
    REFUSAL_TAXONOMY = "refusal_taxonomy"
    SAFE_DECOMPOSITION_PATTERNS = "safe_decomposition_patterns"
    APPROVED_PLAN_EXAMPLES = "approved_plan_examples"
    ANTI_PATTERNS = "anti_patterns"
    FALLBACK_TEMPLATES = "fallback_templates"


@dataclass(frozen=True)
class PlanningPriorReadInput:
    """02.2 § PHASE 1.1 — typed input for the prior reader."""

    intent_frame: IntentFrameSnapshot
    ambiguity_register: dict
    first_safety_authority_reading: FirstSafetyAuthorityReading
    request_id: str
    trace_root: str
    caller_scope_baseline: str
    policy_hash_observed: str
    instruction_hash_observed: str
    allowed_planning_reference_classes: tuple = ()
    blocked_planning_reference_classes: tuple = ()
    planning_prior_budget: int = 4096
    replay_key_seed: str = ""

    def __post_init__(self) -> None:
        _require_str(self.request_id, "request_id")
        _require_str(self.trace_root, "trace_root")
        if not isinstance(self.allowed_planning_reference_classes, tuple):
            raise L1ContractViolation("allowed_planning_reference_classes must be a tuple")
        if not isinstance(self.blocked_planning_reference_classes, tuple):
            raise L1ContractViolation("blocked_planning_reference_classes must be a tuple")
        if self.planning_prior_budget < 0:
            raise L1ContractViolation("planning_prior_budget must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_frame": self.intent_frame.to_dict(),
            "ambiguity_register": dict(self.ambiguity_register),
            "first_safety_authority_reading": self.first_safety_authority_reading.to_dict(),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "caller_scope_baseline": self.caller_scope_baseline,
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "allowed_planning_reference_classes": [
                c.value if isinstance(c, ReferenceClass) else c
                for c in self.allowed_planning_reference_classes
            ],
            "blocked_planning_reference_classes": [
                c.value if isinstance(c, ReferenceClass) else c
                for c in self.blocked_planning_reference_classes
            ],
            "planning_prior_budget": self.planning_prior_budget,
            "replay_key_seed": self.replay_key_seed,
        }


@dataclass(frozen=True)
class PlanningPriorReadPlan:
    """02.2 § PHASE 1.2 — read plan handed to the reader."""

    read_plan_id: str
    reference_classes_requested: tuple
    lookup_keys: tuple = ()
    policy_filters: tuple = ()
    task_schema_filters: tuple = ()
    route_heuristic_filters: tuple = ()
    exemplar_filters: tuple = ()
    rubric_filters: tuple = ()
    decomposition_template_filters: tuple = ()
    refusal_taxonomy_filters: tuple = ()
    max_items_by_class: int = 16
    max_tokens_by_class: int = 1024
    no_answer_evidence_assertion: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "read_plan_id": self.read_plan_id,
            "reference_classes_requested": [
                c.value if isinstance(c, ReferenceClass) else c for c in self.reference_classes_requested
            ],
            "lookup_keys": list(self.lookup_keys),
            "policy_filters": list(self.policy_filters),
            "task_schema_filters": list(self.task_schema_filters),
            "route_heuristic_filters": list(self.route_heuristic_filters),
            "exemplar_filters": list(self.exemplar_filters),
            "rubric_filters": list(self.rubric_filters),
            "decomposition_template_filters": list(self.decomposition_template_filters),
            "refusal_taxonomy_filters": list(self.refusal_taxonomy_filters),
            "max_items_by_class": self.max_items_by_class,
            "max_tokens_by_class": self.max_tokens_by_class,
            "no_answer_evidence_assertion": self.no_answer_evidence_assertion,
        }


@dataclass(frozen=True)
class PlanningReferenceManifest:
    """02.2 § PHASE 1.3 — outcome of the reader call."""

    manifest_id: str
    references_loaded: tuple
    references_blocked: tuple = ()
    stale_references: tuple = ()
    missing_reference_classes: tuple = ()
    l4_snapshot_refs: tuple = ()
    source_authority_labels: tuple = ()
    reference_hashes: tuple = ()
    read_scope_receipt: dict = field(default_factory=dict)
    no_answer_evidence_assertion: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "references_loaded": list(self.references_loaded),
            "references_blocked": list(self.references_blocked),
            "stale_references": list(self.stale_references),
            "missing_reference_classes": list(self.missing_reference_classes),
            "l4_snapshot_refs": list(self.l4_snapshot_refs),
            "source_authority_labels": list(self.source_authority_labels),
            "reference_hashes": list(self.reference_hashes),
            "read_scope_receipt": dict(self.read_scope_receipt),
            "no_answer_evidence_assertion": self.no_answer_evidence_assertion,
        }


@dataclass(frozen=True)
class PlanningPriorGapReport:
    """02.2 § PHASE 1 — gap report for missing prior classes."""

    missing_classes: tuple = ()
    degraded_planning_quality: bool = False
    fallback_strategy: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "missing_classes": list(self.missing_classes),
            "degraded_planning_quality": self.degraded_planning_quality,
            "fallback_strategy": self.fallback_strategy,
        }


@dataclass(frozen=True)
class PriorUseReceipt:
    """02.2 § PHASE 1 — per-prior usage marker."""

    prior_ref: str
    used_for: str
    used_in_section: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prior_ref": self.prior_ref,
            "used_for": self.used_for,
            "used_in_section": self.used_in_section,
        }


@dataclass(frozen=True)
class PlanBundleSnapshot:
    """Hashable read-only projection of :class:`PlanBundle`."""

    bundle_id: str
    bundle_hash: str
    schemas: tuple
    route_heuristics: tuple
    output_contracts: tuple
    validation_rubric: tuple
    policy_bounds: tuple
    escalation_thresholds: tuple
    disallowed_actions: tuple
    hitl_triggers: tuple
    exemplars: tuple
    edge_cases: tuple
    approved_templates: tuple
    stopping_rules: tuple
    retry_boundaries: tuple
    abstain_patterns: tuple
    max_steps: int
    max_wallclock_ms: int
    rule_aware_planning_frame: dict

    @classmethod
    def from_plan_bundle(
        cls,
        bundle: PlanBundle,
        rule_frame: RuleAwarePlanningFrame,
        *,
        bundle_id: str | None = None,
    ) -> "PlanBundleSnapshot":
        return cls(
            bundle_id=bundle_id or f"pb::{bundle.bundle_hash[:12]}",
            bundle_hash=bundle.bundle_hash,
            schemas=tuple(bundle.schemas),
            route_heuristics=tuple(bundle.route_heuristics),
            output_contracts=tuple(bundle.output_contracts),
            validation_rubric=tuple(bundle.validation_rubric),
            policy_bounds=tuple(bundle.policy_bounds),
            escalation_thresholds=tuple(bundle.escalation_thresholds),
            disallowed_actions=tuple(bundle.disallowed_actions),
            hitl_triggers=tuple(bundle.hitl_triggers),
            exemplars=tuple(bundle.exemplars),
            edge_cases=tuple(bundle.edge_cases),
            approved_templates=tuple(bundle.approved_templates),
            stopping_rules=tuple(bundle.stopping_rules),
            retry_boundaries=tuple(bundle.retry_boundaries),
            abstain_patterns=tuple(bundle.abstain_patterns),
            max_steps=bundle.max_steps,
            max_wallclock_ms=bundle.max_wallclock_ms,
            rule_aware_planning_frame=rule_frame.to_dict(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "bundle_hash": self.bundle_hash,
            "schemas": list(self.schemas),
            "route_heuristics": list(self.route_heuristics),
            "output_contracts": list(self.output_contracts),
            "validation_rubric": list(self.validation_rubric),
            "policy_bounds": list(self.policy_bounds),
            "escalation_thresholds": list(self.escalation_thresholds),
            "disallowed_actions": list(self.disallowed_actions),
            "hitl_triggers": list(self.hitl_triggers),
            "exemplars": list(self.exemplars),
            "edge_cases": list(self.edge_cases),
            "approved_templates": list(self.approved_templates),
            "stopping_rules": list(self.stopping_rules),
            "retry_boundaries": list(self.retry_boundaries),
            "abstain_patterns": list(self.abstain_patterns),
            "max_steps": self.max_steps,
            "max_wallclock_ms": self.max_wallclock_ms,
            "rule_aware_planning_frame": dict(self.rule_aware_planning_frame),
        }


def freeze_plan_bundle_snapshot(
    bundle: PlanBundle,
    rule_frame: RuleAwarePlanningFrame,
    *,
    bundle_id: str | None = None,
) -> PlanBundleSnapshot:
    return PlanBundleSnapshot.from_plan_bundle(bundle, rule_frame, bundle_id=bundle_id)


@dataclass(frozen=True)
class PlanBundlePacket:
    """02.2 § PHASE 2 — output of :func:`build_plan_bundle`."""

    plan_bundle: PlanBundleSnapshot
    planning_prior_read_plan: PlanningPriorReadPlan
    planning_reference_manifest: PlanningReferenceManifest
    planning_prior_gap_report: PlanningPriorGapReport
    rule_aware_planning_frame: dict
    bundle_digest: str
    request_id: str
    trace_root: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_bundle": self.plan_bundle.to_dict(),
            "planning_prior_read_plan": self.planning_prior_read_plan.to_dict(),
            "planning_reference_manifest": self.planning_reference_manifest.to_dict(),
            "planning_prior_gap_report": self.planning_prior_gap_report.to_dict(),
            "rule_aware_planning_frame": dict(self.rule_aware_planning_frame),
            "bundle_digest": self.bundle_digest,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
        }


# ---------------------------------------------------------------------------
# Stage 02.3 — Contextual Refinement Reasoning Loop
# ---------------------------------------------------------------------------


class PassStatus(str, Enum):
    PASS_IMPROVED = "PASS_IMPROVED"
    PASS_NO_CHANGE = "PASS_NO_CHANGE"
    PASS_DEGRADED_REJECTED = "PASS_DEGRADED_REJECTED"
    PASS_STOP_CLARIFY_RECOMMENDED = "PASS_STOP_CLARIFY_RECOMMENDED"
    PASS_STOP_ABSTAIN_RECOMMENDED = "PASS_STOP_ABSTAIN_RECOMMENDED"
    PASS_STOP_POLICY_REVIEW_NEEDED = "PASS_STOP_POLICY_REVIEW_NEEDED"


@dataclass(frozen=True)
class PlanningReasoningInput:
    """02.3 § PHASE 1.1 — typed reasoning-loop input."""

    intent_frame: IntentFrameSnapshot
    ambiguity_register: dict
    request_detail_inventory: RequestDetailInventory
    first_safety_authority_reading: FirstSafetyAuthorityReading
    plan_bundle: PlanBundleSnapshot
    rule_aware_planning_frame: dict
    request_id: str
    trace_root: str
    policy_hash_observed: str
    instruction_hash_observed: str
    max_refinement_passes: int = 2
    reasoning_budget: int = 8192
    replay_key_seed: str = ""

    def __post_init__(self) -> None:
        _require_str(self.request_id, "request_id")
        _require_str(self.trace_root, "trace_root")
        if self.max_refinement_passes < 0:
            raise L1ContractViolation("max_refinement_passes must be non-negative")
        if self.reasoning_budget < 0:
            raise L1ContractViolation("reasoning_budget must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_frame": self.intent_frame.to_dict(),
            "ambiguity_register": dict(self.ambiguity_register),
            "request_detail_inventory": self.request_detail_inventory.to_dict(),
            "first_safety_authority_reading": self.first_safety_authority_reading.to_dict(),
            "plan_bundle": self.plan_bundle.to_dict(),
            "rule_aware_planning_frame": dict(self.rule_aware_planning_frame),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "max_refinement_passes": self.max_refinement_passes,
            "reasoning_budget": self.reasoning_budget,
            "replay_key_seed": self.replay_key_seed,
        }


@dataclass(frozen=True)
class InternalPlanState:
    """02.3 § PHASE 1.2 — bounded summary of the reasoning state."""

    internal_plan_state_id: str
    normalized_goal_summary: str
    deliverable_summary: str
    constraint_bindings: tuple = ()
    source_expectation_summary: str = ""
    support_need_summary: str = ""
    action_risk_summary: str = ""
    artifact_need_summary: str = ""
    preliminary_work_units: tuple = ()
    dependency_candidates: tuple = ()
    route_discriminator_candidates: tuple = ()
    uncertainty_markers: tuple = ()
    unsafe_or_unsupported_markers: tuple = ()
    simplification_candidates: tuple = ()
    stop_state_candidates: tuple = ()
    state_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "internal_plan_state_id": self.internal_plan_state_id,
            "normalized_goal_summary": self.normalized_goal_summary,
            "deliverable_summary": self.deliverable_summary,
            "constraint_bindings": list(self.constraint_bindings),
            "source_expectation_summary": self.source_expectation_summary,
            "support_need_summary": self.support_need_summary,
            "action_risk_summary": self.action_risk_summary,
            "artifact_need_summary": self.artifact_need_summary,
            "preliminary_work_units": list(self.preliminary_work_units),
            "dependency_candidates": list(self.dependency_candidates),
            "route_discriminator_candidates": list(self.route_discriminator_candidates),
            "uncertainty_markers": list(self.uncertainty_markers),
            "unsafe_or_unsupported_markers": list(self.unsafe_or_unsupported_markers),
            "simplification_candidates": list(self.simplification_candidates),
            "stop_state_candidates": list(self.stop_state_candidates),
            "state_digest": self.state_digest,
        }


@dataclass(frozen=True)
class PlanningRefinementPass:
    """02.3 § PHASE 1.3 — single refinement pass receipt."""

    pass_id: str
    pass_index: int
    input_state_digest: str
    refinement_focus: str
    constraints_preserved: tuple = ()
    ambiguities_resolved_by_assumption: tuple = ()
    ambiguities_left_open: tuple = ()
    risks_promoted_to_marker: tuple = ()
    support_needs_promoted: tuple = ()
    action_needs_promoted: tuple = ()
    simplifications_applied: tuple = ()
    overreach_removed: tuple = ()
    output_state_digest: str = ""
    pass_status: PassStatus = PassStatus.PASS_IMPROVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "pass_id": self.pass_id,
            "pass_index": self.pass_index,
            "input_state_digest": self.input_state_digest,
            "refinement_focus": self.refinement_focus,
            "constraints_preserved": list(self.constraints_preserved),
            "ambiguities_resolved_by_assumption": list(self.ambiguities_resolved_by_assumption),
            "ambiguities_left_open": list(self.ambiguities_left_open),
            "risks_promoted_to_marker": list(self.risks_promoted_to_marker),
            "support_needs_promoted": list(self.support_needs_promoted),
            "action_needs_promoted": list(self.action_needs_promoted),
            "simplifications_applied": list(self.simplifications_applied),
            "overreach_removed": list(self.overreach_removed),
            "output_state_digest": self.output_state_digest,
            "pass_status": self.pass_status.value,
        }


@dataclass(frozen=True)
class PlanningLoopBudgetReceipt:
    """02.3 § PHASE 1.4 — budget receipt + loop-not-spinning assertion."""

    max_refinement_passes: int
    passes_used: int
    reasoning_budget_initial: int
    reasoning_budget_remaining: int
    stopped_reason: str
    loop_not_spinning_assertion: bool = True
    no_tool_calls_assertion: bool = True
    no_retrieval_assertion: bool = True
    no_route_commit_assertion: bool = True

    def __post_init__(self) -> None:
        if self.passes_used > self.max_refinement_passes:
            raise L1ContractViolation("passes_used must not exceed max_refinement_passes")
        if self.reasoning_budget_remaining < 0:
            raise L1ContractViolation("reasoning_budget_remaining must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_refinement_passes": self.max_refinement_passes,
            "passes_used": self.passes_used,
            "reasoning_budget_initial": self.reasoning_budget_initial,
            "reasoning_budget_remaining": self.reasoning_budget_remaining,
            "stopped_reason": self.stopped_reason,
            "loop_not_spinning_assertion": self.loop_not_spinning_assertion,
            "no_tool_calls_assertion": self.no_tool_calls_assertion,
            "no_retrieval_assertion": self.no_retrieval_assertion,
            "no_route_commit_assertion": self.no_route_commit_assertion,
        }


@dataclass(frozen=True)
class ReasoningQualitySignals:
    """02.3 § PHASE 1.5 — quality markers for the trace summary."""

    constraints_preserved_score: float = 1.0
    deliverable_clarity_score: float = 1.0
    safety_alignment_score: float = 1.0
    simplification_score: float = 1.0
    overall_quality_band: str = "high"

    def __post_init__(self) -> None:
        for fname in (
            "constraints_preserved_score",
            "deliverable_clarity_score",
            "safety_alignment_score",
            "simplification_score",
        ):
            v = getattr(self, fname)
            if not isinstance(v, (int, float)):
                raise L1ContractViolation(f"{fname} must be numeric")
            if not (0.0 <= float(v) <= 1.0):
                raise L1ContractViolation(f"{fname} must be in [0.0, 1.0]")
        if self.overall_quality_band not in ("low", "medium", "high"):
            raise L1ContractViolation("overall_quality_band must be one of low/medium/high")

    def to_dict(self) -> dict[str, Any]:
        return {
            "constraints_preserved_score": self.constraints_preserved_score,
            "deliverable_clarity_score": self.deliverable_clarity_score,
            "safety_alignment_score": self.safety_alignment_score,
            "simplification_score": self.simplification_score,
            "overall_quality_band": self.overall_quality_band,
        }


@dataclass(frozen=True)
class PlanningReasoningTraceSummary:
    """02.3 § PHASE 1.6 — audit-safe trace summary (no chain-of-thought)."""

    summary_id: str
    visible_inputs_hash: str
    plan_bundle_hash: str
    initial_state_digest: str
    final_state_digest: str
    pass_receipts: tuple = ()
    quality_signals: Optional[ReasoningQualitySignals] = None
    non_authority_assertions: dict = field(
        default_factory=lambda: {
            "no_route_authority": True,
            "no_retrieval_performed": True,
            "no_execution_performed": True,
            "no_write_performed": True,
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "visible_inputs_hash": self.visible_inputs_hash,
            "plan_bundle_hash": self.plan_bundle_hash,
            "initial_state_digest": self.initial_state_digest,
            "final_state_digest": self.final_state_digest,
            "pass_receipts": [p.to_dict() for p in self.pass_receipts],
            "quality_signals": self.quality_signals.to_dict() if self.quality_signals is not None else None,
            "non_authority_assertions": dict(self.non_authority_assertions),
        }


@dataclass(frozen=True)
class PlanningReasoningPacket:
    """02.3 § PHASE 2 — output of :func:`run_l1_reasoning_loop`."""

    internal_plan_state: InternalPlanState
    planning_loop_budget_receipt: PlanningLoopBudgetReceipt
    planning_reasoning_trace_summary: PlanningReasoningTraceSummary
    request_id: str
    trace_root: str
    output_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "internal_plan_state": self.internal_plan_state.to_dict(),
            "planning_loop_budget_receipt": self.planning_loop_budget_receipt.to_dict(),
            "planning_reasoning_trace_summary": self.planning_reasoning_trace_summary.to_dict(),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "output_digest": self.output_digest,
        }


# ---------------------------------------------------------------------------
# Stage 02.4 — Draft Plan & Route Hints
# ---------------------------------------------------------------------------


class WorkUnitType(str, Enum):
    INTERPRET = "interpret"
    SUMMARIZE = "summarize"
    COMPARE = "compare"
    TRANSFORM = "transform"
    CREATE_ARTIFACT = "create_artifact"
    EDIT_ARTIFACT = "edit_artifact"
    RETRIEVE_NEEDED = "retrieve_needed"
    PROPOSE_ACTION = "propose_action"
    EXECUTE_CANDIDATE = "execute_candidate"
    VALIDATE_OUTPUT = "validate_output"
    ESCALATE_CANDIDATE = "escalate_candidate"


class ProposedRouteHint(str, Enum):
    R1A_EXACT_CACHE = "R1A_EXACT_CACHE"
    R1B_SEMANTIC_CACHE = "R1B_SEMANTIC_CACHE"
    R3_GROUNDED_READ = "R3_GROUNDED_READ"
    R4_SINGLE_ACTION = "R4_SINGLE_ACTION"
    R3R4_MANAGED_WORKFLOW = "R3R4_MANAGED_WORKFLOW"
    R5_FALLBACK = "R5_FALLBACK"


@dataclass(frozen=True)
class WorkUnit:
    """02.4 § PHASE 1.2 — single advisory work unit."""

    work_unit_id: str
    description: str
    work_unit_type: WorkUnitType
    input_refs: tuple = ()
    output_refs: tuple = ()
    constraints: tuple = ()
    support_need: str = "none"
    action_need: str = "none"
    risk_marker: str = "low"
    dependency_refs: tuple = ()
    can_be_single_step: bool = True
    requires_external_action_hint: bool = False
    requires_grounding_hint: bool = False
    requires_artifact_output_hint: bool = False
    acceptance_criteria: tuple = ()
    stop_condition: str = ""

    def __post_init__(self) -> None:
        _require_str(self.work_unit_id, "work_unit_id")
        _require_str(self.description, "description")
        if not isinstance(self.work_unit_type, WorkUnitType):
            raise L1ContractViolation(f"work_unit_type must be WorkUnitType, got {type(self.work_unit_type)}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "work_unit_id": self.work_unit_id,
            "description": self.description,
            "work_unit_type": self.work_unit_type.value,
            "input_refs": list(self.input_refs),
            "output_refs": list(self.output_refs),
            "constraints": list(self.constraints),
            "support_need": self.support_need,
            "action_need": self.action_need,
            "risk_marker": self.risk_marker,
            "dependency_refs": list(self.dependency_refs),
            "can_be_single_step": self.can_be_single_step,
            "requires_external_action_hint": self.requires_external_action_hint,
            "requires_grounding_hint": self.requires_grounding_hint,
            "requires_artifact_output_hint": self.requires_artifact_output_hint,
            "acceptance_criteria": list(self.acceptance_criteria),
            "stop_condition": self.stop_condition,
        }


@dataclass(frozen=True)
class WorkUnitSet:
    """Ordered, deterministic set of work units."""

    units: tuple

    def __post_init__(self) -> None:
        if isinstance(self.units, str) or not hasattr(self.units, "__iter__"):
            raise L1ContractViolation("units must be a tuple of WorkUnit")
        for idx, u in enumerate(self.units):
            if not isinstance(u, WorkUnit):
                raise L1ContractViolation(f"units[{idx}] must be WorkUnit")
        if not self.units:
            raise L1ContractViolation("WorkUnitSet must contain at least one WorkUnit")
        seen_ids: set = set()
        for u in self.units:
            if u.work_unit_id in seen_ids:
                raise L1ContractViolation(f"duplicate work_unit_id: {u.work_unit_id!r}")
            seen_ids.add(u.work_unit_id)

    def to_dict(self) -> dict[str, Any]:
        return {"units": [u.to_dict() for u in self.units]}


@dataclass(frozen=True)
class DependencySketch:
    """02.4 § PHASE 1.3 — light-weight DAG sketch (not L3 contract)."""

    dependency_sketch_id: str
    sequential_edges: tuple = ()  # tuple of (from_id, to_id) tuples
    parallel_safe_groups: tuple = ()  # tuple of tuples of ids
    join_points: tuple = ()
    prerequisite_checks: tuple = ()
    stopping_points: tuple = ()
    retry_or_repair_posture: str = "advisory_only"
    l3_may_be_needed_reason: str = ""
    l3_not_needed_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "dependency_sketch_id": self.dependency_sketch_id,
            "sequential_edges": [list(e) for e in self.sequential_edges],
            "parallel_safe_groups": [list(g) for g in self.parallel_safe_groups],
            "join_points": list(self.join_points),
            "prerequisite_checks": list(self.prerequisite_checks),
            "stopping_points": list(self.stopping_points),
            "retry_or_repair_posture": self.retry_or_repair_posture,
            "l3_may_be_needed_reason": self.l3_may_be_needed_reason,
            "l3_not_needed_reason": self.l3_not_needed_reason,
        }


@dataclass(frozen=True)
class RouteHintSet:
    """02.4 § PHASE 1.4 — advisory route hint container."""

    route_hint_id: str
    proposed_route_hint: ProposedRouteHint
    reason_codes: tuple = ()
    confidence: float = 0.5
    route_risk: str = "low"
    fallback_chain_hint: tuple = ()
    single_step_or_workflow: str = "single_step"
    cache_eligibility_hint: bool = False
    grounding_hint: bool = False
    action_hint: bool = False
    hitl_hint: bool = False
    uwg_hint: bool = False
    cost_latency_sensitivity: str = "low"
    route_authority_assertion: str = "advisory_only"

    def __post_init__(self) -> None:
        if not isinstance(self.proposed_route_hint, ProposedRouteHint):
            raise L1ContractViolation("proposed_route_hint must be ProposedRouteHint enum")
        if not (0.0 <= float(self.confidence) <= 1.0):
            raise L1ContractViolation("confidence must be in [0.0, 1.0]")
        if self.route_authority_assertion != "advisory_only":
            raise L1ContractViolation(
                "route_authority_assertion must be 'advisory_only' (L1 cannot claim route authority)"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_hint_id": self.route_hint_id,
            "proposed_route_hint": self.proposed_route_hint.value,
            "reason_codes": list(self.reason_codes),
            "confidence": self.confidence,
            "route_risk": self.route_risk,
            "fallback_chain_hint": list(self.fallback_chain_hint),
            "single_step_or_workflow": self.single_step_or_workflow,
            "cache_eligibility_hint": self.cache_eligibility_hint,
            "grounding_hint": self.grounding_hint,
            "action_hint": self.action_hint,
            "hitl_hint": self.hitl_hint,
            "uwg_hint": self.uwg_hint,
            "cost_latency_sensitivity": self.cost_latency_sensitivity,
            "route_authority_assertion": self.route_authority_assertion,
        }


@dataclass(frozen=True)
class SupportExpectation:
    """02.4 § PHASE 1.5 — typed support expectation."""

    grounding_required: bool
    support_target: str = "none"
    evidence_classes: tuple = ()
    freshness_class: str = "stable"
    source_expectations: tuple = ()
    citation_mode_hint: str = "none"
    contradiction_policy: str = "abstain_if_unresolved"
    weak_support_policy: str = "caveat"
    cite_or_abstain_posture: str = "caveat"
    exact_span_needed: bool = False
    code_location_needed: bool = False
    policy_clause_needed: bool = False
    evidence_bundle_needed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "grounding_required": self.grounding_required,
            "support_target": self.support_target,
            "evidence_classes": list(self.evidence_classes),
            "freshness_class": self.freshness_class,
            "source_expectations": list(self.source_expectations),
            "citation_mode_hint": self.citation_mode_hint,
            "contradiction_policy": self.contradiction_policy,
            "weak_support_policy": self.weak_support_policy,
            "cite_or_abstain_posture": self.cite_or_abstain_posture,
            "exact_span_needed": self.exact_span_needed,
            "code_location_needed": self.code_location_needed,
            "policy_clause_needed": self.policy_clause_needed,
            "evidence_bundle_needed": self.evidence_bundle_needed,
        }


@dataclass(frozen=True)
class ActionExpectation:
    """02.4 § PHASE 1.6 — typed action expectation."""

    action_required: bool = False
    candidate_tool_class: str = "none"
    side_effect_class: str = "none"
    sandbox_need_hint: bool = False
    capability_token_need_hint: bool = False
    external_egress_hint: bool = False
    hitl_hint: bool = False
    uwg_hint: bool = False
    irreversible_action_marker: bool = False
    proposed_mutation_only_marker: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_required": self.action_required,
            "candidate_tool_class": self.candidate_tool_class,
            "side_effect_class": self.side_effect_class,
            "sandbox_need_hint": self.sandbox_need_hint,
            "capability_token_need_hint": self.capability_token_need_hint,
            "external_egress_hint": self.external_egress_hint,
            "hitl_hint": self.hitl_hint,
            "uwg_hint": self.uwg_hint,
            "irreversible_action_marker": self.irreversible_action_marker,
            "proposed_mutation_only_marker": self.proposed_mutation_only_marker,
        }


@dataclass(frozen=True)
class DownstreamPlanningNotes:
    """02.4 § PHASE 1.7 — per-consumer notes (no authoritative output)."""

    for_l0: tuple = ()
    for_c0: tuple = ()
    for_prompt_assembly: tuple = ()
    for_l2: tuple = ()
    for_exit_control: tuple = ()
    for_l6: tuple = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "for_l0": list(self.for_l0),
            "for_c0": list(self.for_c0),
            "for_prompt_assembly": list(self.for_prompt_assembly),
            "for_l2": list(self.for_l2),
            "for_exit_control": list(self.for_exit_control),
            "for_l6": list(self.for_l6),
        }


@dataclass(frozen=True)
class DraftPlanInput:
    """02.4 § PHASE 1.1 — typed draft-plan input."""

    intent_frame: IntentFrameSnapshot
    ambiguity_register: dict
    request_detail_inventory: RequestDetailInventory
    first_safety_authority_reading: FirstSafetyAuthorityReading
    plan_bundle: PlanBundleSnapshot
    rule_aware_planning_frame: dict
    internal_plan_state: InternalPlanState
    reasoning_trace_summary: PlanningReasoningTraceSummary
    request_id: str
    trace_root: str
    policy_hash_observed: str
    instruction_hash_observed: str
    replay_key_seed: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_frame": self.intent_frame.to_dict(),
            "ambiguity_register": dict(self.ambiguity_register),
            "request_detail_inventory": self.request_detail_inventory.to_dict(),
            "first_safety_authority_reading": self.first_safety_authority_reading.to_dict(),
            "plan_bundle": self.plan_bundle.to_dict(),
            "rule_aware_planning_frame": dict(self.rule_aware_planning_frame),
            "internal_plan_state": self.internal_plan_state.to_dict(),
            "reasoning_trace_summary": self.reasoning_trace_summary.to_dict(),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "replay_key_seed": self.replay_key_seed,
        }


@dataclass(frozen=True)
class DraftPlan:
    """02.4 § PHASE 1.8 — frozen draft plan."""

    draft_plan_id: str
    work_unit_set: WorkUnitSet
    dependency_sketch: DependencySketch
    route_hint_set: RouteHintSet
    support_expectation: SupportExpectation
    action_expectation: ActionExpectation
    downstream_planning_notes: DownstreamPlanningNotes
    draft_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "draft_plan_id": self.draft_plan_id,
            "work_unit_set": self.work_unit_set.to_dict(),
            "dependency_sketch": self.dependency_sketch.to_dict(),
            "route_hint_set": self.route_hint_set.to_dict(),
            "support_expectation": self.support_expectation.to_dict(),
            "action_expectation": self.action_expectation.to_dict(),
            "downstream_planning_notes": self.downstream_planning_notes.to_dict(),
            "draft_digest": self.draft_digest,
        }


@dataclass(frozen=True)
class DraftPlanPacket:
    """02.4 § PHASE 2 — output of :func:`write_draft_plan`."""

    draft_plan: DraftPlan
    request_id: str
    trace_root: str
    output_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "draft_plan": self.draft_plan.to_dict(),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "output_digest": self.output_digest,
        }


# ---------------------------------------------------------------------------
# Stage 02.5 — Plan Validation & Self-Repair
# ---------------------------------------------------------------------------


class AmbiguitySeverity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    NOT_RUN = "not_run"


class RepairAction(str, Enum):
    REPAIR_DROPPED_CONSTRAINT = "repair_dropped_constraint"
    REPAIR_MISSING_OUTPUT_TARGET = "repair_missing_output_target"
    REPAIR_UNSAFE_ROUTE_HINT = "repair_unsafe_route_hint"
    REPAIR_UNCLEAR_SUPPORT_EXPECTATION = "repair_unclear_support_expectation"
    REPAIR_OVERBROAD_ACTION_ASSUMPTION = "repair_overbroad_action_assumption"
    REPAIR_MISSING_FALLBACK = "repair_missing_fallback"
    REPAIR_MISSING_HITL_OR_UWG_HINT = "repair_missing_hitl_or_uwg_hint"
    REPAIR_UNNECESSARY_WORKFLOW = "repair_unnecessary_workflow"
    REPAIR_EXCESSIVE_CLARIFICATION = "repair_excessive_clarification"
    REPAIR_UNSUPPORTED_CERTAINTY = "repair_unsupported_certainty"
    NO_ACTION = "no_action"


@dataclass(frozen=True)
class PlanValidationInput:
    """02.5 § PHASE 1.1 — typed validation input."""

    draft_plan: DraftPlan
    intent_frame: IntentFrameSnapshot
    ambiguity_register: dict
    first_safety_authority_reading: FirstSafetyAuthorityReading
    request_id: str
    trace_root: str
    policy_hash_observed: str
    instruction_hash_observed: str
    max_self_repair_passes: int = 2
    replay_key_seed: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "draft_plan": self.draft_plan.to_dict(),
            "intent_frame": self.intent_frame.to_dict(),
            "ambiguity_register": dict(self.ambiguity_register),
            "first_safety_authority_reading": self.first_safety_authority_reading.to_dict(),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "max_self_repair_passes": self.max_self_repair_passes,
            "replay_key_seed": self.replay_key_seed,
        }


@dataclass(frozen=True)
class PlanValidationReport:
    """02.5 § PHASE 1.2 — typed validation report."""

    report_id: str
    listened_to_user_status: ValidationStatus
    constraints_preserved_status: ValidationStatus
    deliverable_fit_status: ValidationStatus
    style_format_fit_status: ValidationStatus
    safety_checked_status: ValidationStatus
    coherent_plan_status: ValidationStatus
    route_hint_consistency_status: ValidationStatus
    support_expectation_status: ValidationStatus
    action_expectation_status: ValidationStatus
    lowest_viable_agency_status: ValidationStatus
    no_execution_authority_asserted: bool = True
    no_retrieval_performed: bool = True
    no_write_performed: bool = True
    validation_failures: tuple = ()
    validation_warnings: tuple = ()
    report_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "listened_to_user_status": self.listened_to_user_status.value,
            "constraints_preserved_status": self.constraints_preserved_status.value,
            "deliverable_fit_status": self.deliverable_fit_status.value,
            "style_format_fit_status": self.style_format_fit_status.value,
            "safety_checked_status": self.safety_checked_status.value,
            "coherent_plan_status": self.coherent_plan_status.value,
            "route_hint_consistency_status": self.route_hint_consistency_status.value,
            "support_expectation_status": self.support_expectation_status.value,
            "action_expectation_status": self.action_expectation_status.value,
            "lowest_viable_agency_status": self.lowest_viable_agency_status.value,
            "no_execution_authority_asserted": self.no_execution_authority_asserted,
            "no_retrieval_performed": self.no_retrieval_performed,
            "no_write_performed": self.no_write_performed,
            "validation_failures": list(self.validation_failures),
            "validation_warnings": list(self.validation_warnings),
            "report_digest": self.report_digest,
        }

    def is_pass(self) -> bool:
        for s in (
            self.listened_to_user_status,
            self.constraints_preserved_status,
            self.deliverable_fit_status,
            self.style_format_fit_status,
            self.safety_checked_status,
            self.coherent_plan_status,
            self.route_hint_consistency_status,
            self.support_expectation_status,
            self.action_expectation_status,
            self.lowest_viable_agency_status,
        ):
            if s == ValidationStatus.FAIL:
                return False
        return True


@dataclass(frozen=True)
class PlanConsistencyAudit:
    """02.5 § PHASE 1.3 — consistency-check checklist."""

    cache_hint_freshness_consistent: bool = True
    grounded_read_marks_c0: bool = True
    single_action_bounded: bool = True
    managed_workflow_justified: bool = True
    fallback_reason_present: bool = True
    durable_mutation_marks_uwg: bool = True
    high_risk_marks_hitl: bool = True
    confidence_matches_evidence: bool = True
    full_overwrite_preserves_structure: bool = True
    findings: tuple = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "cache_hint_freshness_consistent": self.cache_hint_freshness_consistent,
            "grounded_read_marks_c0": self.grounded_read_marks_c0,
            "single_action_bounded": self.single_action_bounded,
            "managed_workflow_justified": self.managed_workflow_justified,
            "fallback_reason_present": self.fallback_reason_present,
            "durable_mutation_marks_uwg": self.durable_mutation_marks_uwg,
            "high_risk_marks_hitl": self.high_risk_marks_hitl,
            "confidence_matches_evidence": self.confidence_matches_evidence,
            "full_overwrite_preserves_structure": self.full_overwrite_preserves_structure,
            "findings": list(self.findings),
        }

    def all_consistent(self) -> bool:
        return all(
            (
                self.cache_hint_freshness_consistent,
                self.grounded_read_marks_c0,
                self.single_action_bounded,
                self.managed_workflow_justified,
                self.fallback_reason_present,
                self.durable_mutation_marks_uwg,
                self.high_risk_marks_hitl,
                self.confidence_matches_evidence,
                self.full_overwrite_preserves_structure,
            )
        )


@dataclass(frozen=True)
class LowestViableAgencyReceipt:
    """02.5 § PHASE 1.4 — lowest-viable-agency reduction receipt."""

    receipt_id: str
    original_complexity_class: str
    reduced_complexity_class: str
    direct_answer_possible: bool = False
    grounded_read_needed: bool = False
    single_action_sufficient: bool = False
    managed_workflow_justified: bool = False
    workflow_removed_reason: str = ""
    tool_use_removed_reason: str = ""
    clarification_removed_reason: str = ""
    final_agency_recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "original_complexity_class": self.original_complexity_class,
            "reduced_complexity_class": self.reduced_complexity_class,
            "direct_answer_possible": self.direct_answer_possible,
            "grounded_read_needed": self.grounded_read_needed,
            "single_action_sufficient": self.single_action_sufficient,
            "managed_workflow_justified": self.managed_workflow_justified,
            "workflow_removed_reason": self.workflow_removed_reason,
            "tool_use_removed_reason": self.tool_use_removed_reason,
            "clarification_removed_reason": self.clarification_removed_reason,
            "final_agency_recommendation": self.final_agency_recommendation,
        }


@dataclass(frozen=True)
class L1SelfRepairLedger:
    """02.5 § PHASE 1.5 — bounded self-repair ledger."""

    ledger_id: str
    max_passes: int
    passes_used: int
    repairs_attempted: tuple = ()
    repairs_accepted: tuple = ()
    repairs_rejected: tuple = ()
    unresolved_failures: tuple = ()
    stop_reason: str = ""
    no_tool_rescue_assertion: bool = True
    no_retrieval_rescue_assertion: bool = True
    no_route_commit_assertion: bool = True

    def __post_init__(self) -> None:
        if self.passes_used > self.max_passes:
            raise L1ContractViolation("passes_used must not exceed max_passes")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger_id": self.ledger_id,
            "max_passes": self.max_passes,
            "passes_used": self.passes_used,
            "repairs_attempted": [
                a.value if isinstance(a, RepairAction) else a for a in self.repairs_attempted
            ],
            "repairs_accepted": [
                a.value if isinstance(a, RepairAction) else a for a in self.repairs_accepted
            ],
            "repairs_rejected": [
                a.value if isinstance(a, RepairAction) else a for a in self.repairs_rejected
            ],
            "unresolved_failures": list(self.unresolved_failures),
            "stop_reason": self.stop_reason,
            "no_tool_rescue_assertion": self.no_tool_rescue_assertion,
            "no_retrieval_rescue_assertion": self.no_retrieval_rescue_assertion,
            "no_route_commit_assertion": self.no_route_commit_assertion,
        }


@dataclass(frozen=True)
class ClarifyAbstainFallbackMarker:
    """02.5 § PHASE 1.6 — clarify/abstain/fallback recommendation."""

    marker_id: str
    clarify_recommended: bool = False
    clarify_question: str = ""
    abstain_recommended: bool = False
    fallback_recommended: bool = False
    policy_review_recommended: bool = False
    reason_codes: tuple = ()
    critical_gap_refs: tuple = ()
    unsafe_completion_refs: tuple = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "marker_id": self.marker_id,
            "clarify_recommended": self.clarify_recommended,
            "clarify_question": self.clarify_question,
            "abstain_recommended": self.abstain_recommended,
            "fallback_recommended": self.fallback_recommended,
            "policy_review_recommended": self.policy_review_recommended,
            "reason_codes": list(self.reason_codes),
            "critical_gap_refs": list(self.critical_gap_refs),
            "unsafe_completion_refs": list(self.unsafe_completion_refs),
        }

    def is_active(self) -> bool:
        return any(
            (
                self.clarify_recommended,
                self.abstain_recommended,
                self.fallback_recommended,
                self.policy_review_recommended,
            )
        )


@dataclass(frozen=True)
class FinalPlanReadinessReceipt:
    """02.5 § PHASE 1.7 — readiness receipt for handoff."""

    receipt_id: str
    plan_ready_for_handoff: bool
    final_plan_status: str
    validation_pass: bool
    self_repair_used: bool
    clarify_or_abstain_recommended: bool
    notes: tuple = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "plan_ready_for_handoff": self.plan_ready_for_handoff,
            "final_plan_status": self.final_plan_status,
            "validation_pass": self.validation_pass,
            "self_repair_used": self.self_repair_used,
            "clarify_or_abstain_recommended": self.clarify_or_abstain_recommended,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class ValidatedPlanPacket:
    """02.5 § PHASE 2 — output of :func:`validate_and_repair_l1_plan`."""

    final_draft_plan: DraftPlan
    plan_validation_report: PlanValidationReport
    plan_consistency_audit: PlanConsistencyAudit
    lowest_viable_agency_receipt: LowestViableAgencyReceipt
    self_repair_ledger: L1SelfRepairLedger
    clarify_abstain_fallback_marker: ClarifyAbstainFallbackMarker
    final_plan_readiness_receipt: FinalPlanReadinessReceipt
    request_id: str
    trace_root: str
    output_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "final_draft_plan": self.final_draft_plan.to_dict(),
            "plan_validation_report": self.plan_validation_report.to_dict(),
            "plan_consistency_audit": self.plan_consistency_audit.to_dict(),
            "lowest_viable_agency_receipt": self.lowest_viable_agency_receipt.to_dict(),
            "self_repair_ledger": self.self_repair_ledger.to_dict(),
            "clarify_abstain_fallback_marker": self.clarify_abstain_fallback_marker.to_dict(),
            "final_plan_readiness_receipt": self.final_plan_readiness_receipt.to_dict(),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "output_digest": self.output_digest,
        }


# ---------------------------------------------------------------------------
# Stage 02.6 — L1PlanContract & Handoff
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuerySpec:
    """02.6 § PHASE 1.3 — typed query spec."""

    normalized_request: str
    entities: tuple = ()
    aliases: tuple = ()
    terms: tuple = ()
    files_or_sources: tuple = ()
    connectors: tuple = ()
    uploaded_file_expectations: tuple = ()
    dates_or_versions: tuple = ()
    freshness_class: str = "stable"
    source_expectations: tuple = ()
    support_need: str = "none"
    currentness_mandatory: bool = False
    citation_or_exact_span_may_be_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "normalized_request": self.normalized_request,
            "entities": list(self.entities),
            "aliases": list(self.aliases),
            "terms": list(self.terms),
            "files_or_sources": list(self.files_or_sources),
            "connectors": list(self.connectors),
            "uploaded_file_expectations": list(self.uploaded_file_expectations),
            "dates_or_versions": list(self.dates_or_versions),
            "freshness_class": self.freshness_class,
            "source_expectations": list(self.source_expectations),
            "support_need": self.support_need,
            "currentness_mandatory": self.currentness_mandatory,
            "citation_or_exact_span_may_be_required": self.citation_or_exact_span_may_be_required,
        }


@dataclass(frozen=True)
class TaskSpec:
    """02.6 § PHASE 1.4 — typed task spec."""

    work_units: tuple
    output_target: str
    output_format: str
    structure_requirements: tuple = ()
    style_constraints: tuple = ()
    acceptance_criteria: tuple = ()
    stop_condition: str = ""
    expected_length_or_depth: str = ""
    artifact_packaging_requirement: str = ""
    partial_completion_allowed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "work_units": list(self.work_units),
            "output_target": self.output_target,
            "output_format": self.output_format,
            "structure_requirements": list(self.structure_requirements),
            "style_constraints": list(self.style_constraints),
            "acceptance_criteria": list(self.acceptance_criteria),
            "stop_condition": self.stop_condition,
            "expected_length_or_depth": self.expected_length_or_depth,
            "artifact_packaging_requirement": self.artifact_packaging_requirement,
            "partial_completion_allowed": self.partial_completion_allowed,
        }


@dataclass(frozen=True)
class PlanReplayManifest:
    """02.6 § PHASE 1.5 — replay manifest."""

    manifest_id: str
    normalized_request_hash: str
    visible_context_hash: str
    intent_frame_hash: str
    plan_bundle_hash: str
    internal_plan_state_hash: str
    draft_plan_hash: str
    validation_report_hash: str
    policy_hash: str
    instruction_hash: str
    source_envelope_id: str
    deterministic_digest_algorithm: str = DETERMINISTIC_DIGEST_ALGORITHM
    excluded_volatile_fields: tuple = (
        "wall_clock_time",
        "nondeterministic_memory_ids",
        "transient_span_ids",
        "provider_latency",
        "local_filesystem_temp_names",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "normalized_request_hash": self.normalized_request_hash,
            "visible_context_hash": self.visible_context_hash,
            "intent_frame_hash": self.intent_frame_hash,
            "plan_bundle_hash": self.plan_bundle_hash,
            "internal_plan_state_hash": self.internal_plan_state_hash,
            "draft_plan_hash": self.draft_plan_hash,
            "validation_report_hash": self.validation_report_hash,
            "policy_hash": self.policy_hash,
            "instruction_hash": self.instruction_hash,
            "source_envelope_id": self.source_envelope_id,
            "deterministic_digest_algorithm": self.deterministic_digest_algorithm,
            "excluded_volatile_fields": list(self.excluded_volatile_fields),
        }


@dataclass(frozen=True)
class NonAuthorityAssertion:
    """02.6 § PHASE 1.6 — all flags must be True for handoff."""

    no_evidence_retrieval: bool = True
    no_final_route_commitment: bool = True
    no_tool_execution: bool = True
    no_model_execution_for_work: bool = True
    no_durable_state_mutation: bool = True
    no_external_provider_call_for_work: bool = True
    no_final_egress_approval: bool = True
    no_hitl_approval: bool = True
    no_uwg_commit: bool = True
    no_learning_promotion: bool = True

    def __post_init__(self) -> None:
        for fname in (
            "no_evidence_retrieval",
            "no_final_route_commitment",
            "no_tool_execution",
            "no_model_execution_for_work",
            "no_durable_state_mutation",
            "no_external_provider_call_for_work",
            "no_final_egress_approval",
            "no_hitl_approval",
            "no_uwg_commit",
            "no_learning_promotion",
        ):
            if not getattr(self, fname):
                raise L1ContractViolation(f"NonAuthorityAssertion.{fname} must be True for L1 handoff")

    def to_dict(self) -> dict[str, Any]:
        return {
            "no_evidence_retrieval": self.no_evidence_retrieval,
            "no_final_route_commitment": self.no_final_route_commitment,
            "no_tool_execution": self.no_tool_execution,
            "no_model_execution_for_work": self.no_model_execution_for_work,
            "no_durable_state_mutation": self.no_durable_state_mutation,
            "no_external_provider_call_for_work": self.no_external_provider_call_for_work,
            "no_final_egress_approval": self.no_final_egress_approval,
            "no_hitl_approval": self.no_hitl_approval,
            "no_uwg_commit": self.no_uwg_commit,
            "no_learning_promotion": self.no_learning_promotion,
        }


@dataclass(frozen=True)
class L1TelemetryKeySet:
    """02.6 § PHASE 1.7 — telemetry key set carried with handoff."""

    request_id: str
    trace_root: str
    l1_plan_id: str
    plan_digest: str
    span_names: tuple = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "l1_plan_id": self.l1_plan_id,
            "plan_digest": self.plan_digest,
            "span_names": list(self.span_names),
        }


@dataclass(frozen=True)
class L1HandoffReceipt:
    """02.6 § PHASE 1.8 — handoff receipt to L0."""

    handoff_receipt_id: str
    l1_plan_id: str
    target_layer: str
    handoff_time_policy: str
    plan_digest: str
    trace_root: str
    request_id: str
    readiness_status: str
    non_authority_assertion_ref: str
    telemetry_keys: tuple = ()

    def __post_init__(self) -> None:
        if self.target_layer != "L0_ROUTE_DECISION":
            raise L1ContractViolation("target_layer must be 'L0_ROUTE_DECISION' for the L1 handoff")

    def to_dict(self) -> dict[str, Any]:
        return {
            "handoff_receipt_id": self.handoff_receipt_id,
            "l1_plan_id": self.l1_plan_id,
            "target_layer": self.target_layer,
            "handoff_time_policy": self.handoff_time_policy,
            "plan_digest": self.plan_digest,
            "trace_root": self.trace_root,
            "request_id": self.request_id,
            "readiness_status": self.readiness_status,
            "non_authority_assertion_ref": self.non_authority_assertion_ref,
            "telemetry_keys": list(self.telemetry_keys),
        }


@dataclass(frozen=True)
class L1PlanContractInput:
    """02.6 § PHASE 1.1 — typed contract-build input."""

    validated_plan_packet: ValidatedPlanPacket
    intent_frame: IntentFrameSnapshot
    query_spec: Optional[QuerySpec]
    task_spec: TaskSpec
    route_hint_set: RouteHintSet
    support_expectation: SupportExpectation
    action_expectation: ActionExpectation
    assumptions_and_gaps: dict
    validation_summary: dict
    downstream_notes: DownstreamPlanningNotes
    request_id: str
    session_id: str
    trace_root: str
    policy_hash_observed: str
    instruction_hash_observed: str
    source_envelope_id: str
    replay_key_seed: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "validated_plan_packet": self.validated_plan_packet.to_dict(),
            "intent_frame": self.intent_frame.to_dict(),
            "query_spec": self.query_spec.to_dict() if self.query_spec else None,
            "task_spec": self.task_spec.to_dict(),
            "route_hint_set": self.route_hint_set.to_dict(),
            "support_expectation": self.support_expectation.to_dict(),
            "action_expectation": self.action_expectation.to_dict(),
            "assumptions_and_gaps": dict(self.assumptions_and_gaps),
            "validation_summary": dict(self.validation_summary),
            "downstream_notes": self.downstream_notes.to_dict(),
            "request_id": self.request_id,
            "session_id": self.session_id,
            "trace_root": self.trace_root,
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "source_envelope_id": self.source_envelope_id,
            "replay_key_seed": self.replay_key_seed,
        }


@dataclass(frozen=True)
class PlanDigest:
    """02.6 § PHASE 1.9 — frozen deterministic plan digest."""

    digest: str
    algorithm: str = DETERMINISTIC_DIGEST_ALGORITHM

    def to_dict(self) -> dict[str, Any]:
        return {"digest": self.digest, "algorithm": self.algorithm}


@dataclass(frozen=True)
class L1PlanContract:
    """02.6 § PHASE 1.2 — canonical L1 plan contract.

    This is the v6 doctrine envelope. It is **not** a replacement for
    :class:`agentic_core.L1_cognition.types.plan_contract_types.L1PlanContractV2`;
    the v2 contract remains the in-memory authority for the v4/v5 layer.
    The v6 contract carries v6-canonical sections plus an opaque
    ``v2_projection`` field for callers that still want the v2 shape.
    """

    layer: str
    version: str
    authority: str
    identity: dict
    intent_frame: dict
    query_spec: Optional[dict]
    task_spec: dict
    route_hint: dict
    support_expectation: dict
    action_expectation: dict
    assumptions_and_gaps: dict
    validation_summary: dict
    downstream_notes: dict
    plan_replay_manifest: dict
    plan_digest: PlanDigest
    non_authority_assertion: NonAuthorityAssertion
    v2_projection: Optional[dict] = None

    def __post_init__(self) -> None:
        if self.layer != "L1_REASONING_PLAN_GENERATION":
            raise L1ContractViolation("layer must be 'L1_REASONING_PLAN_GENERATION'")
        if self.authority != "advisory_plan_only":
            raise L1ContractViolation("authority must be 'advisory_plan_only'")
        # validation_summary must positively assert L1's invariants.
        for fname in (
            "no_retrieval_performed",
            "no_execution_performed",
            "no_write_performed",
        ):
            if not self.validation_summary.get(fname):
                raise L1ContractViolation(f"validation_summary.{fname} must be True on the v6 contract")
        if "route_digest" in self.route_hint or "hmac_sig" in self.route_hint:
            raise L1ContractViolation(
                "route_hint must not contain route_digest or hmac_sig (L0 owns route authority)"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "version": self.version,
            "authority": self.authority,
            "identity": dict(self.identity),
            "intent_frame": dict(self.intent_frame),
            "query_spec": dict(self.query_spec) if self.query_spec else None,
            "task_spec": dict(self.task_spec),
            "route_hint": dict(self.route_hint),
            "support_expectation": dict(self.support_expectation),
            "action_expectation": dict(self.action_expectation),
            "assumptions_and_gaps": dict(self.assumptions_and_gaps),
            "validation_summary": dict(self.validation_summary),
            "downstream_notes": dict(self.downstream_notes),
            "plan_replay_manifest": dict(self.plan_replay_manifest),
            "plan_digest": self.plan_digest.to_dict(),
            "non_authority_assertion": self.non_authority_assertion.to_dict(),
            "v2_projection": dict(self.v2_projection) if self.v2_projection else None,
        }


@dataclass(frozen=True)
class L1PlanHandoffPacket:
    """02.6 § PHASE 2 — output of :func:`emit_l1_plan_contract`."""

    l1_plan_contract: L1PlanContract
    l1_handoff_receipt: L1HandoffReceipt
    l1_telemetry_key_set: L1TelemetryKeySet
    plan_digest: PlanDigest
    request_id: str
    trace_root: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "l1_plan_contract": self.l1_plan_contract.to_dict(),
            "l1_handoff_receipt": self.l1_handoff_receipt.to_dict(),
            "l1_telemetry_key_set": self.l1_telemetry_key_set.to_dict(),
            "plan_digest": self.plan_digest.to_dict(),
            "request_id": self.request_id,
            "trace_root": self.trace_root,
        }


# ---------------------------------------------------------------------------
# Internal-only helper: ensure stable_digest is available for stages.
# ---------------------------------------------------------------------------

# Re-export for convenience (so stage modules can `from .contracts import
# stable_digest` if they prefer). Functional behaviour identical to the
# helper in :mod:`.digests`.
__all__ += ["stable_digest", "DETERMINISTIC_DIGEST_ALGORITHM"]


# Provide a tiny convenience type for callers that already produced an
# :class:`L1PlanContractV2` — they can attach it to the v6 contract via
# the ``v2_projection`` field.
def project_v2_contract(v2: L1PlanContractV2) -> dict[str, Any]:
    """Render a v2 L1PlanContract as a dict for the v6 ``v2_projection``."""
    if not isinstance(v2, L1PlanContractV2):
        raise L1ContractViolation(f"project_v2_contract expects L1PlanContractV2, got {type(v2)}")
    return v2.to_dict()


__all__ += ["project_v2_contract"]
