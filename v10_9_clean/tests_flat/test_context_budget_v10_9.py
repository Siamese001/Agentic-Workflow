from context_budget_v10_8 import ContextBudgetConfigV10_8, ContextBudgetManagerV10_8
from core_v10_7.services import ContextBudgetManager


def test_context_budget_manager_enforces_limits():
    manager = ContextBudgetManager(max_tokens=10)
    manager.allocate(4)
    manager.allocate(3)
    assert manager.remaining() == 3


def test_context_budget_soft_enforcement_trims_data():
    config = ContextBudgetConfigV10_8(max_episodic_messages=2, max_rag_documents=1, max_summary_chars=10)
    manager = ContextBudgetManagerV10_8(config)
    state = {
        "memory": {"episodic": {"conversation": [1, 2, 3]}},
        "rag": {"documents": ["a", "b"]},
        "summary": "0123456789LONG",
    }
    enforced = manager.enforce_all(state)
    assert enforced["memory"]["episodic"]["conversation"] == [2, 3]
    assert enforced["rag"]["documents"] == ["a"]
    assert enforced["summary"] == "0123456789"
