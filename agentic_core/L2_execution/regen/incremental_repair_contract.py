"""IncrementalRepairContract — E4 heal input with spine envelope (ADR-085)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.L2_execution.regen.prefix_digest import canonical_json, sha256_hex
from agentic_core.L2_execution.regen.prompt_lock import (
    CONTRACT_VERSION,
    DEFAULT_MAX_DELTA_LINES,
    DEFAULT_MAX_DELTA_TOKENS,
    DEFAULT_MAX_SEMANTIC_REGEN_ATTEMPTS,
)
from agentic_core.L2_execution.regen.regen_types import (
    AnchorClassification,
    DefectClass,
    RegenRefusalCode,
    TriggerSource,
)

if TYPE_CHECKING:
    from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages


@dataclass(frozen=True)
class IncrementalRepairContract:
    """App-supplied heal input; core validates and enforces guards."""

    request_id: str
    run_id: str
    trace_root: str
    parent_contract_ref: str
    parent_attempt_receipt_id: str
    replay_key: str
    policy_hash: str
    blueprint_hash: str
    registry_digest_set: tuple[str, ...]
    frozen_compile_ref: str
    prompt_hash: str
    provider_lane: str
    model_lane: str
    parent_provider_lane: str
    parent_model_lane: str
    anchor_output_hash: str
    anchor_output_text: str
    anchor_classification: AnchorClassification
    defect_class: DefectClass
    trigger_source: TriggerSource
    delta_lines: tuple[str, ...]
    semantic_regen_attempt_index: int = 1
    transport_retry_count: int = 0
    max_semantic_regen_attempts: int = DEFAULT_MAX_SEMANTIC_REGEN_ATTEMPTS
    max_delta_lines: int = DEFAULT_MAX_DELTA_LINES
    max_delta_tokens: int = DEFAULT_MAX_DELTA_TOKENS
    capability_token: str = ""
    sandbox_envelope: str = ""
    l5_governance_context_digest: str = ""
    runtime_gate_refs: tuple[str, ...] = ()
    receipt_refs: tuple[str, ...] = ()
    data_boundary_labels: tuple[str, ...] = ()
    audit_manifest_ref: str = ""
    authority_scope: str = "same_authority_no_commit"
    contract_type: str = "IncrementalRepairContract"
    contract_version: str = CONTRACT_VERSION
    producer_stage: str = "L2_E4_HEAL"
    consumer_stage: str = "L2_E3_EXEC"
    authority_blocked: bool = False
    mocked_provider: bool = False
    prompt_recompile_detected: bool = False
    nested_heal_without_new_attempt: bool = False
    anchor_x2_red_soft_repairable: bool = True
    anchor_x2_snapshot_ref: str = ""
    expected_system_prefix_hash: str = ""
    prompt_messages: PromptMessages | None = None

    def contract_digest(self) -> str:
        stable = {
            "contract_type": self.contract_type,
            "contract_version": self.contract_version,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "parent_contract_ref": self.parent_contract_ref,
            "frozen_compile_ref": self.frozen_compile_ref,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "registry_digest_set": list(self.registry_digest_set),
            "replay_key": self.replay_key,
            "anchor_output_hash": self.anchor_output_hash,
            "semantic_regen_attempt_index": self.semantic_regen_attempt_index,
        }
        return sha256_hex(canonical_json(stable))

    def validate_authority_refs(self) -> RegenRefusalCode | None:
        if not self.frozen_compile_ref:
            return RegenRefusalCode.MISSING_FROZEN_COMPILE_REF
        if not self.anchor_output_hash:
            return RegenRefusalCode.MISSING_ANCHOR_OUTPUT
        if not self.replay_key or not self.policy_hash or not self.blueprint_hash:
            return RegenRefusalCode.MISSING_AUTHORITY_REFS
        if not self.registry_digest_set:
            return RegenRefusalCode.MISSING_AUTHORITY_REFS
        return None

    def validate_anchor_and_defect(self) -> RegenRefusalCode | None:
        if self.anchor_classification is AnchorClassification.REFUSE_UNSAFE:
            return RegenRefusalCode.ANCHOR_UNSAFE
        if self.defect_class is not DefectClass.SOFT_REPAIRABLE:
            if self.defect_class is DefectClass.UNKNOWN:
                return RegenRefusalCode.UNKNOWN_VALIDATION_STATUS
            return RegenRefusalCode.ANCHOR_X2_RED_NOT_SOFT_REPAIRABLE
        if not self.anchor_x2_red_soft_repairable:
            if self.anchor_classification not in (
                AnchorClassification.LAST_APPROVED,
                AnchorClassification.DEGRADED_ANCHOR_ALLOWED,
            ):
                return RegenRefusalCode.ANCHOR_X2_RED_NOT_SOFT_REPAIRABLE
        return None

    def validate_budget_and_recursion(self) -> RegenRefusalCode | None:
        if self.semantic_regen_attempt_index > self.max_semantic_regen_attempts:
            return RegenRefusalCode.SEMANTIC_REGEN_BUDGET_EXHAUSTED
        if self.nested_heal_without_new_attempt:
            return RegenRefusalCode.RECURSIVE_REGEN_FORBIDDEN
        return None

    def validate_policy_flags(self) -> RegenRefusalCode | None:
        if self.authority_blocked:
            return RegenRefusalCode.AUTHORITY_BLOCKED
        if self.mocked_provider:
            return RegenRefusalCode.MOCKED_PROVIDER_ALLOW
        if self.prompt_recompile_detected:
            return RegenRefusalCode.PROMPT_RECOMPILE
        if (
            self.parent_provider_lane != self.provider_lane
            or self.parent_model_lane != self.model_lane
        ):
            return RegenRefusalCode.PROVIDER_SUBSTITUTION
        return None

    def as_dict(self) -> dict[str, object]:
        return {
            "contract_type": self.contract_type,
            "contract_version": self.contract_version,
            "producer_stage": self.producer_stage,
            "consumer_stage": self.consumer_stage,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "parent_contract_ref": self.parent_contract_ref,
            "contract_digest": self.contract_digest(),
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "registry_digest_set": list(self.registry_digest_set),
            "replay_key": self.replay_key,
            "frozen_compile_ref": self.frozen_compile_ref,
            "anchor_classification": self.anchor_classification.value,
            "defect_class": self.defect_class.value,
            "trigger_source": self.trigger_source.value,
            "semantic_regen_attempt_index": self.semantic_regen_attempt_index,
            "transport_retry_count": self.transport_retry_count,
            "max_semantic_regen_attempts": self.max_semantic_regen_attempts,
        }
