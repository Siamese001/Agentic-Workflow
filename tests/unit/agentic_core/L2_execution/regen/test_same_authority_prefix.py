"""NC-1..NC-3 and thread shape tests for same-authority regen (ADR-085 W1)."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
)
from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages
from agentic_core.L2_execution.regen.prefix_digest import (
    compute_delta_message_hash,
    compute_system_prefix_hash,
)
from agentic_core.L2_execution.regen.same_authority_bundle import SameAuthorityBundle
from agentic_core.L2_execution.regen.same_authority_errors import (
    FrozenPrefixMutationError,
    SameAuthorityBundleDriftError,
)
from agentic_core.L2_execution.regen.same_authority_thread import (
    assert_bundle_unchanged,
    assert_prefix_unchanged,
)


@pytest.fixture()
def slotted_messages() -> PromptMessages:
    artifact = CompiledPromptArtifact(
        trace_id="t-regen",
        system_version_hash="h-regen",
        final_system_string="",
        final_user_string="",
        allowed_tools_schema=[],
        tokens=10,
        slots_used=["S0", "D0", "U0"],
        signature="",
    )
    slots = {
        "S0": AuthoritySlot(
            slot_type="S0",
            content="SYSTEM_CONSTITUTION",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L0",
        ),
        "D0": AuthoritySlot(
            slot_type="D0",
            content="DEVELOPER_FENCE",
            authority_level=AuthorityLevel.BINDING,
            source_layer="L5",
        ),
        "U0": AuthoritySlot(
            slot_type="U0",
            content="INITIAL_USER_ASK",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }
    return PromptMessages.from_artifact(artifact, slots=slots)


def _bundle_for(messages: PromptMessages) -> SameAuthorityBundle:
    sys_hash = compute_system_prefix_hash(messages.system_text())
    return SameAuthorityBundle(
        frozen_compile_ref="compile-abc123",
        system_prefix_hash=sys_hash,
        policy_hash="pol-1",
        blueprint_hash="bp-1",
        registry_digest_set=("reg-a", "reg-b"),
        replay_key="replay-key-1",
        provider_lane="vllm",
        model_lane="Qwen/Qwen2.5-32B-Instruct-AWQ",
        capability_token="cap-1",
        sandbox_envelope="sandbox-1",
        prompt_hash="compile-abc123",
    )


def test_append_same_authority_turn_chat_shape(slotted_messages: PromptMessages) -> None:
    state = slotted_messages.append_same_authority_turn(
        frozen_compile_ref="compile-abc123",
        policy_hash="pol-1",
        blueprint_hash="bp-1",
        registry_digest_set=("reg-a", "reg-b"),
        replay_key="replay-key-1",
        provider_lane="vllm",
        model_lane="Qwen/Qwen2.5-32B-Instruct-AWQ",
        anchor_assistant_content="ANCHOR_DRAFT_BODY",
        delta_user_content="REGEN_DELTA_v1\nPROMPT_LOCK\nJUDGE_DELTA: fix tone",
    )
    msgs = state.to_chat_messages()
    roles = [m["role"] for m in msgs]
    assert roles == ["system", "developer", "user", "assistant", "user"]
    assert "SYSTEM_CONSTITUTION" in msgs[0]["content"]
    assert "DEVELOPER_FENCE" in msgs[1]["content"]
    assert msgs[2]["content"] == "INITIAL_USER_ASK"
    assert msgs[3]["content"] == "ANCHOR_DRAFT_BODY"
    assert "REGEN_DELTA_v1" in msgs[4]["content"]
    assert state.delta_message_hash == compute_delta_message_hash(msgs[4]["content"])


def test_nc1_prefix_mutation_after_append_fails(slotted_messages: PromptMessages) -> None:
    state = slotted_messages.append_same_authority_turn(
        frozen_compile_ref="compile-abc123",
        policy_hash="pol-1",
        blueprint_hash="bp-1",
        registry_digest_set=("reg-a", "reg-b"),
        replay_key="replay-key-1",
        provider_lane="vllm",
        model_lane="Qwen/Qwen2.5-32B-Instruct-AWQ",
        anchor_assistant_content="ANCHOR",
        delta_user_content="DELTA",
    )
    mutated = PromptMessages(
        slot_map={
            **slotted_messages.slot_map,
            "S0": "MUTATED_SYSTEM",
        },
        ordered_slots=slotted_messages.ordered_slots,
    )
    with pytest.raises(FrozenPrefixMutationError):
        assert_prefix_unchanged(state, mutated)


def test_nc2_bundle_drift_fails(slotted_messages: PromptMessages) -> None:
    bundle = _bundle_for(slotted_messages)
    state = slotted_messages.append_same_authority_turn(
        frozen_compile_ref=bundle.frozen_compile_ref,
        policy_hash=bundle.policy_hash,
        blueprint_hash=bundle.blueprint_hash,
        registry_digest_set=bundle.registry_digest_set,
        replay_key=bundle.replay_key,
        provider_lane=bundle.provider_lane,
        model_lane=bundle.model_lane,
        anchor_assistant_content="ANCHOR",
        delta_user_content="DELTA",
    )
    drifted = SameAuthorityBundle(
        frozen_compile_ref=bundle.frozen_compile_ref,
        system_prefix_hash=bundle.system_prefix_hash,
        policy_hash="pol-CHANGED",
        blueprint_hash=bundle.blueprint_hash,
        registry_digest_set=bundle.registry_digest_set,
        replay_key=bundle.replay_key,
        provider_lane=bundle.provider_lane,
        model_lane=bundle.model_lane,
    )
    with pytest.raises(SameAuthorityBundleDriftError):
        assert_bundle_unchanged(state, drifted)


def test_nc3_preserves_compile_ref_and_new_delta_hash_only(
    slotted_messages: PromptMessages,
) -> None:
    bundle = _bundle_for(slotted_messages)
    state = slotted_messages.append_same_authority_turn(
        frozen_compile_ref=bundle.frozen_compile_ref,
        policy_hash=bundle.policy_hash,
        blueprint_hash=bundle.blueprint_hash,
        registry_digest_set=bundle.registry_digest_set,
        replay_key=bundle.replay_key,
        provider_lane=bundle.provider_lane,
        model_lane=bundle.model_lane,
        anchor_assistant_content="ANCHOR",
        delta_user_content="DELTA_ONE",
    )
    assert state.bundle.frozen_compile_ref == "compile-abc123"
    assert state.delta_message_hash == compute_delta_message_hash("DELTA_ONE")
    state2 = slotted_messages.append_same_authority_turn(
        frozen_compile_ref=bundle.frozen_compile_ref,
        policy_hash=bundle.policy_hash,
        blueprint_hash=bundle.blueprint_hash,
        registry_digest_set=bundle.registry_digest_set,
        replay_key=bundle.replay_key,
        provider_lane=bundle.provider_lane,
        model_lane=bundle.model_lane,
        anchor_assistant_content="ANCHOR",
        delta_user_content="DELTA_TWO",
    )
    assert state2.bundle.frozen_compile_ref == state.bundle.frozen_compile_ref
    assert state2.delta_message_hash != state.delta_message_hash
