from context_budget_v10_8 import ContextBudgetConfig, ContextBudgetManager


def test_strict_pruning_applies_at_thresholds():
    config = ContextBudgetConfig(
        max_episodic_messages=3, max_rag_documents=2, max_summary_chars=10
    )
    manager = ContextBudgetManager(config)

    state = {
        "memory": {
            "episodic": {
                "conversation": [
                    {"role": "user", "content": "1"},
                    {"role": "assistant", "content": "2"},
                    {"role": "assistant", "content": "3"},
                    {"role": "assistant", "content": "4"},
                ]
            }
        },
        "rag": {"history": [1, 2, 3]},
        "resume": {"summary": "1234567890123"},
    }

    pruned = manager.enforce_all(state)

    assert pruned["memory"]["episodic"]["conversation"] == [
        {"role": "assistant", "content": "2"},
        {"role": "assistant", "content": "3"},
        {"role": "assistant", "content": "4"},
    ]
    assert pruned["rag"]["history"] == [2, 3]
    assert pruned["resume"]["summary"].endswith("[... SUMMARY TRIMMED ...]")
    assert len(pruned["resume"]["summary"]) <= 10 + len("\n\n[... SUMMARY TRIMMED ...]")
