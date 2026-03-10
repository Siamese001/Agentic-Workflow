"""
§Wave4.3 — L2SelfHealingTrigger tests.

1. Contract + determinism: stable JSON, sorted actions, stable trace_id
2. Authorization gating: auto-approved/HIL-approved emit; rejected/pending do NOT
3. SemanticClock enforcement: None → ValueError
4. Idempotency: same authorized inputs → identical JSON
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.self_healing_trigger_types import (
    AUTHORIZED_DECISIONS,
    REJECTED_DECISIONS,
    L2SelfHealingTrigger,
    emit_self_healing_trigger,
    is_healing_authorized,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clock() -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=12, vector_clock=(("L0", 6), ("L2", 6)))


# ===========================================================================
# 1. Contract + determinism
# ===========================================================================


class TestContractDeterminism:
    def test_to_dict_stable_json(self, clock):
        trigger = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="agentic_core/L5_safety/reasoning/HierarchyAgent.py",
            reason_code="mro_violation",
            recommended_actions=["fix_mro", "rerun_tests"],
            risk_tier="high",
            semantic_clock=clock,
        )
        assert trigger is not None
        j = json.dumps(trigger.to_dict(), sort_keys=True, separators=(",", ":"))
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed["artifact_type"] == "SELF_HEALING_TRIGGER"
        assert parsed["semantic_clock"]["tick"] == 12

    def test_recommended_actions_sorted(self, clock):
        trigger = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="target_a",
            reason_code="import_cycle",
            recommended_actions=["z_action", "a_action", "m_action"],
            risk_tier="medium",
            semantic_clock=clock,
        )
        assert trigger is not None
        assert trigger.recommended_actions == ("a_action", "m_action", "z_action")

    def test_duplicate_actions_deduplicated(self, clock):
        trigger = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="target_a",
            reason_code="import_cycle",
            recommended_actions=["fix_import", "fix_import", "rerun_tests"],
            risk_tier="medium",
            semantic_clock=clock,
        )
        assert trigger is not None
        assert trigger.recommended_actions == ("fix_import", "rerun_tests")

    def test_to_dict_has_all_keys(self, clock):
        trigger = emit_self_healing_trigger(
            decision="HIL_APPROVED",
            target="subsystem_x",
            reason_code="stale_write",
            recommended_actions=["rollback"],
            risk_tier="critical",
            semantic_clock=clock,
            policy_config_hash="hash_abc",
            route_context="user_request_heal",
        )
        assert trigger is not None
        d = trigger.to_dict()
        assert set(d.keys()) == {
            "artifact_type",
            "authorization",
            "policy_config_hash",
            "reason_code",
            "recommended_actions",
            "risk_tier",
            "route_context",
            "semantic_clock",
            "target",
            "trace_id",
        }

    def test_frozen_immutable(self, clock):
        trigger = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert trigger is not None
        with pytest.raises(AttributeError):
            trigger.trace_id = "mutated"  # type: ignore[misc]

    def test_wrong_artifact_type_raises(self, clock):
        with pytest.raises(ValueError, match="artifact_type must be"):
            L2SelfHealingTrigger(
                artifact_type="WRONG",
                semantic_clock=clock,
                trace_id="t1",
                target="t",
                reason_code="r",
                recommended_actions=("a",),
                risk_tier="low",
                authorization="AUTO_APPROVED",
            )

    def test_unsorted_actions_raises(self, clock):
        with pytest.raises(ValueError, match="recommended_actions must be sorted"):
            L2SelfHealingTrigger(
                artifact_type="SELF_HEALING_TRIGGER",
                semantic_clock=clock,
                trace_id="t1",
                target="t",
                reason_code="r",
                recommended_actions=("z_action", "a_action"),
                risk_tier="low",
                authorization="AUTO_APPROVED",
            )

    def test_empty_reason_code_raises(self, clock):
        with pytest.raises(ValueError, match="reason_code must be non-empty"):
            L2SelfHealingTrigger(
                artifact_type="SELF_HEALING_TRIGGER",
                semantic_clock=clock,
                trace_id="t1",
                target="t",
                reason_code="",
                recommended_actions=(),
                risk_tier="low",
                authorization="AUTO_APPROVED",
            )

    def test_empty_target_raises(self, clock):
        with pytest.raises(ValueError, match="target must be non-empty"):
            L2SelfHealingTrigger(
                artifact_type="SELF_HEALING_TRIGGER",
                semantic_clock=clock,
                trace_id="t1",
                target="",
                reason_code="r",
                recommended_actions=(),
                risk_tier="low",
                authorization="AUTO_APPROVED",
            )


# ===========================================================================
# 2. Authorization gating
# ===========================================================================


class TestAuthorizationGating:
    def test_auto_approved_emits_trigger(self, clock):
        trigger = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert trigger is not None
        assert trigger.authorization == "AUTO_APPROVED"

    def test_hil_approved_emits_trigger(self, clock):
        trigger = emit_self_healing_trigger(
            decision="HIL_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="high",
            semantic_clock=clock,
        )
        assert trigger is not None
        assert trigger.authorization == "HIL_APPROVED"

    def test_rejected_does_not_emit(self, clock):
        trigger = emit_self_healing_trigger(
            decision="REJECTED",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert trigger is None

    def test_pending_does_not_emit(self, clock):
        trigger = emit_self_healing_trigger(
            decision="PENDING",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert trigger is None

    def test_read_only_does_not_emit(self, clock):
        trigger = emit_self_healing_trigger(
            decision="READ_ONLY",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert trigger is None

    def test_not_approved_does_not_emit(self, clock):
        trigger = emit_self_healing_trigger(
            decision="NOT_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert trigger is None

    def test_unknown_decision_does_not_emit(self, clock):
        trigger = emit_self_healing_trigger(
            decision="UNKNOWN_GARBAGE",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert trigger is None

    def test_is_healing_authorized_helper(self):
        for d in AUTHORIZED_DECISIONS:
            assert is_healing_authorized(d) is True
        for d in REJECTED_DECISIONS:
            assert is_healing_authorized(d) is False

    def test_invalid_authorization_on_direct_construction_raises(self, clock):
        with pytest.raises(ValueError, match="authorization must be one of"):
            L2SelfHealingTrigger(
                artifact_type="SELF_HEALING_TRIGGER",
                semantic_clock=clock,
                trace_id="t1",
                target="t",
                reason_code="r",
                recommended_actions=(),
                risk_tier="low",
                authorization="REJECTED",
            )


# ===========================================================================
# 3. SemanticClock enforcement
# ===========================================================================


class TestSemanticClockEnforcement:
    def test_none_semantic_clock_raises_on_direct_construction(self):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            L2SelfHealingTrigger(
                artifact_type="SELF_HEALING_TRIGGER",
                semantic_clock=None,  # type: ignore[arg-type]
                trace_id="t1",
                target="t",
                reason_code="r",
                recommended_actions=(),
                risk_tier="low",
                authorization="AUTO_APPROVED",
            )

    def test_none_semantic_clock_raises_on_emit(self):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            emit_self_healing_trigger(
                decision="AUTO_APPROVED",
                target="t",
                reason_code="r",
                recommended_actions=["a"],
                risk_tier="low",
                semantic_clock=None,  # type: ignore[arg-type]
            )


# ===========================================================================
# 4. Idempotency
# ===========================================================================


class TestIdempotency:
    def test_same_inputs_byte_identical_json(self, clock):
        def _make():
            return emit_self_healing_trigger(
                decision="AUTO_APPROVED",
                target="agentic_core/L5_safety/reasoning/HierarchyAgent.py",
                reason_code="mro_violation",
                recommended_actions=["fix_mro", "rerun_tests"],
                risk_tier="high",
                semantic_clock=clock,
                policy_config_hash="policy_abc",
            )

        t1 = _make()
        t2 = _make()
        assert t1 is not None and t2 is not None
        j1 = json.dumps(t1.to_dict(), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(t2.to_dict(), sort_keys=True, separators=(",", ":"))
        assert j1 == j2

    def test_trace_id_deterministic_across_calls(self, clock):
        def _make():
            return emit_self_healing_trigger(
                decision="HIL_APPROVED",
                target="t",
                reason_code="r",
                recommended_actions=["a", "b"],
                risk_tier="medium",
                semantic_clock=clock,
            )

        t1 = _make()
        t2 = _make()
        assert t1 is not None and t2 is not None
        assert t1.trace_id == t2.trace_id

    def test_different_tick_different_trace_id(self):
        c1 = SemanticClockSnapshot(tick=1)
        c2 = SemanticClockSnapshot(tick=2)
        t1 = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=c1,
        )
        t2 = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["a"],
            risk_tier="low",
            semantic_clock=c2,
        )
        assert t1 is not None and t2 is not None
        assert t1.trace_id != t2.trace_id

    def test_action_order_independent_same_json(self, clock):
        t1 = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["b_action", "a_action"],
            risk_tier="low",
            semantic_clock=clock,
        )
        t2 = emit_self_healing_trigger(
            decision="AUTO_APPROVED",
            target="t",
            reason_code="r",
            recommended_actions=["a_action", "b_action"],
            risk_tier="low",
            semantic_clock=clock,
        )
        assert t1 is not None and t2 is not None
        j1 = json.dumps(t1.to_dict(), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(t2.to_dict(), sort_keys=True, separators=(",", ":"))
        assert j1 == j2
