"""Unit tests for L2ResolutionContext (04.5a Phase 1 + Phase 2).

Covers:
  - Field-validation rules in __post_init__
  - Canonical-JSON serialization determinism
  - SHA-256 digest stability across processes (via deterministic content)
  - first_mismatched_field deterministic field-order traversal
  - is_default_agent_fallback sentinel detection
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L2_execution.types.l2_resolution_context import (
    L2ResolutionContext,
    RepairAuthorityClass,
    ResolutionContextField,
    compute_resolution_digest,
    is_default_agent_fallback,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx(
    *,
    agent_id: str = "agent-A",
    agent_version: str = "1.0.0",
    policy_hash: str = "p" * 64,
    blueprint_hash: str = "b" * 64,
    capability_scope_hash: str = "c" * 64,
    sandbox_envelope_hash: str = "s" * 64,
    replay_key: str = "r" * 64,
    snapshot_manifest_hash: str = "m" * 64,
    provider_lane: str = "deterministic",
    repair_authority_class: RepairAuthorityClass = RepairAuthorityClass.LOCAL_SAFE_ONLY,
    allowed_repair_types: tuple[str, ...] = ("retry_same_call", "json_repair"),
    max_repair_count: int = 3,
    validator_id: str = "validator-A",
) -> L2ResolutionContext:
    return L2ResolutionContext(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        route_id="route-1",
        step_id="step-1",
        agent_id=agent_id,
        agent_type="executor",
        agent_version=agent_version,
        agent_profile_hash="ah" + "0" * 62,
        validator_id=validator_id,
        validator_version="1.0.0",
        capability_token="cap-token-1",
        capability_scope_hash=capability_scope_hash,
        sandbox_envelope_hash=sandbox_envelope_hash,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        snapshot_manifest_hash=snapshot_manifest_hash,
        tool_registry_digest="td" + "0" * 62,
        model_registry_digest="md" + "0" * 62,
        provider_lane=provider_lane,
        repair_authority_class=repair_authority_class,
        allowed_repair_types=allowed_repair_types,
        max_repair_count=max_repair_count,
        frozen_execution_context_hash="fe" + "0" * 62,
        resolver_digest="rs" + "0" * 62,
    )


# ---------------------------------------------------------------------------
# Construction + validation
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_happy_path_valid_context_constructs(self) -> None:
        ctx = _ctx()
        assert ctx.agent_id == "agent-A"
        assert ctx.repair_authority_class is RepairAuthorityClass.LOCAL_SAFE_ONLY

    def test_frozen_dataclass_blocks_mutation(self) -> None:
        ctx = _ctx()
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.agent_id = "agent-B"  # type: ignore[misc]

    @pytest.mark.parametrize(
        "field_name",
        [
            "request_id",
            "run_id",
            "trace_id",
            "route_id",
            "agent_id",
            "agent_type",
            "validator_id",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
        ],
    )
    def test_empty_required_string_fails(self, field_name: str) -> None:
        kwargs = {
            "request_id": "req-1",
            "run_id": "run-1",
            "trace_id": "trace-1",
            "route_id": "route-1",
            "step_id": None,
            "agent_id": "agent-A",
            "agent_type": "executor",
            "agent_version": "1.0.0",
            "agent_profile_hash": "ah" + "0" * 62,
            "validator_id": "v-A",
            "validator_version": "1.0.0",
            "capability_token": "cap-1",
            "capability_scope_hash": "c" * 64,
            "sandbox_envelope_hash": "s" * 64,
            "policy_hash": "p" * 64,
            "blueprint_hash": "b" * 64,
            "replay_key": "r" * 64,
            "snapshot_manifest_hash": "m" * 64,
            "tool_registry_digest": "td" + "0" * 62,
            "model_registry_digest": "md" + "0" * 62,
            "provider_lane": "deterministic",
            "repair_authority_class": RepairAuthorityClass.LOCAL_SAFE_ONLY,
            "allowed_repair_types": ("retry",),
            "max_repair_count": 3,
            "frozen_execution_context_hash": "fe" + "0" * 62,
            "resolver_digest": "rs" + "0" * 62,
        }
        kwargs[field_name] = ""
        with pytest.raises(ValueError, match=field_name):
            L2ResolutionContext(**kwargs)

    def test_negative_max_repair_count_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_repair_count"):
            _ctx(max_repair_count=-1)

    def test_step_id_can_be_none(self) -> None:
        ctx = L2ResolutionContext(
            request_id="r",
            run_id="r",
            trace_id="t",
            route_id="ro",
            step_id=None,
            agent_id="a",
            agent_type="x",
            agent_version="1",
            agent_profile_hash="ah" + "0" * 62,
            validator_id="v",
            validator_version="1",
            capability_token="c",
            capability_scope_hash="c" * 64,
            sandbox_envelope_hash="s" * 64,
            policy_hash="p" * 64,
            blueprint_hash="b" * 64,
            replay_key="r" * 64,
            snapshot_manifest_hash="m" * 64,
            tool_registry_digest="td" + "0" * 62,
            model_registry_digest="md" + "0" * 62,
            provider_lane="deterministic",
            repair_authority_class=RepairAuthorityClass.NONE,
            allowed_repair_types=(),
            max_repair_count=0,
            frozen_execution_context_hash="fe" + "0" * 62,
            resolver_digest="rs" + "0" * 62,
        )
        assert ctx.step_id is None


# ---------------------------------------------------------------------------
# Digest determinism
# ---------------------------------------------------------------------------


class TestDigest:
    def test_same_fields_yield_same_digest(self) -> None:
        a = _ctx()
        b = _ctx()
        assert a.digest() == b.digest()
        assert compute_resolution_digest(a) == compute_resolution_digest(b)

    def test_digest_is_64_char_hex(self) -> None:
        d = _ctx().digest()
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    @pytest.mark.parametrize(
        ("kwargs", "expect_change"),
        [
            ({"agent_id": "agent-Z"}, True),
            ({"agent_version": "9.9.9"}, True),
            ({"policy_hash": "x" * 64}, True),
            ({"blueprint_hash": "x" * 64}, True),
            ({"capability_scope_hash": "x" * 64}, True),
            ({"sandbox_envelope_hash": "x" * 64}, True),
            ({"replay_key": "x" * 64}, True),
            ({"snapshot_manifest_hash": "x" * 64}, True),
            ({"provider_lane": "anthropic"}, True),
            (
                {"repair_authority_class": RepairAuthorityClass.ESCALATE_REQUIRED},
                True,
            ),
            ({"allowed_repair_types": ("retry_same_call",)}, True),
            ({"max_repair_count": 5}, True),
        ],
    )
    def test_field_change_changes_digest(self, kwargs: dict[str, object], expect_change: bool) -> None:
        baseline = _ctx().digest()
        mutated = _ctx(**kwargs).digest()  # type: ignore[arg-type]
        if expect_change:
            assert baseline != mutated
        else:
            assert baseline == mutated

    def test_first_mismatched_field_returns_first_in_canonical_order(self) -> None:
        # Mutate two fields; the field that appears earlier in
        # ResolutionContextField order MUST be reported first.
        a = _ctx()
        # provider_lane sits AFTER policy_hash in the canonical order,
        # so when both differ, policy_hash must win.
        b = _ctx(policy_hash="x" * 64, provider_lane="anthropic")
        first = a.first_mismatched_field(b)
        assert first == ResolutionContextField.POLICY_HASH.value

    def test_first_mismatched_field_empty_when_equal(self) -> None:
        a = _ctx()
        b = _ctx()
        assert a.first_mismatched_field(b) == ""


# ---------------------------------------------------------------------------
# Default-agent fallback sentinel
# ---------------------------------------------------------------------------


class TestDefaultAgentFallback:
    @pytest.mark.parametrize(
        "agent_id",
        ["default", "fallback", "default-agent", "<default>", "DEFAULT", "Fallback"],
    )
    def test_sentinel_agent_ids_detected(self, agent_id: str) -> None:
        assert is_default_agent_fallback(_ctx(agent_id=agent_id)) is True

    @pytest.mark.parametrize(
        "agent_id",
        ["agent-A", "ResearchAgent", "exec-1", "qwen-vllm-routed-agent-7"],
    )
    def test_real_agent_ids_pass(self, agent_id: str) -> None:
        assert is_default_agent_fallback(_ctx(agent_id=agent_id)) is False
