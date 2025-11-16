"""
Test Suite — Bullet Execution v10.8

Responsibilities:
    • Cover bullet-generation workflows involving L1 strategy and L2 bullet executors.
    • Validate orchestration paths managed by L3 bullet orchestrators.
    • Check alignment with L4 state persistence and L5 safety policies when implemented.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l1_strategy_reasoner import StrategyReasoner
from l2_bullet_execution import BulletExecutionAgent


def test_bullet_generation_from_strategy_plan():
    state = {"objective": "summarize", "deliverables": ["point a", "point b"]}
    plan = StrategyReasoner().plan(state)
    patch = BulletExecutionAgent().execute(plan, state)

    assert patch["last_bullets"] == ["- point a", "- point b"]
    assert patch["messages"][-1]["format"] == "bullets"
