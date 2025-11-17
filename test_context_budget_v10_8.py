"""
Test Suite — Context Budget v10.8

Responsibilities:
    • Validate budgeting mechanics for tokens and compute across workflows.
    • Ensure coordination between context budget management and memory operations.
    • Confirm orchestration hooks respect budgeting constraints in L3 flows.

This test file is scaffolded for Priority 0; implementation comes later.
"""
import copy

from l4_context_budget import ContextBudget
from l4_memory_manager import MemoryManager
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


def test_token_budget_prunes_messages_deterministically():
    config = BudgetConfig(max_prompt_tokens=5)
    budget = ContextBudget(config)

    messages = [
        {"role": "user", "content": "one two three"},
        {"role": "assistant", "content": "four five"},
        {"role": "assistant", "content": "six"},
    ]

    pruned_once = budget.prune_messages_by_tokens(messages)
    pruned_twice = budget.prune_messages_by_tokens(messages)

    assert pruned_once == pruned_twice
    assert pruned_once == [{"role": "assistant", "content": "four five"}, {"role": "assistant", "content": "six"}]
    assert messages[0]["content"] == "one two three"


def test_token_budget_prunes_rag_items():
    config = BudgetConfig(max_retrieval_tokens=4)
    budget = ContextBudget(config)

    items = [
        {"query": "q1", "evidence": "alpha beta"},
        {"query": "q2", "evidence": "gamma delta"},
        {"query": "q3", "evidence": "epsilon"},
    ]

    pruned = budget.prune_rag_items_by_tokens(items)

    assert pruned == [{"query": "q2", "evidence": "gamma delta"}, {"query": "q3", "evidence": "epsilon"}]
    assert items[0]["query"] == "q1"


def test_reconcile_state_respects_token_budgets_without_mutation():
    budget = ContextBudget(BudgetConfig(max_prompt_tokens=3, max_retrieval_tokens=2, max_messages=10, max_rag_items=10))
    manager = MemoryManager(budget)
    state = {
        "messages": [
            {"role": "user", "content": "one two"},
            {"role": "assistant", "content": "three four"},
        ],
        "rag_history": [
            {"query": "q1", "evidence": "alpha"},
            {"query": "q2", "evidence": "beta gamma"},
        ],
    }

    original = copy.deepcopy(state)
    reconciled = manager.reconcile_state(state)

    assert reconciled["messages"] == [{"role": "assistant", "content": "three four"}]
    assert reconciled["rag_history"] == [{"query": "q2", "evidence": ["beta gamma"]}]
    assert state == original
