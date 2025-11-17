"""
Test Suite — RAG Execution v10.8

Responsibilities:
    • Validate retrieval-augmented execution agents in the v10.8 architecture.
    • Ensure interactions between L1 RAG planners, L2 RAG executors, and L3 orchestrators are covered.
    • Confirm compliance with L4 state handling and L5 safety hooks once implemented.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l1_rag_reasoner import RAGReasoner
from l2_rag_execution import RAGExecutionAgent
from rag_transformers import normalize_documents, truncate_by_budget
from utils_types import BudgetConfig


def test_rag_execution_pipeline_round_trip():
    state = {
        "objective": "explain determinism",
        "messages": [{"role": "user", "content": "How does this work?"}],
    }

    plan = RAGReasoner().plan(state)
    assert plan["mode"] == "rag"
    assert "retrieval" in plan
    retrieval = plan["retrieval"]
    assert retrieval["queries"]

    patch = RAGExecutionAgent().execute(plan, state)
    assert patch["last_retrieval"]["status"] == "completed"
    assert patch["last_retrieval"]["queries"] == retrieval["queries"]
    assert patch["last_retrieval"]["filters"] == retrieval["filters"]
    assert len(patch["rag_history"]) == len(retrieval["queries"])


def test_rag_execution_truncates_by_budget():
    queries = [f"query-{idx}" for idx in range(BudgetConfig().max_rag_items + 5)]
    plan = {
        "retrieval": {
            "queries": queries,
            "filters": {"domain": "example"},
            "ranking": {"strategy": "relevance", "limit": len(queries)},
        }
    }

    patch = RAGExecutionAgent().execute(plan, {})

    assert len(patch["rag_history"]) == BudgetConfig().max_rag_items
    assert patch["rag_history"][0]["query"] == queries[5]
    assert patch["last_retrieval"]["queries"] == queries
    assert patch["last_retrieval"]["filters"] == {"domain": "example"}
    assert patch["last_retrieval"]["ranking"] == {"strategy": "relevance", "limit": len(queries)}


def test_rag_execution_deduplicates_results():
    plan = {
        "retrieval": {
            "queries": ["dup", "dup", "unique"],
            "filters": {},
            "ranking": {"strategy": "relevance"},
        }
    }

    patch = RAGExecutionAgent().execute(plan, {})

    assert [entry["query"] for entry in patch["rag_history"]] == ["dup", "unique"]
    assert [entry["rank"] for entry in patch["rag_history"]] == [1, 3]


def test_normalization_produces_expected_keys():
    raw_results = [{"query": "q1"}, {"evidence": "ev2"}, {"rank": 3}]
    normalized = normalize_documents(raw_results)

    assert normalized == [
        {"query": "q1", "rank": 0, "evidence": ""},
        {"query": "", "rank": 0, "evidence": "ev2"},
        {"query": "", "rank": 3, "evidence": ""},
    ]


def test_truncate_by_budget_is_deterministic():
    results = [{"query": f"q-{i}"} for i in range(30)]
    truncated = truncate_by_budget(normalize_documents(results), BudgetConfig())

    assert len(truncated) == BudgetConfig().max_rag_items
    assert truncated[0]["query"] == "q-10"
