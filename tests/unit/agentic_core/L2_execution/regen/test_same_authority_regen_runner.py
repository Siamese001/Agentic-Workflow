"""W2 runner, receipt, ceiling, anchor, and semantic/transport separation tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
)
from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages
from agentic_core.L2_execution.regen.incremental_repair_contract import (
    IncrementalRepairContract,
)
from agentic_core.L2_execution.regen.prefix_digest import compute_system_prefix_hash
from agentic_core.L2_execution.regen.regen_types import (
    AnchorClassification,
    DefectClass,
    RegenRefusalCode,
    TriggerSource,
)
from agentic_core.L2_execution.regen.same_authority_regen_runner import (
    SameAuthorityRegenRunner,
)
from agentic_core.L2_execution.types.l2_v3_receipts import HealOutcomeStamp


def _prompt_messages() -> PromptMessages:
    artifact = CompiledPromptArtifact(
        trace_id="t-w2",
        system_version_hash="h-w2",
        final_system_string="",
        final_user_string="",
        allowed_tools_schema=[],
        tokens=1,
        slots_used=["S0", "U0"],
        signature="",
    )
    slots = {
        "S0": AuthoritySlot(
            slot_type="S0",
            content="SYS",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L0",
        ),
        "U0": AuthoritySlot(
            slot_type="U0",
            content="USER",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }
    return PromptMessages.from_artifact(artifact, slots=slots)


def _base_contract(**overrides: object) -> IncrementalRepairContract:
    pm = _prompt_messages()
    sys_hash = compute_system_prefix_hash(pm.system_text())
    defaults: dict[str, object] = {
        "request_id": "req-1",
        "run_id": "run-1",
        "trace_root": "trace-1",
        "parent_contract_ref": "attempt-1",
        "parent_attempt_receipt_id": "attempt-1",
        "replay_key": "rk-1",
        "policy_hash": "pol-1",
        "blueprint_hash": "bp-1",
        "registry_digest_set": ("reg-1",),
        "frozen_compile_ref": "compile-1",
        "prompt_hash": "compile-1",
        "provider_lane": "vllm",
        "model_lane": "qwen",
        "parent_provider_lane": "vllm",
        "parent_model_lane": "qwen",
        "anchor_output_hash": "anchor-hash",
        "anchor_output_text": "ANCHOR BODY",
        "anchor_classification": AnchorClassification.LAST_APPROVED,
        "defect_class": DefectClass.SOFT_REPAIRABLE,
        "trigger_source": TriggerSource.X3_JUDGE,
        "delta_lines": ("JUDGE_DELTA: fix clarity on risk.",),
        "semantic_regen_attempt_index": 1,
        "transport_retry_count": 3,
        "max_semantic_regen_attempts": 1,
        "prompt_messages": pm,
        "expected_system_prefix_hash": sys_hash,
    }
    defaults.update(overrides)
    return IncrementalRepairContract(**defaults)  # type: ignore[arg-type]


def test_semantic_budget_exhausted_is_not_transport_retry() -> None:
    contract = _base_contract(semantic_regen_attempt_index=2)
    runner = SameAuthorityRegenRunner()
    refusal = runner.evaluate_refusal(contract)
    assert refusal is not None
    assert refusal.code is RegenRefusalCode.SEMANTIC_REGEN_BUDGET_EXHAUSTED
    assert refusal.semantic_regen_budget_exhausted is True
    receipt = runner.build_refusal_receipt(contract, refusal)
    assert receipt.transport_retry_count == 3
    assert receipt.semantic_regen_attempt_index == 2
    assert receipt.semantic_regen_budget_exhausted is True


def test_anchor_unsafe_refusal() -> None:
    contract = _base_contract(
        anchor_classification=AnchorClassification.REFUSE_UNSAFE,
    )
    refusal = SameAuthorityRegenRunner().evaluate_refusal(contract)
    assert refusal is not None
    assert refusal.code is RegenRefusalCode.ANCHOR_UNSAFE


def test_success_run_emits_heal_compatible_receipt() -> None:
    contract = _base_contract()

    def _fake_provider(messages: list[dict[str, str]]) -> dict[str, object]:
        assert [m["role"] for m in messages] == [
            "system",
            "user",
            "assistant",
            "user",
        ]
        assert "REGEN_DELTA_v1" in messages[-1]["content"]
        return {"content": "REVISED ANCHOR BODY"}

    result = SameAuthorityRegenRunner().run(
        contract,
        provider_generate=_fake_provider,
    )
    assert result.accepted is True
    assert result.receipt is not None
    assert result.receipt.heal_outcome is HealOutcomeStamp.PASS
    assert result.receipt.next_action == "RETURN_TO_E3"
    assert result.receipt.no_prompt_recompile_assertion is True
    assert result.receipt.semantic_regen_attempt_index == 1
    assert result.receipt.transport_retry_count == 3
    heal = result.receipt.to_heal_receipt()
    assert heal.repair_tactic == "incremental_delta_turn_v1"
    assert heal.routes_back_to_e3() is True


def test_mocked_provider_refused() -> None:
    contract = _base_contract(mocked_provider=True)
    refusal = SameAuthorityRegenRunner().evaluate_refusal(contract)
    assert refusal is not None
    assert refusal.code is RegenRefusalCode.MOCKED_PROVIDER_ALLOW


def test_provider_substitution_refused() -> None:
    contract = _base_contract(parent_model_lane="other-model")
    refusal = SameAuthorityRegenRunner().evaluate_refusal(contract)
    assert refusal is not None
    assert refusal.code is RegenRefusalCode.PROVIDER_SUBSTITUTION


def test_recursive_regen_forbidden() -> None:
    contract = _base_contract(nested_heal_without_new_attempt=True)
    refusal = SameAuthorityRegenRunner().evaluate_refusal(contract)
    assert refusal is not None
    assert refusal.code is RegenRefusalCode.RECURSIVE_REGEN_FORBIDDEN


def test_semantic_index_not_panel_max_attempts() -> None:
    """Panel transport max_attempts must not satisfy semantic regen proof."""
    contract = _base_contract(
        semantic_regen_attempt_index=1,
        transport_retry_count=99,
    )
    result = SameAuthorityRegenRunner().run(
        contract,
        provider_generate=lambda _m: {"content": "ok"},
    )
    assert result.receipt is not None
    assert result.receipt.semantic_regen_attempt_index == 1
    assert result.receipt.transport_retry_count == 99
    assert result.receipt.semantic_regen_attempt_index != result.receipt.transport_retry_count
