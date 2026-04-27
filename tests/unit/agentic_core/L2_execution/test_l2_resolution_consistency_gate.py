"""Unit tests for resolution_consistency_gate (04.5a INV-RC-1..8).

Covers the pure gate function in isolation. Pipeline integration tests
live in test_l2_pipeline_resolution_invariant.py.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.orchestration.resolution_consistency_gate import (
    MISMATCH_DECISIVE_RULE_ID,
    ResolutionMismatchError,
    assert_validator_heal_resolution_match,
)
from agentic_core.L2_execution.types.l2_resolution_context import (
    L2ResolutionContext,
    RepairAuthorityClass,
    compute_resolution_digest,
)


def _ctx(**overrides: object) -> L2ResolutionContext:
    base = {
        "request_id": "req-1",
        "run_id": "run-1",
        "trace_id": "trace-1",
        "route_id": "route-1",
        "step_id": "step-1",
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
        "allowed_repair_types": ("retry_same_call",),
        "max_repair_count": 3,
        "frozen_execution_context_hash": "fe" + "0" * 62,
        "resolver_digest": "rs" + "0" * 62,
    }
    base.update(overrides)
    return L2ResolutionContext(**base)  # type: ignore[arg-type]


class TestHappyPath:
    def test_matching_contexts_pass(self) -> None:
        v = _ctx()
        h = _ctx()
        d = compute_resolution_digest(v)
        # Should NOT raise.
        assert_validator_heal_resolution_match(
            validator_context=v,
            heal_context=h,
            validator_digest=d,
            heal_digest=d,
        )


class TestMismatch:
    @pytest.mark.parametrize(
        ("override", "expected_field"),
        [
            ({"agent_id": "agent-B"}, "agent_id"),
            ({"agent_version": "2.0.0"}, "agent_version"),
            ({"policy_hash": "x" * 64}, "policy_hash"),
            ({"blueprint_hash": "x" * 64}, "blueprint_hash"),
            ({"capability_scope_hash": "x" * 64}, "capability_scope_hash"),
            ({"sandbox_envelope_hash": "x" * 64}, "sandbox_envelope_hash"),
            ({"replay_key": "x" * 64}, "replay_key"),
            ({"snapshot_manifest_hash": "x" * 64}, "snapshot_manifest_hash"),
            ({"provider_lane": "anthropic"}, "provider_lane"),
            (
                {"repair_authority_class": RepairAuthorityClass.ESCALATE_REQUIRED},
                "repair_authority_class",
            ),
        ],
    )
    def test_field_mismatch_raises_with_specific_field(
        self, override: dict[str, object], expected_field: str
    ) -> None:
        v = _ctx()
        h = _ctx(**override)
        with pytest.raises(ResolutionMismatchError) as ei:
            assert_validator_heal_resolution_match(
                validator_context=v,
                heal_context=h,
                validator_digest=compute_resolution_digest(v),
                heal_digest=compute_resolution_digest(h),
            )
        ev = ei.value.evidence
        assert ev.decisive_rule_id == MISMATCH_DECISIVE_RULE_ID
        assert ev.first_mismatched_field == expected_field
        assert ev.validator_resolution_digest != ev.heal_resolution_digest


class TestDefaultAgentFallback:
    """INV-RC-8: default-agent fallback is forbidden on either side."""

    def test_validator_default_agent_blocks(self) -> None:
        v = _ctx(agent_id="default")
        h = _ctx()
        with pytest.raises(ResolutionMismatchError) as ei:
            assert_validator_heal_resolution_match(
                validator_context=v,
                heal_context=h,
                validator_digest=compute_resolution_digest(v),
                heal_digest=compute_resolution_digest(h),
            )
        assert "default/fallback" in ei.value.evidence.reason
        assert ei.value.evidence.first_mismatched_field == "agent_id"

    def test_heal_default_agent_blocks(self) -> None:
        v = _ctx()
        h = _ctx(agent_id="fallback")
        with pytest.raises(ResolutionMismatchError) as ei:
            assert_validator_heal_resolution_match(
                validator_context=v,
                heal_context=h,
                validator_digest=compute_resolution_digest(v),
                heal_digest=compute_resolution_digest(h),
            )
        assert "default/fallback" in ei.value.evidence.reason


class TestDigestFormat:
    def test_non_hex_validator_digest_blocks(self) -> None:
        v = _ctx()
        h = _ctx()
        with pytest.raises(ResolutionMismatchError) as ei:
            assert_validator_heal_resolution_match(
                validator_context=v,
                heal_context=h,
                validator_digest="not-a-real-digest",
                heal_digest=compute_resolution_digest(h),
            )
        assert ei.value.evidence.first_mismatched_field == "validator_resolution_digest"

    def test_non_hex_heal_digest_blocks(self) -> None:
        v = _ctx()
        h = _ctx()
        d = compute_resolution_digest(v)
        with pytest.raises(ResolutionMismatchError) as ei:
            assert_validator_heal_resolution_match(
                validator_context=v,
                heal_context=h,
                validator_digest=d,
                heal_digest="not-hex",
            )
        assert ei.value.evidence.first_mismatched_field == "heal_resolution_digest"


class TestDigestContextInconsistency:
    """Defense-in-depth: when digests match but contexts diverge."""

    def test_matching_digests_with_diverging_contexts_blocks(self) -> None:
        v = _ctx()
        h = _ctx(agent_id="agent-Z")
        # Force a "lying" matched digest pair to simulate a hash collision
        # OR a buggy compute_resolution_digest. The gate must still catch
        # the field-level divergence.
        forged_digest = compute_resolution_digest(v)
        with pytest.raises(ResolutionMismatchError) as ei:
            assert_validator_heal_resolution_match(
                validator_context=v,
                heal_context=h,
                validator_digest=forged_digest,
                heal_digest=forged_digest,  # forged equality
            )
        assert ei.value.evidence.first_mismatched_field == "agent_id"
        assert "field-wise" in ei.value.evidence.reason


class TestEvidencePopulated:
    def test_evidence_carries_required_phase5_fields(self) -> None:
        v = _ctx(agent_id="agent-A", validator_id="v-A")
        h = _ctx(agent_id="agent-B", validator_id="v-B")
        with pytest.raises(ResolutionMismatchError) as ei:
            assert_validator_heal_resolution_match(
                validator_context=v,
                heal_context=h,
                validator_digest=compute_resolution_digest(v),
                heal_digest=compute_resolution_digest(h),
            )
        ev = ei.value.evidence
        assert ev.trace_id == "trace-1"
        assert ev.request_id == "req-1"
        assert ev.run_id == "run-1"
        assert ev.route_id == "route-1"
        assert ev.step_id == "step-1"
        assert ev.agent_id_validator == "agent-A"
        assert ev.agent_id_heal == "agent-B"
        assert ev.validator_id_validator == "v-A"
        assert ev.validator_id_heal == "v-B"
        assert ev.decisive_rule_id == MISMATCH_DECISIVE_RULE_ID
        # to_dict round-trip
        d = ev.to_dict()
        assert d["decisive_rule_id"] == MISMATCH_DECISIVE_RULE_ID
        assert d["trace_id"] == "trace-1"
