"""SameAuthorityRegenReceipt — HealReceipt-compatible E4 output (ADR-085)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.regen.prompt_lock import (
    CONTRACT_VERSION,
    REPAIR_TACTIC_INCREMENTAL_DELTA,
)
from agentic_core.L2_execution.regen.regen_types import (
    AnchorClassification,
    RegenRefusalCode,
    TriggerSource,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    HealOutcomeStamp,
    HealReceipt,
    LineageRoot,
)


@dataclass(frozen=True)
class SameAuthorityRegenReceipt:
    """E4.7-compatible same-authority incremental regen receipt."""

    repair_attempt_id: str
    parent_attempt_receipt_id: str
    request_id: str
    run_id: str
    trace_root: str
    parent_contract_ref: str
    contract_digest: str
    policy_hash: str
    blueprint_hash: str
    registry_digest_set: tuple[str, ...]
    replay_key: str
    frozen_compile_ref: str
    semantic_regen_attempt_index: int
    transport_retry_count: int
    max_semantic_regen_attempts: int
    semantic_regen_budget_exhausted: bool
    trigger_source: TriggerSource
    anchor_output_hash: str
    delta_message_hash: str
    prior_output_hash: str
    regenerated_output_hash: str
    anchor_classification: AnchorClassification
    same_authority_assertions: dict[str, bool]
    no_prompt_recompile_assertion: bool
    no_provider_substitution_assertion: bool
    no_app_policy_decision_assertion: bool
    heal_outcome: HealOutcomeStamp
    next_action: str
    determinism: DeterminismBundle
    lineage: LineageRoot
    provider_request_ref: str = ""
    provider_response_ref: str = ""
    refusal_code: RegenRefusalCode | None = None
    l5_governance_context_digest: str = ""
    runtime_gate_refs: tuple[str, ...] = ()
    receipt_refs: tuple[str, ...] = ()
    data_boundary_labels: tuple[str, ...] = ()
    audit_manifest_ref: str = ""
    authority_scope: str = "same_authority_no_commit"
    contract_type: str = "SameAuthorityRegenReceipt"
    contract_version: str = CONTRACT_VERSION
    producer_stage: str = "L2_E4_HEAL"
    consumer_stage: str = "L2_E3_EXEC"
    repair_tactic: str = REPAIR_TACTIC_INCREMENTAL_DELTA
    sealed_at: float = field(default_factory=time.monotonic)

    @staticmethod
    def new_id() -> str:
        return f"heal-regen-{uuid.uuid4().hex}"

    def to_heal_receipt(self) -> HealReceipt:
        """Bridge to v4 ``HealReceipt`` for sequencer integration."""
        return HealReceipt(
            repair_attempt_id=self.repair_attempt_id,
            parent_attempt_receipt_id=self.parent_attempt_receipt_id,
            failed_span_id=None,
            reason_code=self.refusal_code.value if self.refusal_code else "incremental_delta_turn_v1",
            repair_count=self.semantic_regen_attempt_index,
            determinism=self.determinism,
            lineage=self.lineage,
            delta_summary=self.delta_message_hash[:32],
            outcome=self.heal_outcome,
            sealed_at=self.sealed_at,
            repair_tactic=self.repair_tactic,
            before_hash=self.prior_output_hash,
            after_hash=self.regenerated_output_hash,
            oscillation_status="CLEAN",
            snapshot_guard_status="PASS",
            next_action=self.next_action,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_type": self.contract_type,
            "contract_version": self.contract_version,
            "producer_stage": self.producer_stage,
            "consumer_stage": self.consumer_stage,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "parent_contract_ref": self.parent_contract_ref,
            "contract_digest": self.contract_digest,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "registry_digest_set": list(self.registry_digest_set),
            "replay_key": self.replay_key,
            "repair_attempt_id": self.repair_attempt_id,
            "parent_attempt_receipt_id": self.parent_attempt_receipt_id,
            "repair_tactic": self.repair_tactic,
            "semantic_regen_attempt_index": self.semantic_regen_attempt_index,
            "transport_retry_count": self.transport_retry_count,
            "max_semantic_regen_attempts": self.max_semantic_regen_attempts,
            "semantic_regen_budget_exhausted": self.semantic_regen_budget_exhausted,
            "trigger_source": self.trigger_source.value,
            "frozen_compile_ref": self.frozen_compile_ref,
            "anchor_output_hash": self.anchor_output_hash,
            "delta_message_hash": self.delta_message_hash,
            "prior_output_hash": self.prior_output_hash,
            "regenerated_output_hash": self.regenerated_output_hash,
            "provider_request_ref": self.provider_request_ref,
            "provider_response_ref": self.provider_response_ref,
            "anchor_classification": self.anchor_classification.value,
            "same_authority_assertions": dict(self.same_authority_assertions),
            "no_prompt_recompile_assertion": self.no_prompt_recompile_assertion,
            "no_provider_substitution_assertion": self.no_provider_substitution_assertion,
            "no_app_policy_decision_assertion": self.no_app_policy_decision_assertion,
            "heal_outcome": self.heal_outcome.value,
            "next_action": self.next_action,
            "refusal_code": self.refusal_code.value if self.refusal_code else None,
            "l5_governance_context_digest": self.l5_governance_context_digest,
            "runtime_gate_refs": list(self.runtime_gate_refs),
            "receipt_refs": list(self.receipt_refs),
            "authority_scope": self.authority_scope,
        }
