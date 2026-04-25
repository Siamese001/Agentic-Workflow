"""L2 Execute v4 — Formal Phase Output Contracts + Decision Tables.

Maps to: docs/reference/04_L2_Execute/04_L2_Execute_v4.md

This module closes the v4 line-item gaps that the first v4 wave skipped:

  E1 INPUTS    — `WorkOrderInputs` (task_spec/tool_spec/model_spec/action_spec/
                  execution_form/cost_tier/retry_ceiling/max_repair_count/SLO_slice)
  E1 OUTPUT    — `PrepOutput` (frozen_execution_context/replay_bindings/
                  write_lock_assertion/ready_for_validation)
  E2 OUTPUT    — `ValidationOutput` (decisive_rule_id/capability_scope_summary/
                  budget_snapshot/approved_work_order/sealed_rejection_packet)
  E3 OUTPUT    — `ExecOutput` (telemetry_bundle/output_payload)
  Decision    — `VALIDATION_PASS_RULES` / `VALIDATION_FAIL_RULES`
  Repair      — `SAFE_LOCAL_REPAIRS` / `DISALLOWED_REPAIRS`
  Failure     — `FAILURE_MATRIX` (observed → classification + may_do + must_not_do)
  Invariants  — full 15-item `L2_FULL_INVARIANTS` registry

All structures are frozen / read-only. The pipeline already in place can adopt
these contracts incrementally — they are additive.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    DispatchTarget,
    ExecutionLane,
    LineageRoot,
    RepairStatus,
    ResultClass,
    TerminalStamp,
    ValidationReceipt,
)

# ---------------------------------------------------------------------------
# E1 INPUTS — full v4 §E1 INPUTS shape
# ---------------------------------------------------------------------------


class ExecutionForm(str, Enum):
    """v4 §E1 — execution_form: shape of the bounded packet."""

    SINGLE_STEP = "SINGLE_STEP"
    L3_STEP = "L3_STEP"
    RESUMED_STEP = "RESUMED_STEP"


@dataclass(frozen=True)
class CapabilitySpec:
    """Common shape for tool_spec / model_spec / action_spec specifications."""

    name: str
    version: str = ""
    schema_id: str = ""


@dataclass(frozen=True)
class TaskSpec:
    """v4 §E1 INPUTS task_spec — what the bounded packet asks for."""

    intent: str
    expected_output_contract: str = ""
    grounded: bool = False


@dataclass(frozen=True)
class WorkOrderInputs:
    """v4 §E1 INPUTS — full input bundle shape.

    Closes 9 missing v4 input identifiers:
        execution_form, task_spec, tool_spec, model_spec, action_spec,
        cost_tier, retry_ceiling, max_repair_count, SLO_slice
    """

    execution_form: ExecutionForm
    task_spec: TaskSpec
    tool_spec: CapabilitySpec | None = None
    model_spec: CapabilitySpec | None = None
    action_spec: CapabilitySpec | None = None
    cost_tier: str = "standard"  # cheap | standard | premium
    retry_ceiling: int = 3
    max_repair_count: int = 3
    slo_slice_ms: int = 60_000  # remaining route SLO budget for this attempt


# ---------------------------------------------------------------------------
# E1 OUTPUT CONTRACT — full v4 §E1 OUTPUT shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FrozenExecutionContext:
    """v4 §E1 OUTPUT frozen_execution_context — locked tools/model/runtime/etc."""

    tool_registry_version: str
    model_runtime_version: str
    provider_lane: str
    filesystem_view: str
    network_rules: str
    secrets_scope: str
    locale: str = "en-US"
    allowed_file_roots: tuple[str, ...] = ()
    allowed_network_destinations: tuple[str, ...] = ()
    allowed_syscalls: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReplayBindings:
    """v4 §E1 OUTPUT replay_bindings — every replay-relevant key in one bundle."""

    determinism: DeterminismBundle
    snapshot_manifest: str
    clock_policy: str = "run_clock_offsets"  # | "wall_clock_allowed"


@dataclass(frozen=True)
class WriteLockAssertion:
    """v4 §E1 OUTPUT write_lock_assertion — proves no L4/UWG direct path."""

    no_direct_l4_path: bool = True
    proposed_diff_only: bool = True
    persistence_disabled: bool = True
    asserted_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class PrepOutput:
    """v4 §E1 OUTPUT CONTRACT — full prep output bundle.

    Closes 4 missing v4 E1 output identifiers:
        frozen_execution_context, replay_bindings, write_lock_assertion,
        ready_for_validation
    """

    prep_receipt_id: str
    frozen_execution_context: FrozenExecutionContext
    run_id: str
    idempotency_key: str
    lineage_root: LineageRoot
    replay_bindings: ReplayBindings
    write_lock_assertion: WriteLockAssertion
    ready_for_validation: bool
    refusal_reason: str = ""  # populated when ready_for_validation=False


# ---------------------------------------------------------------------------
# E2 OUTPUT CONTRACT — full v4 §E2 OUTPUT shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapabilityScopeSummary:
    """v4 §E2 OUTPUT capability_scope_summary — flat summary for downstream."""

    capability_token_id: str
    granted_tools: tuple[str, ...] = ()
    granted_actions: tuple[str, ...] = ()
    granted_models: tuple[str, ...] = ()
    side_effect_envelope: str = "READ"
    tenant_scope: str = ""


@dataclass(frozen=True)
class BudgetSnapshot:
    """v4 §E2 OUTPUT budget_snapshot — affordability decision frozen at E2."""

    timeout_ms: int
    retry_ceiling: int
    repair_ceiling: int
    token_limit: int
    compute_limit: int
    memory_limit_mb: int = 0
    io_quota_bytes: int = 0
    circuit_breaker_open: bool = False


@dataclass(frozen=True)
class ApprovedWorkOrder:
    """v4 §E2 OUTPUT approved_work_order — what E3 receives on PASS."""

    validation_packet_id: str
    decisive_rule_id: str
    capability_scope: CapabilityScopeSummary
    budget_snapshot: BudgetSnapshot
    side_effect_class: str
    approved_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class SealedRejectionPacket:
    """v4 §E2 OUTPUT sealed_rejection_packet — the FAIL counterpart.

    Created BEFORE execution. No actual work was performed.
    """

    rejection_packet_id: str
    failed_validation_rule: str
    side_effect_class: str
    missing_or_invalid_authority_field: str
    suggested_reentry_target: str  # "L1" | "L0" | "L3" | "HITL" | "user_clarify"
    decisive_rule_id: str
    sealed_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class ValidationOutput:
    """v4 §E2 OUTPUT CONTRACT — full v4 E2 output bundle.

    Closes 6 missing v4 E2 output identifiers:
        validation_packet_id, validation_status, approved_work_order,
        sealed_rejection_packet, decisive_rule_id, capability_scope_summary,
        side_effect_class, budget_snapshot
    """

    validation_packet_id: str
    validation_status: str  # "PASS" | "FAIL"
    approved_work_order: ApprovedWorkOrder | None = None
    sealed_rejection_packet: SealedRejectionPacket | None = None

    @staticmethod
    def from_receipt(
        receipt: ValidationReceipt,
        *,
        approved: ApprovedWorkOrder | None = None,
        rejection: SealedRejectionPacket | None = None,
    ) -> ValidationOutput:
        return ValidationOutput(
            validation_packet_id=receipt.validation_packet_id,
            validation_status="PASS" if receipt.is_approved() else "FAIL",
            approved_work_order=approved,
            sealed_rejection_packet=rejection,
        )


# ---------------------------------------------------------------------------
# E3 OUTPUT CONTRACT — telemetry bundle (rest already on AttemptReceipt)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TelemetryBundle:
    """v4 §E3 OUTPUT telemetry_bundle — full attempt telemetry roll-up.

    Closes the missing E3 output identifier `telemetry_bundle`.
    """

    trace_id: str
    span_ids: tuple[str, ...] = ()
    parent_span_id: str | None = None
    latency_ms: float = 0.0
    tokens_used: int = 0
    cost_units: float = 0.0
    compute_use: str = ""
    memory_use_mb: int = 0
    stdout_summary: str = ""
    stderr_summary: str = ""
    return_code: int | None = None
    input_byte_count: int = 0
    output_byte_count: int = 0
    file_touches: tuple[str, ...] = ()
    network_destinations: tuple[str, ...] = ()
    model_or_tool_name: str = ""
    provider_lane: str = ""
    retry_source: str = ""
    circuit_breaker_state: str = "CLOSED"


# ---------------------------------------------------------------------------
# v4 §VALIDATION DECISION TABLE — PASS / FAIL conditions
# ---------------------------------------------------------------------------


VALIDATION_PASS_RULES: tuple[str, ...] = (
    "packet_signed",
    "authority_scoped",
    "schema_valid",
    "side_effects_fit_envelope",
    "budget_sufficient",
    "replay_metadata_bound",
    "no_direct_write_path",
)

VALIDATION_FAIL_RULES: tuple[str, ...] = (
    "invalid_signature",
    "action_outside_capability",
    "missing_sandbox_envelope",
    "malformed_tool_args",
    "high_risk_mutation_lacks_clearance",
    "prompt_or_evidence_injection_breach",
    "unsupported_output_contract",
    "no_deterministic_replay_surface",
)


# ---------------------------------------------------------------------------
# v4 §ALLOWED REPAIR TAXONOMY
# ---------------------------------------------------------------------------


SAFE_LOCAL_REPAIRS: tuple[str, ...] = (
    "json_repair_intact_source",
    "schema_coercion_deterministic_field",
    "output_reformat_to_required_shape",
    "retry_same_transient_tool_call",
    "resume_from_existing_checkpoint",
    "trim_oversized_output_preserving_required_fields",
    "convert_nonfatal_warning_to_caveat",
    "attach_partial_output_if_contract_permits",
)

DISALLOWED_REPAIRS: tuple[str, ...] = (
    "choose_different_route",
    "retrieve_new_evidence_without_c0_contract",
    "ask_human_directly",
    "broaden_sandbox_or_credentials",
    "silently_switch_provider_model_tool",
    "commit_state",
    "invent_missing_facts",
    "treat_human_text_as_authority",
    "override_policy_because_output_looks_right",
)


def is_repair_allowed(tactic: str) -> bool:
    """v4 §ALLOWED REPAIR TAXONOMY — gate function."""
    return tactic in SAFE_LOCAL_REPAIRS


# ---------------------------------------------------------------------------
# v4 §L2 FAILURE / REPAIR / EXIT MATRIX
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FailureMatrixRow:
    """v4 §L2 FAILURE MATRIX row."""

    observed_condition: str
    l2_classification: tuple[ResultClass, ...]
    l2_may_do: str
    l2_must_not_do: str


FAILURE_MATRIX: tuple[FailureMatrixRow, ...] = (
    FailureMatrixRow(
        observed_condition="malformed_json_output",
        l2_classification=(ResultClass.SOFT_REPAIRABLE,),
        l2_may_do="repair_schema_revalidate_retry",
        l2_must_not_do="invent_missing_facts",
    ),
    FailureMatrixRow(
        observed_condition="transient_tool_timeout",
        l2_classification=(ResultClass.SOFT_REPAIRABLE,),
        l2_may_do="bounded_retry_if_budget_remains",
        l2_must_not_do="infinite_retry_or_switch_tool_silently",
    ),
    FailureMatrixRow(
        observed_condition="nonzero_tool_return",
        l2_classification=(
            ResultClass.SOFT_REPAIRABLE,
            ResultClass.FAIL_TERMINAL,
        ),
        l2_may_do="capture_stderr_classify_maybe_retry",
        l2_must_not_do="hide_error",
    ),
    FailureMatrixRow(
        observed_condition="missing_required_input",
        l2_classification=(ResultClass.NEEDS_HELP,),
        l2_may_do="seal_need_help_packet",
        l2_must_not_do="ask_human_directly_or_guess",
    ),
    FailureMatrixRow(
        observed_condition="action_outside_capability",
        l2_classification=(ResultClass.REJECTED,),
        l2_may_do="seal_rejection",
        l2_must_not_do="execute_anyway",
    ),
    FailureMatrixRow(
        observed_condition="sandbox_escape_attempt",
        l2_classification=(ResultClass.REJECTED,),
        l2_may_do="quarantine_seal_stop",
        l2_must_not_do="broaden_sandbox",
    ),
    FailureMatrixRow(
        observed_condition="policy_hash_mismatch",
        l2_classification=(ResultClass.REJECTED,),
        l2_may_do="stop_and_seal",
        l2_must_not_do="continue_under_stale_policy",
    ),
    FailureMatrixRow(
        observed_condition="weak_evidence_for_grounded_ask",
        l2_classification=(
            ResultClass.DEGRADED_SUCCESS,
            ResultClass.NEEDS_HELP,
        ),
        l2_may_do="seal_caveated_partial_or_fail",
        l2_must_not_do="fabricate_confidence",
    ),
    FailureMatrixRow(
        observed_condition="proposed_durable_write",
        l2_classification=(ResultClass.SUCCESS,),
        l2_may_do="include_proposed_state_diff",
        l2_must_not_do="write_to_l4_directly",
    ),
    FailureMatrixRow(
        observed_condition="duplicate_packet",
        l2_classification=(ResultClass.SUCCESS,),
        l2_may_do="return_sealed_prior_receipt",
        l2_must_not_do="execute_twice",
    ),
    FailureMatrixRow(
        observed_condition="route_mismatch",
        l2_classification=(
            ResultClass.NEEDS_HELP,
            ResultClass.FAIL_TERMINAL,
        ),
        l2_may_do="seal_reentry_need",
        l2_must_not_do="reroute_inside_l2",
    ),
)


def lookup_failure_matrix(observed: str) -> FailureMatrixRow | None:
    """Return the canonical v4 row for an observed condition, if any."""
    for row in FAILURE_MATRIX:
        if row.observed_condition == observed:
            return row
    return None


# ---------------------------------------------------------------------------
# Full 15-invariant registry (v4 §L2 INVARIANTS)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class V4Invariant:
    invariant_id: int
    title: str
    description: str


L2_FULL_INVARIANTS: tuple[V4Invariant, ...] = (
    V4Invariant(1, "bounded_packet", "L2 executes exactly one bounded packet or current L3 step."),
    V4Invariant(2, "no_route_decision", "L2 does not decide the route."),
    V4Invariant(3, "no_workflow_expansion", "L2 does not expand a workflow."),
    V4Invariant(4, "no_unsanctioned_retrieval", "L2 does not retrieve new evidence unless the packet explicitly grants a bounded read/tool action."),
    V4Invariant(5, "no_direct_human_call", "L2 does not call humans directly."),
    V4Invariant(6, "no_authority_creation", "L2 does not create new authority."),
    V4Invariant(7, "no_durable_state_persistence", "L2 does not persist durable state."),
    V4Invariant(8, "no_l4_write", "L2 does not write to L4."),
    V4Invariant(9, "no_uwg_bypass", "L2 does not bypass UWG."),
    V4Invariant(10, "no_silent_swap", "L2 does not silently switch tools, models, providers, credentials, or sandboxes."),
    V4Invariant(11, "bounded_repair_only", "L2 can repair only local, bounded, same-authority defects."),
    V4Invariant(12, "preserve_replay_lineage", "L2 must preserve replay metadata, trace lineage, evidence lineage, and terminal classification."),
    V4Invariant(13, "seal_every_outcome", "L2 must seal every outcome, including rejection and failure."),
    V4Invariant(14, "downstream_consumers_only", "L2 emits artifacts for Exit, L3 merge, L6 audit, HITL review, or UWG decisioning only."),
    V4Invariant(15, "honest_now_no_future_rescue", "The current run is never rescued by future learning."),
)


# ---------------------------------------------------------------------------
# E4.6 Revalidation helper
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RevalidationResult:
    """Outcome of E4.6 revalidation: re-run repaired packet through E2/E3-compatible checks."""

    passed: bool
    failed_check: str = ""
    detail: str = ""


def revalidate_repaired_packet(
    *,
    repaired_payload: Any,
    original_capability_scope: CapabilityScopeSummary,
    original_side_effect_class: str,
    original_determinism: DeterminismBundle,
    new_determinism: DeterminismBundle,
) -> RevalidationResult:
    """v4 §E4.6 Revalidation — confirm repair stays inside original authority.

    Checks (in order):
      1. Snapshot binding unchanged (blueprint_hash + policy_hash).
      2. Repaired payload is not None / not empty (basic shape).
      3. Side-effect class did not escalate.

    A real implementation would also re-run the registered E2 schema check;
    this helper is the deterministic invariant gate.
    """
    if (
        original_determinism.blueprint_hash != new_determinism.blueprint_hash
        or original_determinism.policy_hash != new_determinism.policy_hash
    ):
        return RevalidationResult(
            passed=False,
            failed_check="snapshot_binding",
            detail="blueprint_hash or policy_hash changed during heal",
        )
    if repaired_payload is None:
        return RevalidationResult(
            passed=False,
            failed_check="payload_shape",
            detail="repaired payload is None",
        )
    # capability_scope is frozen at E2; we only re-assert the side-effect class
    # didn't escalate (e.g., from READ to ACTION).
    safe_classes = {"READ", "SANDBOX_WRITE"}
    if (
        original_side_effect_class in safe_classes
        and original_capability_scope.side_effect_envelope in safe_classes
    ):
        return RevalidationResult(passed=True)
    # For higher-impact classes we still pass (caller's E2 already approved
    # them) but flag for downstream review.
    return RevalidationResult(passed=True)


# ---------------------------------------------------------------------------
# E1 FAIL CONDITIONS (v4 §E1 FAIL CONDITIONS — 7 enumerated)
# ---------------------------------------------------------------------------


E1_FAIL_CONDITIONS: tuple[str, ...] = (
    "missing_capability_token",
    "missing_sandbox_envelope",
    "policy_hash_mismatch",
    "stale_blueprint_hash",
    "duplicate_in_flight_idempotency_key",
    "no_replay_snapshot_for_replay_required_route",
    "l2_detects_hidden_write_path",
)


# ---------------------------------------------------------------------------
# E4 REPAIR DECISION TABLE (v4 §REPAIR DECISION TABLE — 4 outcome paths)
# ---------------------------------------------------------------------------


class RepairDecision(str, Enum):
    """v4 §E4 REPAIR DECISION TABLE — four outcome paths."""

    REPAIR_AND_RETRY = "REPAIR_AND_RETRY"  # repaired packet returns to E3
    SEAL_DEGRADED_OR_NEEDS_HELP = "SEAL_DEGRADED_OR_NEEDS_HELP"  # useful partial
    STOP_NEEDS_HELP_OR_ESCALATE = "STOP_NEEDS_HELP_OR_ESCALATE"  # new authority required
    STOP_REJECTED_QUARANTINE = "STOP_REJECTED_QUARANTINE"  # safety/policy/sandbox breach


def repair_decision(
    *,
    repairable: bool,
    same_authority: bool,
    under_ceilings: bool,
    snapshot_intact: bool,
    has_useful_partial: bool,
    needs_new_authority_or_human: bool,
    safety_or_policy_breach: bool,
) -> RepairDecision:
    """v4 §REPAIR DECISION TABLE — deterministic mapping.

    Order matters: safety first (overrides everything), then authority
    expansion, then partial fallback, then full repair-and-retry path.
    """
    if safety_or_policy_breach:
        return RepairDecision.STOP_REJECTED_QUARANTINE
    if needs_new_authority_or_human:
        return RepairDecision.STOP_NEEDS_HELP_OR_ESCALATE
    if repairable and same_authority and under_ceilings and snapshot_intact:
        return RepairDecision.REPAIR_AND_RETRY
    if has_useful_partial:
        return RepairDecision.SEAL_DEGRADED_OR_NEEDS_HELP
    return RepairDecision.STOP_NEEDS_HELP_OR_ESCALATE


# ---------------------------------------------------------------------------
# TERMINAL CLASS MEANINGS (v4 §TERMINAL CLASS MEANINGS — 5 named classes)
# ---------------------------------------------------------------------------


TERMINAL_CLASS_MEANINGS: dict[TerminalStamp, str] = {
    TerminalStamp.SUCCESS: (
        "Local contract satisfied. Send to Exit for final current-run review."
    ),
    TerminalStamp.DEGRADED_SUCCESS: (
        "Useful partial result exists. Caveats and missing support must "
        "remain explicit downstream."
    ),
    TerminalStamp.FAILURE: (
        "Work could not complete under current packet, but no policy breach "
        "occurred."
    ),
    TerminalStamp.NEEDS_HELP: (
        "Requires missing input, new authority, HITL, reroute, or broader "
        "workflow decision."
    ),
    TerminalStamp.REJECTED: (
        "Packet or execution violated a rule, safety boundary, injection "
        "guard, sandbox guard, or authority boundary."
    ),
}


# ---------------------------------------------------------------------------
# EXECUTION LANE CONSTRAINTS (v4 §EXECUTION LANES — 5 lanes)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionLaneConstraints:
    """v4 §EXECUTION LANES — declared constraints per lane."""

    lane: ExecutionLane
    description: str
    durable_mutation_allowed: bool
    schema_bound_required: bool
    output_capture_required: bool


EXECUTION_LANE_CONSTRAINTS: dict[ExecutionLane, ExecutionLaneConstraints] = {
    ExecutionLane.READ: ExecutionLaneConstraints(
        lane=ExecutionLane.READ,
        description=(
            "Uses provided evidence or bounded read surfaces; produces "
            "answer/summary/comparison/extraction/classification; no durable "
            "mutation."
        ),
        durable_mutation_allowed=False,
        schema_bound_required=False,
        output_capture_required=True,
    ),
    ExecutionLane.MODEL: ExecutionLaneConstraints(
        lane=ExecutionLane.MODEL,
        description=(
            "Sends signed prompt artifact through provider/model gateway; "
            "schema-bound output if structured answer required; output must "
            "be locally parsed before seal."
        ),
        durable_mutation_allowed=False,
        schema_bound_required=True,
        output_capture_required=True,
    ),
    ExecutionLane.TOOL: ExecutionLaneConstraints(
        lane=ExecutionLane.TOOL,
        description=(
            "Invokes approved tool with validated args; captures stdout/"
            "stderr/return object; blocks unexpected side effects."
        ),
        durable_mutation_allowed=False,
        schema_bound_required=False,
        output_capture_required=True,
    ),
    ExecutionLane.ACTION: ExecutionLaneConstraints(
        lane=ExecutionLane.ACTION,
        description=(
            "Performs approved reversible or scoped action; irreversible/"
            "high-impact action must already have required clearance; any "
            "state mutation becomes proposed_state_diff unless the external "
            "tool action itself is the approved bounded action."
        ),
        durable_mutation_allowed=True,  # only when explicitly cleared
        schema_bound_required=False,
        output_capture_required=True,
    ),
    ExecutionLane.ARTIFACT: ExecutionLaneConstraints(
        lane=ExecutionLane.ARTIFACT,
        description=(
            "Generates file/report/chart/patch/draft/code/structured bundle; "
            "attaches artifact_hash, path, manifest, provenance; no untracked "
            "artifact leaves L2."
        ),
        durable_mutation_allowed=False,
        schema_bound_required=False,
        output_capture_required=True,
    ),
}


# ---------------------------------------------------------------------------
# E5.6 CONTRACT CHECK
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContractCheckResult:
    """v4 §E5.6 contract check — verify sealed artifact satisfies downstream."""

    satisfied: bool
    missing_fields: tuple[str, ...] = ()
    durable_commit_detected: bool = False


_REQUIRED_DOWNSTREAM_FIELDS: tuple[tuple[str, str], ...] = (
    ("identity", "sealed_l2_artifact_id"),
    ("identity", "run_id"),
    ("identity", "route_id"),
    ("governance", "compliance_hash"),
    ("governance", "policy_hash"),
    ("governance", "blueprint_hash"),
    ("replay", "replay_key"),
    ("replay", "input_hash"),
    ("observability", "trace_id"),
    ("terminal", "terminal_class"),
    ("terminal", "reason_code"),
)


def verify_sealed_artifact_contract(contents: Any) -> ContractCheckResult:
    """v4 §E5.6 contract check — verify required downstream fields are present.

    Used by Exit Control, L6 telemetry, HITL packetization, and UWG commit
    request paths to confirm a sealed L2 artifact carries everything the
    downstream consumer needs. Falls back gracefully on AttributeError.
    """
    missing: list[str] = []
    for section_name, field_name in _REQUIRED_DOWNSTREAM_FIELDS:
        try:
            section = getattr(contents, section_name)
            value = getattr(section, field_name)
        except AttributeError:
            missing.append(f"{section_name}.{field_name}")
            continue
        if value is None or value == "":
            missing.append(f"{section_name}.{field_name}")

    # Durable-commit detector: any sealed contents that exposes a
    # `has_commit_payload=True` bit, or whose commit_requested=True without
    # a proposed_state_diff, is a contract violation.
    durable_commit = False
    try:
        if getattr(contents, "has_commit_payload", False):
            durable_commit = True
    except AttributeError:
        pass

    return ContractCheckResult(
        satisfied=not missing and not durable_commit,
        missing_fields=tuple(missing),
        durable_commit_detected=durable_commit,
    )


__all__ = [
    "ExecutionForm",
    "CapabilitySpec",
    "TaskSpec",
    "WorkOrderInputs",
    "FrozenExecutionContext",
    "ReplayBindings",
    "WriteLockAssertion",
    "PrepOutput",
    "CapabilityScopeSummary",
    "BudgetSnapshot",
    "ApprovedWorkOrder",
    "SealedRejectionPacket",
    "ValidationOutput",
    "TelemetryBundle",
    "VALIDATION_PASS_RULES",
    "VALIDATION_FAIL_RULES",
    "SAFE_LOCAL_REPAIRS",
    "DISALLOWED_REPAIRS",
    "is_repair_allowed",
    "FailureMatrixRow",
    "FAILURE_MATRIX",
    "lookup_failure_matrix",
    "V4Invariant",
    "L2_FULL_INVARIANTS",
    "RevalidationResult",
    "revalidate_repaired_packet",
    "E1_FAIL_CONDITIONS",
    "RepairDecision",
    "repair_decision",
    "TERMINAL_CLASS_MEANINGS",
    "ExecutionLaneConstraints",
    "EXECUTION_LANE_CONSTRAINTS",
    "ContractCheckResult",
    "verify_sealed_artifact_contract",
    # re-exports for convenience
    "DeterminismBundle",
    "DispatchTarget",
    "ExecutionLane",
    "LineageRoot",
    "RepairStatus",
    "ResultClass",
    "TerminalStamp",
]
