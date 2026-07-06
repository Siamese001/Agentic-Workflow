"""apps_rg-owned L2 envelope receipt and contract types."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

L2_ENVELOPE_AUTHORITY_SCOPE = "apps_rg_l2_envelope_adapter_receipts"
CANONICAL_L2_ARTIFACT_AUTHORITY_SCOPE = "agentic_core_runtime_sealed_l2_artifact"


class ResultClass(str, Enum):
    SUCCESS = "SUCCESS"
    SOFT_REPAIRABLE = "SOFT_REPAIRABLE"
    FAIL_TERMINAL = "FAIL_TERMINAL"
    NEEDS_HELP = "NEEDS_HELP"
    REJECTED = "REJECTED"
    DEGRADED_SUCCESS = "DEGRADED_SUCCESS"


class RepairStatus(str, Enum):
    REPAIRED = "REPAIRED"
    NOT_REPAIRED = "NOT_REPAIRED"
    QUARANTINED = "QUARANTINED"
    NEEDS_HELP = "NEEDS_HELP"
    FAIL_TERMINAL = "FAIL_TERMINAL"


class ExecutionLane(str, Enum):
    READ = "READ"
    MODEL = "MODEL"
    TOOL = "TOOL"
    ACTION = "ACTION"
    ARTIFACT = "ARTIFACT"


class ExecutionForm(str, Enum):
    SINGLE_STEP = "SINGLE_STEP"
    L3_STEP = "L3_STEP"
    RESUMED_STEP = "RESUMED_STEP"


class HealOutcomeStamp(str, Enum):
    PASS = "PASS"
    NEEDS_HELP = "NEEDS_HELP"
    ESCALATE_ARTIFACT = "ESCALATE_ARTIFACT"
    FAIL_TERMINAL = "FAIL_TERMINAL"


@dataclass(frozen=True)
class LineageRoot:
    parent_route_id: str
    parent_plan_id: str | None
    parent_step_id: str | None
    ancestry_chain: tuple[str, ...] = ()
    same_run_packet_family: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "parent_route_id": self.parent_route_id,
            "parent_plan_id": self.parent_plan_id,
            "parent_step_id": self.parent_step_id,
            "ancestry_chain": list(self.ancestry_chain),
            "same_run_packet_family": self.same_run_packet_family,
        }


@dataclass(frozen=True)
class DeterminismBundle:
    blueprint_hash: str
    policy_hash: str
    prompt_hash: str
    input_hash: str
    replay_key: str
    attempt_seed: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "blueprint_hash": self.blueprint_hash,
            "policy_hash": self.policy_hash,
            "prompt_hash": self.prompt_hash,
            "input_hash": self.input_hash,
            "replay_key": self.replay_key,
            "attempt_seed": self.attempt_seed,
        }


@dataclass(frozen=True)
class AppsRgL2ExecutionPacket:
    request_id: str
    run_id: str
    trace_id: str
    route_id: str
    workflow_id: str = ""
    node_id: str = ""
    step_id: str = ""
    capability_token: str = ""
    sandbox_envelope: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    prompt_hash: str = ""
    replay_key: str = ""
    attempt_seed: str = ""
    registry_digest_set: tuple[str, ...] = ()
    compiled_prompt_artifact_ref: str = ""
    final_evidence_contract_ref: str = ""
    side_effect_class: str = "READ"
    budget: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "route_id": self.route_id,
            "workflow_id": self.workflow_id,
            "node_id": self.node_id,
            "step_id": self.step_id,
            "capability_token": self.capability_token,
            "sandbox_envelope": self.sandbox_envelope,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "prompt_hash": self.prompt_hash,
            "replay_key": self.replay_key,
            "attempt_seed": self.attempt_seed,
            "registry_digest_set": list(self.registry_digest_set),
            "compiled_prompt_artifact_ref": self.compiled_prompt_artifact_ref,
            "final_evidence_contract_ref": self.final_evidence_contract_ref,
            "side_effect_class": self.side_effect_class,
            "budget": dict(self.budget),
        }


@dataclass(frozen=True)
class AttemptReceipt:
    attempt_receipt_id: str
    validation_packet_id: str
    attempt_count: int
    determinism: DeterminismBundle
    lineage: LineageRoot
    trace_id: str
    span_id: str | None
    latency_ms: float
    tokens_used: int
    return_code: int | None
    result_class: ResultClass
    output_digest: str = ""
    error_summary: str | None = None
    sealed_at: float = field(default_factory=time.monotonic)
    execution_lane: ExecutionLane | None = None
    decisive_reason_code: str = ""
    local_check_results: Any = ()
    generated_artifacts: tuple[str, ...] = ()
    proposed_state_diff: dict[str, Any] = field(default_factory=dict)
    quarantined_payload: str | None = None
    authority_scope: str = L2_ENVELOPE_AUTHORITY_SCOPE
    canonical_l2_artifact_authority: bool = False

    @staticmethod
    def new_id() -> str:
        return f"attempt-{uuid.uuid4().hex}"


@dataclass(frozen=True)
class HealReceipt:
    repair_attempt_id: str
    parent_attempt_receipt_id: str
    failed_span_id: str | None
    reason_code: str
    repair_count: int
    determinism: DeterminismBundle
    lineage: LineageRoot
    delta_summary: str = ""
    outcome: HealOutcomeStamp = HealOutcomeStamp.NEEDS_HELP
    sealed_at: float = field(default_factory=time.monotonic)
    repair_status: RepairStatus | None = None
    repair_tactic: str = ""
    before_hash: str = ""
    after_hash: str = ""
    repair_patch: dict[str, Any] = field(default_factory=dict)
    oscillation_status: str = ""
    snapshot_guard_status: str = "PASS"
    next_action: str = ""
    authority_scope: str = L2_ENVELOPE_AUTHORITY_SCOPE
    canonical_l2_artifact_authority: bool = False

    @staticmethod
    def new_id() -> str:
        return f"heal-{uuid.uuid4().hex}"

    def routes_back_to_e3(self) -> bool:
        return self.outcome is HealOutcomeStamp.PASS


@dataclass(frozen=True)
class H0RepairContext:
    repair_tactic: str
    failed_reason: str
    failed_error: str
    instruction: str


@dataclass(frozen=True)
class RepairInvocationPatch:
    stage: str
    repair_count: int
    repair_tactic: str
    parent_attempt_receipt_id: str
    h0_context: H0RepairContext


@dataclass(frozen=True)
class CapabilitySpec:
    name: str
    version: str = ""
    schema_id: str = ""


@dataclass(frozen=True)
class TaskSpec:
    intent: str
    expected_output_contract: str = ""
    grounded: bool = False


@dataclass(frozen=True)
class WorkOrderInputs:
    execution_form: ExecutionForm
    task_spec: TaskSpec
    tool_spec: CapabilitySpec | None = None
    model_spec: CapabilitySpec | None = None
    action_spec: CapabilitySpec | None = None
    cost_tier: str = "standard"
    retry_ceiling: int = 3
    max_repair_count: int = 3
    slo_slice_ms: int = 60_000


@dataclass(frozen=True)
class FrozenExecutionContext:
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
    determinism: DeterminismBundle
    snapshot_manifest: str
    clock_policy: str = "run_clock_offsets"


@dataclass(frozen=True)
class WriteLockAssertion:
    no_direct_l4_path: bool = True
    proposed_diff_only: bool = True
    persistence_disabled: bool = True
    asserted_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class PrepOutput:
    prep_receipt_id: str
    frozen_execution_context: FrozenExecutionContext
    run_id: str
    idempotency_key: str
    lineage_root: LineageRoot
    replay_bindings: ReplayBindings
    write_lock_assertion: WriteLockAssertion
    ready_for_validation: bool
    refusal_reason: str = ""
    authority_scope: str = L2_ENVELOPE_AUTHORITY_SCOPE
    canonical_l2_artifact_authority: bool = False


@dataclass(frozen=True)
class CapabilityScopeSummary:
    capability_token_id: str
    granted_tools: tuple[str, ...] = ()
    granted_actions: tuple[str, ...] = ()
    granted_models: tuple[str, ...] = ()
    side_effect_envelope: str = "READ"
    tenant_scope: str = ""


@dataclass(frozen=True)
class BudgetSnapshot:
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
    validation_packet_id: str
    decisive_rule_id: str
    capability_scope: CapabilityScopeSummary
    budget_snapshot: BudgetSnapshot
    side_effect_class: str
    approved_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class SealedRejectionPacket:
    rejection_packet_id: str
    failed_validation_rule: str
    side_effect_class: str
    missing_or_invalid_authority_field: str
    suggested_reentry_target: str
    decisive_rule_id: str
    sealed_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class ValidationOutput:
    validation_packet_id: str
    validation_status: str
    approved_work_order: ApprovedWorkOrder | None = None
    sealed_rejection_packet: SealedRejectionPacket | None = None
    gate_refs: tuple[str, ...] = ()
    authority_scope: str = L2_ENVELOPE_AUTHORITY_SCOPE
    canonical_l2_artifact_authority: bool = False


@dataclass(frozen=True)
class TelemetryBundle:
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
    return tactic in SAFE_LOCAL_REPAIRS


__all__ = [
    "ApprovedWorkOrder",
    "AppsRgL2ExecutionPacket",
    "AttemptReceipt",
    "BudgetSnapshot",
    "CANONICAL_L2_ARTIFACT_AUTHORITY_SCOPE",
    "CapabilityScopeSummary",
    "CapabilitySpec",
    "DISALLOWED_REPAIRS",
    "DeterminismBundle",
    "ExecutionForm",
    "ExecutionLane",
    "FrozenExecutionContext",
    "H0RepairContext",
    "HealOutcomeStamp",
    "HealReceipt",
    "LineageRoot",
    "L2_ENVELOPE_AUTHORITY_SCOPE",
    "PrepOutput",
    "RepairInvocationPatch",
    "RepairStatus",
    "ReplayBindings",
    "ResultClass",
    "SAFE_LOCAL_REPAIRS",
    "SealedRejectionPacket",
    "TaskSpec",
    "TelemetryBundle",
    "ValidationOutput",
    "WorkOrderInputs",
    "WriteLockAssertion",
    "is_repair_allowed",
]
