"""
Test Suite — Drafting Execution v10.8

Responsibilities:
    • Exercise drafting workflows connecting L1 drafting reasoners and L2 drafting executors.
    • Validate L3 draft orchestration sequences and checkpoint handling.
    • Ensure resulting drafts interface correctly with L4 state and L5 safety layers when available.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l1_drafting_reasoner import DraftingReasoner
from l2_drafting_execution import DraftingExecutionAgent


def test_drafting_pipeline_creates_sections():
    state = {"objective": "Write", "outline": ["Intro", "Body"]}
    plan = DraftingReasoner().plan(state)
    assert plan["sections"] == ["Intro", "Body"]

    patch = DraftingExecutionAgent().execute(plan, state)
    assert "draft" in patch
    assert patch["draft"]["sections"] == ["Intro", "Body"]
