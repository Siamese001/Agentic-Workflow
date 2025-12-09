"""Grouped L4 state and memory tests."""
"""
Test Suite — Context Budget v10.8

Responsibilities:
    • Validate budgeting mechanics for tokens and compute across workflows.
    • Ensure coordination between context budget management and memory operations.
    • Confirm orchestration hooks respect budgeting constraints in L3 flows.

This test file is scaffolded for Priority 0; implementation comes later.
"""
import copy

from l4_memory import ContextBudget
from l4_memory import MemoryManager
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
import copy

from l4_memory import (
    get_conversational_view,
    get_prompt_context_view,
    get_retrieval_view,
)


def test_conversational_view_defaults_and_keys():
    state = {}
    view = get_conversational_view(state)

    assert set(view.keys()) == {"messages", "summary"}
    assert view["messages"] == []
    assert view["summary"] == ""
    assert state == {}


def test_retrieval_view_defaults_and_keys():
    state = {}
    view = get_retrieval_view(state)

    assert set(view.keys()) == {"rag_history", "world"}
    assert view["rag_history"] == []
    assert view["world"] == []
    assert state == {}


def test_prompt_context_view_combines_all_fields_without_mutation():
    state = {
        "messages": ["hello"],
        "summary": "s",
        "rag_history": ["rag"],
        "world": ["w"],
    }
    original_state = copy.deepcopy(state)

    view = get_prompt_context_view(state)

    assert set(view.keys()) == {"messages", "summary", "rag_history", "world"}
    assert view["messages"] == ["hello"]
    assert view["summary"] == "s"
    assert view["rag_history"] == ["rag"]
    assert view["world"] == ["w"]
    assert state == original_state


def test_views_deep_copy_list_fields():
    state = {
        "messages": [{"role": "user", "content": "hi"}],
        "rag_history": [{"doc": "a"}],
        "world": [{"fact": 1}],
    }

    conversational = get_conversational_view(state)
    retrieval = get_retrieval_view(state)
    prompt_context = get_prompt_context_view(state)

    conversational["messages"][0]["content"] = "changed"
    retrieval["rag_history"][0]["doc"] = "changed"
    retrieval["world"].append({"fact": 2})
    prompt_context["messages"].append({"role": "assistant", "content": "reply"})

    assert state["messages"][0]["content"] == "hi"
    assert state["rag_history"][0]["doc"] == "a"
    assert state["world"] == [{"fact": 1}]
"""
Test Suite — State Adapter v10.8

Responsibilities:
    • Validate the L4 state adapter interfaces across orchestrators and memory managers.
    • Ensure deterministic state mutations and compatibility with execution outputs.
    • Confirm integration points for safety and policy annotations at L5.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l4_state import StateAdapter
from utils_types import Phase, StatePatch


def test_state_adapter_applies_patch_and_phase():
    adapter = StateAdapter()
    patch = StatePatch({"messages": [{"role": "assistant", "content": "hi"}], "phase": Phase.PLANNING.value})

    state = adapter.apply_patch(patch)
    assert state["messages"][-1]["content"] == "hi"
    assert adapter.state_machine.phase == Phase.PLANNING
    assert adapter.state["phase"] == Phase.PLANNING.value
    assert adapter.state["phase_metadata"]["phase"] == Phase.PLANNING.value


def test_state_adapter_phase_history_and_metadata_updates():
    adapter = StateAdapter()

    planning_state = adapter.apply_patch(StatePatch({"phase": Phase.PLANNING.value}))
    assert planning_state["phase"] == Phase.PLANNING.value
    assert planning_state["phase_metadata"]["phase"] == Phase.PLANNING.value

    executing_state = adapter.apply_patch(StatePatch({"phase": Phase.EXECUTING.value}))
    assert executing_state["phase"] == Phase.EXECUTING.value
    assert executing_state["phase_metadata"]["phase"] == Phase.EXECUTING.value

    if hasattr(adapter.state_machine, "history"):
        assert adapter.state_machine.history() == [
            Phase.INIT.value,
            Phase.PLANNING.value,
            Phase.EXECUTING.value,
        ]
"""
Test Suite — State & Memory v10.8

Validates memory budgeting, state validation, and world-model normalization.
"""
from l4_state import StateAdapter
from l4_state import validate
from utils_types import StatePatch
from l4_memory import normalize_world_facts


def test_high_volume_messages_pruned_to_budget():
    adapter = StateAdapter()
    patch = StatePatch({"messages": [{"role": "user", "content": f"m{i}"} for i in range(500)]})

    state = adapter.apply_patch(patch)

    assert len(state["messages"]) == adapter.memory_manager.context_budget.config.max_messages
    assert state["messages"][-1]["content"] == "m499"


def test_validation_flags_missing_keys():
    result = validate({"messages": [], "summary": ""})

    assert "rag_history" in result["missing"]
    assert "world" in result["missing"]
    assert "phase" in result["missing"]


def test_validation_warns_on_inconsistent_fields():
    state = {
        "messages": [],
        "rag_history": [],
        "summary": "",
        "world": [],
        "session": {},
        "metadata": {},
        "phase": "init",
        "phase_metadata": {},
        "draft": "draft text",
        "qa_report": {"issues": []},
    }

    result = validate(state)

    assert any("draft" in warning for warning in result["cross_field_warnings"])
    assert any("qa_report" in warning for warning in result["cross_field_warnings"])


def test_world_model_normalization():
    facts = [
        {"category": "event", "content": "incident", "origin": "user"},
        {"content": 123, "origin": "unknown", "category": "unknown"},
        "string_fact",
    ]

    normalized = normalize_world_facts(facts)

    assert normalized[0] == {"category": "event", "content": "incident", "origin": "user"}
    assert normalized[1]["category"] == "entity"
    assert normalized[1]["origin"] == "system"
    assert normalized[1]["content"] == "123"
    assert normalized[2]["content"] == "string_fact"
"""
Test Suite — State Schema v10.8

Validates the default shape and backward compatibility of the state
representation, ensuring new world-model fields coexist with existing
structures.
"""

from l4_state import StateAdapter
from utils_types import StatePatch


def test_state_schema_defaults_include_world_and_metadata():
    adapter = StateAdapter()
    state = adapter.state

    expected_keys = {"messages", "rag_history", "summary", "world", "session", "metadata", "phase"}
    assert expected_keys.issubset(state.keys())

    assert isinstance(state.get("messages"), list)
    assert isinstance(state.get("rag_history"), list)
    assert isinstance(state.get("summary"), str)
    assert isinstance(state.get("world"), list)
    assert isinstance(state.get("session"), dict)
    assert isinstance(state.get("metadata"), dict)
    assert isinstance(state.get("phase"), str)


def test_apply_patch_preserves_default_fields_when_not_patched():
    adapter = StateAdapter()
    base_state = adapter.state

    patch = StatePatch({
        "summary": "updated summary",
        "messages": [{"role": "user", "content": "hello"}],
    })

    updated_state = adapter.apply_patch(patch)

    expected_keys = {"messages", "rag_history", "summary", "world", "session", "metadata", "phase"}
    assert expected_keys.issubset(updated_state.keys())

    assert updated_state["summary"] == "updated summary"
    assert updated_state["messages"][-1]["content"] == "hello"

    assert updated_state["rag_history"] == base_state["rag_history"]
    assert updated_state["world"] == base_state["world"]
    assert updated_state["session"] == base_state["session"]
    assert updated_state["metadata"] == base_state["metadata"]
    assert updated_state["phase"] == base_state["phase"]


def test_apply_patch_retains_defaults_for_new_fields():
    adapter = StateAdapter()

    patch = StatePatch({"rag_history": [{"query": "foo", "context": []}]})
    updated_state = adapter.apply_patch(patch)

    assert updated_state["rag_history"][-1]["query"] == "foo"
    assert updated_state["world"] == []
    assert updated_state["session"] == {}
    assert updated_state["metadata"] == {}
