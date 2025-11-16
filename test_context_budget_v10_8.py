"""
Test Suite — Context Budget v10.8

Responsibilities:
    • Validate budgeting mechanics for tokens and compute across workflows.
    • Ensure coordination between context budget management and memory operations.
    • Confirm orchestration hooks respect budgeting constraints in L3 flows.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l4_context_budget import ContextBudget
from utils_types import BudgetConfig


def test_context_budget_prunes_buffers():
    budget = ContextBudget(BudgetConfig(max_messages=2, max_rag_items=1, max_summary_chars=5))

    messages = budget.prune_messages([
        {"role": "user", "content": "1"},
        {"role": "assistant", "content": "2"},
        {"role": "assistant", "content": "3"},
    ])
    rag_items = budget.prune_rag_items([{"id": 1}, {"id": 2}])
    summary = budget.prune_summary("abcdef")

    assert len(messages) == 2 and messages[0]["content"] == "2"
    assert rag_items == [{"id": 2}]
    assert summary == "bcdef"


def test_context_budget_prunes_world_buffer():
    budget = ContextBudget(BudgetConfig(max_world_items=2))

    world = budget.prune_world([
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ])

    assert world == [{"id": 2}, {"id": 3}]


def test_world_pruning_matches_rag_semantics():
    config = BudgetConfig(max_rag_items=2, max_world_items=2)
    budget = ContextBudget(config)

    items = [{"id": 1}, {"id": 2}, {"id": 3}]

    assert budget.prune_world(items) == budget.prune_rag_items(items)
