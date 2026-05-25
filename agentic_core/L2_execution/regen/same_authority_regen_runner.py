"""SameAuthorityRegenRunner — L2 E4 Heal subtype (ADR-085)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages
from agentic_core.L2_execution.regen.delta_shape_guard import validate_delta_shape
from agentic_core.L2_execution.regen.incremental_repair_contract import (
    IncrementalRepairContract,
)
from agentic_core.L2_execution.regen.prefix_digest import (
    compute_delta_message_hash,
    compute_system_prefix_hash,
    sha256_hex,
)
from agentic_core.L2_execution.regen.prompt_lock import format_regen_delta_user_turn
from agentic_core.L2_execution.regen.regen_refusal import RegenRefusal
from agentic_core.L2_execution.regen.regen_types import RegenRefusalCode
from agentic_core.L2_execution.regen.same_authority_regen_receipt import (
    SameAuthorityRegenReceipt,
)
from agentic_core.L2_execution.regen.same_authority_thread import append_same_authority_turn
from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    HealOutcomeStamp,
    LineageRoot,
)

ProviderGenerateFn = Callable[[list[dict[str, str]]], dict[str, Any]]


class _LineageFactory(Protocol):
    def __call__(
        self, contract: IncrementalRepairContract,
    ) -> LineageRoot: ...


@dataclass(frozen=True)
class RegenRunResult:
    """Outcome of one heal evaluation."""

    accepted: bool
    receipt: SameAuthorityRegenReceipt | None = None
    refusal: RegenRefusal | None = None
    regenerated_text: str = ""
    chat_messages: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, object]:
        if self.refusal is not None:
            return {"accepted": False, "refusal": self.refusal.to_dict()}
        assert self.receipt is not None
        return {
            "accepted": True,
            "receipt": self.receipt.as_dict(),
            "regenerated_text": self.regenerated_text,
        }


def _default_lineage(contract: IncrementalRepairContract) -> LineageRoot:
    return LineageRoot(
        parent_route_id=contract.run_id,
        parent_plan_id=None,
        parent_step_id=contract.parent_attempt_receipt_id,
        ancestry_chain=(contract.parent_contract_ref,),
        same_run_packet_family=contract.run_id,
    )


def _determinism_from_contract(contract: IncrementalRepairContract) -> DeterminismBundle:
    return DeterminismBundle(
        blueprint_hash=contract.blueprint_hash,
        policy_hash=contract.policy_hash,
        prompt_hash=contract.prompt_hash or contract.frozen_compile_ref,
        input_hash=contract.anchor_output_hash,
        replay_key=contract.replay_key,
        attempt_seed=contract.replay_key[:16],
    )


class SameAuthorityRegenRunner:
    """E4 heal runner: validate → append delta turn → provider ``messages[]``."""

    repair_tactic: str = "incremental_delta_turn_v1"

    def evaluate_refusal(self, contract: IncrementalRepairContract) -> RegenRefusal | None:
        """Pre-flight refusal checks (no provider dispatch)."""
        checks = (
            contract.validate_authority_refs,
            contract.validate_policy_flags,
            contract.validate_anchor_and_defect,
            contract.validate_budget_and_recursion,
        )
        for check in checks:
            code = check()
            if code is not None:
                return self._refusal_from_code(contract, code)

        shape_code = validate_delta_shape(
            contract.delta_lines,
            max_delta_lines=contract.max_delta_lines,
            max_delta_tokens=contract.max_delta_tokens,
            anchor_output_text=contract.anchor_output_text,
        )
        if shape_code is not None:
            return self._refusal_from_code(contract, shape_code)

        if contract.prompt_messages is not None and contract.expected_system_prefix_hash:
            current = compute_system_prefix_hash(contract.prompt_messages.system_text())
            if current != contract.expected_system_prefix_hash:
                return self._refusal_from_code(contract, RegenRefusalCode.PROMPT_RECOMPILE)

        return None

    def _refusal_from_code(
        self,
        contract: IncrementalRepairContract,
        code: RegenRefusalCode,
    ) -> RegenRefusal:
        budget_exhausted = code is RegenRefusalCode.SEMANTIC_REGEN_BUDGET_EXHAUSTED
        next_action = "SEND_TO_E5" if budget_exhausted else "SEND_TO_E5"
        return RegenRefusal(
            code=code,
            message=f"same_authority_regen refused: {code.value}",
            semantic_regen_attempt_index=contract.semantic_regen_attempt_index,
            max_semantic_regen_attempts=contract.max_semantic_regen_attempts,
            semantic_regen_budget_exhausted=budget_exhausted,
        )

    def build_refusal_receipt(
        self,
        contract: IncrementalRepairContract,
        refusal: RegenRefusal,
        *,
        lineage_factory: _LineageFactory | None = None,
    ) -> SameAuthorityRegenReceipt:
        """Terminal heal receipt for refusal (E5 / NEEDS_HELP path)."""
        lineage = (lineage_factory or _default_lineage)(contract)
        determinism = _determinism_from_contract(contract)
        return SameAuthorityRegenReceipt(
            repair_attempt_id=SameAuthorityRegenReceipt.new_id(),
            parent_attempt_receipt_id=contract.parent_attempt_receipt_id,
            request_id=contract.request_id,
            run_id=contract.run_id,
            trace_root=contract.trace_root,
            parent_contract_ref=contract.parent_contract_ref,
            contract_digest=contract.contract_digest(),
            policy_hash=contract.policy_hash,
            blueprint_hash=contract.blueprint_hash,
            registry_digest_set=contract.registry_digest_set,
            replay_key=contract.replay_key,
            frozen_compile_ref=contract.frozen_compile_ref,
            semantic_regen_attempt_index=refusal.semantic_regen_attempt_index,
            transport_retry_count=contract.transport_retry_count,
            max_semantic_regen_attempts=refusal.max_semantic_regen_attempts,
            semantic_regen_budget_exhausted=refusal.semantic_regen_budget_exhausted,
            trigger_source=contract.trigger_source,
            anchor_output_hash=contract.anchor_output_hash,
            delta_message_hash="",
            prior_output_hash=contract.anchor_output_hash,
            regenerated_output_hash="",
            anchor_classification=contract.anchor_classification,
            same_authority_assertions={"refused": True},
            no_prompt_recompile_assertion=False,
            no_provider_substitution_assertion=False,
            no_app_policy_decision_assertion=True,
            heal_outcome=HealOutcomeStamp.NEEDS_HELP,
            next_action="SEND_TO_E5",
            determinism=determinism,
            lineage=lineage,
            refusal_code=refusal.code,
            l5_governance_context_digest=contract.l5_governance_context_digest,
            runtime_gate_refs=contract.runtime_gate_refs,
            receipt_refs=contract.receipt_refs,
            data_boundary_labels=contract.data_boundary_labels,
            audit_manifest_ref=contract.audit_manifest_ref,
            consumer_stage="L2_E5_SEAL",
        )

    def run(
        self,
        contract: IncrementalRepairContract,
        *,
        provider_generate: ProviderGenerateFn,
        lineage_factory: _LineageFactory | None = None,
        provider_request_ref: str = "",
        provider_response_ref: str = "",
    ) -> RegenRunResult:
        """Execute regen when pre-flight passes; otherwise terminal refusal."""
        refusal = self.evaluate_refusal(contract)
        if refusal is not None:
            return RegenRunResult(
                accepted=False,
                refusal=refusal,
                receipt=self.build_refusal_receipt(
                    contract,
                    refusal,
                    lineage_factory=lineage_factory,
                ),
            )

        if contract.prompt_messages is None:
            refusal = self._refusal_from_code(
                contract,
                RegenRefusalCode.MISSING_FROZEN_COMPILE_REF,
            )
            return RegenRunResult(
                accepted=False,
                refusal=refusal,
                receipt=self.build_refusal_receipt(contract, refusal),
            )

        delta_text = format_regen_delta_user_turn(contract.delta_lines)
        thread = append_same_authority_turn(
            contract.prompt_messages,
            bundle=self.bundle_from_contract(contract),
            anchor_assistant_content=contract.anchor_output_text,
            delta_user_content=delta_text,
        )
        messages = thread.to_chat_messages()
        provider_result = provider_generate(messages)

        if provider_result.get("mocked_allow"):
            refusal = self._refusal_from_code(
                contract,
                RegenRefusalCode.MOCKED_PROVIDER_ALLOW,
            )
            return RegenRunResult(
                accepted=False,
                refusal=refusal,
                receipt=self.build_refusal_receipt(contract, refusal),
            )

        regenerated = str(provider_result.get("content") or "")
        regen_hash = sha256_hex(regenerated) if regenerated else ""
        assertions = {
            "frozen_compile_preserved": True,
            "delta_only_append": True,
            "provider_lane_unchanged": contract.parent_provider_lane == contract.provider_lane,
            "semantic_budget_ok": (
                contract.semantic_regen_attempt_index <= contract.max_semantic_regen_attempts
            ),
        }

        receipt = SameAuthorityRegenReceipt(
            repair_attempt_id=SameAuthorityRegenReceipt.new_id(),
            parent_attempt_receipt_id=contract.parent_attempt_receipt_id,
            request_id=contract.request_id,
            run_id=contract.run_id,
            trace_root=contract.trace_root,
            parent_contract_ref=contract.parent_contract_ref,
            contract_digest=contract.contract_digest(),
            policy_hash=contract.policy_hash,
            blueprint_hash=contract.blueprint_hash,
            registry_digest_set=contract.registry_digest_set,
            replay_key=contract.replay_key,
            frozen_compile_ref=contract.frozen_compile_ref,
            semantic_regen_attempt_index=contract.semantic_regen_attempt_index,
            transport_retry_count=contract.transport_retry_count,
            max_semantic_regen_attempts=contract.max_semantic_regen_attempts,
            semantic_regen_budget_exhausted=False,
            trigger_source=contract.trigger_source,
            anchor_output_hash=contract.anchor_output_hash,
            delta_message_hash=thread.delta_message_hash,
            prior_output_hash=contract.anchor_output_hash,
            regenerated_output_hash=regen_hash,
            anchor_classification=contract.anchor_classification,
            same_authority_assertions=assertions,
            no_prompt_recompile_assertion=True,
            no_provider_substitution_assertion=True,
            no_app_policy_decision_assertion=True,
            heal_outcome=HealOutcomeStamp.PASS,
            next_action="RETURN_TO_E3",
            determinism=_determinism_from_contract(contract),
            lineage=(lineage_factory or _default_lineage)(contract),
            provider_request_ref=provider_request_ref,
            provider_response_ref=provider_response_ref,
            l5_governance_context_digest=contract.l5_governance_context_digest,
            runtime_gate_refs=contract.runtime_gate_refs,
            receipt_refs=contract.receipt_refs,
            data_boundary_labels=contract.data_boundary_labels,
            audit_manifest_ref=contract.audit_manifest_ref,
        )
        return RegenRunResult(
            accepted=True,
            receipt=receipt,
            regenerated_text=regenerated,
            chat_messages=tuple(messages),
        )

    def bundle_from_contract(self, contract: IncrementalRepairContract):
        from agentic_core.L2_execution.regen.same_authority_bundle import SameAuthorityBundle

        sys_hash = contract.expected_system_prefix_hash
        if not sys_hash and contract.prompt_messages is not None:
            sys_hash = compute_system_prefix_hash(contract.prompt_messages.system_text())
        return SameAuthorityBundle(
            frozen_compile_ref=contract.frozen_compile_ref,
            system_prefix_hash=sys_hash,
            policy_hash=contract.policy_hash,
            blueprint_hash=contract.blueprint_hash,
            registry_digest_set=contract.registry_digest_set,
            replay_key=contract.replay_key,
            provider_lane=contract.provider_lane,
            model_lane=contract.model_lane,
            capability_token=contract.capability_token,
            sandbox_envelope=contract.sandbox_envelope,
            prompt_hash=contract.prompt_hash,
        )
