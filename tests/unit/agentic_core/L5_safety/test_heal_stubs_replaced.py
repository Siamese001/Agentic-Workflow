"""Tests verifying W3 stub heal() replacements return valid HealResult dicts.

Plan: .windsurf/plans/l2-execute-v2-agent-conformance-c8e4f1.md §W3.
Replaces: NotImplementedError + stub `{"status": "skipped"}` dicts.
"""

from __future__ import annotations

from agentic_core.L5_safety.types.heal_request_types import HealOutcome, HealResult


REQUIRED_KEYS = {
    "outcome",
    "reason_code",
    "parent_packet_id",
    "repair_count",
    "policy_hash",
    "blueprint_hash",
    "evidence",
    "message",
}


def _assert_valid_heal_dict(d: dict) -> None:
    assert isinstance(d, dict), f"heal() must return dict, got {type(d).__name__}"
    missing = REQUIRED_KEYS - d.keys()
    assert not missing, f"heal() dict missing HealResult keys: {missing}"
    assert d["outcome"] in {o.value for o in HealOutcome}, f"invalid outcome: {d['outcome']}"
    # Verify round-trip through HealResult dataclass: raises if shape is wrong
    r = HealResult(
        outcome=d["outcome"],
        reason_code=d["reason_code"],
        parent_packet_id=d["parent_packet_id"],
        repair_count=d["repair_count"],
        policy_hash=d["policy_hash"],
        blueprint_hash=d["blueprint_hash"],
        evidence=d["evidence"],
        message=d["message"],
    )
    assert r.to_dict() == d


class TestStructuredEngineAgentHeal:
    def test_agentplan_heal_returns_needs_help(self):
        from agentic_core.L2_execution.reasoning.StructuredEngineAgent import AgentPlan

        plan = AgentPlan(reasoning="test", tool_calls=[])
        result = plan.heal({"type": "bad_structure"})
        _assert_valid_heal_dict(result)
        assert result["outcome"] == "NEEDS_HELP"
        assert result["reason_code"] == "data_structure_not_healable"

    def test_agentplan_heal_handles_empty_violation(self):
        from agentic_core.L2_execution.reasoning.StructuredEngineAgent import AgentPlan

        plan = AgentPlan(reasoning="t", tool_calls=[])
        result = plan.heal({})
        _assert_valid_heal_dict(result)
        assert result["parent_packet_id"] == "unknown"

    def test_agentplan_heal_handles_none_violation(self):
        from agentic_core.L2_execution.reasoning.StructuredEngineAgent import AgentPlan

        plan = AgentPlan(reasoning="t", tool_calls=[])
        result = plan.heal(None)
        _assert_valid_heal_dict(result)
        assert result["outcome"] == "NEEDS_HELP"

    def test_agentplan_heal_propagates_snapshot_from_violation(self):
        from agentic_core.L2_execution.reasoning.StructuredEngineAgent import AgentPlan

        plan = AgentPlan(reasoning="t", tool_calls=[])
        result = plan.heal(
            {
                "parent_packet_id": "pkt-99",
                "policy_hash": "pol-abc",
                "blueprint_hash": "bp-xyz",
            }
        )
        assert result["parent_packet_id"] == "pkt-99"
        assert result["policy_hash"] == "pol-abc"
        assert result["blueprint_hash"] == "bp-xyz"


class TestBaseProactiveAgentHeal:
    def test_heal_returns_needs_help_shape(self):
        from apps_shared.reasoning import BaseProactiveAgent as module

        class _Stub:
            __class__ = type("FakeSub", (), {"__name__": "FakeProactive"})

        result = module.BaseProactiveAgent.heal(_Stub(), {"type": "lint_fail"})
        _assert_valid_heal_dict(result)
        assert result["outcome"] == "NEEDS_HELP"
        assert result["reason_code"] == "base_heal_not_overridden"

    def test_heal_handles_none_violation_gracefully(self):
        from apps_shared.reasoning import BaseProactiveAgent as module

        class _Stub:
            pass

        result = module.BaseProactiveAgent.heal(_Stub(), {})
        _assert_valid_heal_dict(result)
        assert result["parent_packet_id"] == "unknown"


class TestBaseReflectionAgentHeal:
    def test_heal_returns_needs_help_shape(self):
        from apps_shared.reasoning import BaseReflectionAgent as module

        class _Stub:
            pass

        result = module.BaseReflectionAgent.heal(_Stub(), {"type": "review_fail"})
        _assert_valid_heal_dict(result)
        assert result["outcome"] == "NEEDS_HELP"
        assert result["reason_code"] == "base_heal_not_overridden"


class TestStructuredEngineAgentHealRepository:
    def test_heal_repository_returns_needs_help_not_raises(self):
        from agentic_core.L2_execution.reasoning import StructuredEngineAgent as module

        class _Stub:
            pass

        result = module.StructuredEngineAgent.heal_repository(_Stub())
        _assert_valid_heal_dict(result)
        assert result["outcome"] == "NEEDS_HELP"
        assert result["reason_code"] == "heal_repository_not_implemented"
