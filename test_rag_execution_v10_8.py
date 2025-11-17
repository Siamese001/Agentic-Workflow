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
from rag_transformers import (
    fuse_sources,
    normalize_documents,
    dedupe_results,
    rerank_results,
    truncate_by_budget,
)
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
    assert patch["rag_history"][0]["query"] == "query-13"
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


def test_rerank_results_sorts_by_rank():
    unordered = [
        {"query": "q2", "rank": 3, "evidence": "e2"},
        {"query": "q1", "rank": 1, "evidence": "e1"},
        {"query": "q3", "rank": 2, "evidence": "e3"},
    ]

    reranked = rerank_results(unordered, "relevance_then_recency")

    assert [entry["rank"] for entry in reranked] == [1, 2, 3]
    assert [entry["query"] for entry in reranked] == ["q1", "q3", "q2"]


def test_fuse_sources_sorts_by_query():
    unordered = [
        {"query": "b", "rank": 2, "evidence": "e2"},
        {"query": "a", "rank": 1, "evidence": "e1"},
        {"query": "c", "rank": 3, "evidence": "e3"},
    ]

    fused = fuse_sources(unordered)

    assert [entry["query"] for entry in fused] == ["a", "b", "c"]
    assert [entry["rank"] for entry in fused] == [1, 2, 3]


def test_full_pipeline_is_deterministic_with_rerank_and_fuse():
    results = [
        {"query": "query-b", "rank": 2, "evidence": "ev-b"},
        {"query": "query-a", "rank": 3, "evidence": "ev-a"},
        {"query": "query-a", "rank": 1, "evidence": "ev-a"},
        {"query": "query-c", "rank": 1, "evidence": "ev-c"},
    ]

    transformed = normalize_documents(results)
    transformed = dedupe_results(transformed)
    transformed = rerank_results(transformed, "relevance_then_recency")
    transformed = fuse_sources(transformed)
    transformed = truncate_by_budget(transformed, BudgetConfig())

    assert [entry["query"] for entry in transformed] == ["query-a", "query-b", "query-c"]
    assert [entry["rank"] for entry in transformed] == [3, 2, 1]


def test_rag_execution_applies_token_and_count_budgets(monkeypatch):
    def _limited_budget():
        return BudgetConfig(max_rag_items=3, max_retrieval_tokens=5)

    monkeypatch.setattr("l2_rag_execution.BudgetConfig", _limited_budget)

    queries = [f"q-{idx}" for idx in range(5)]
    plan = {
        "retrieval": {
            "queries": queries,
            "filters": {},
            "ranking": {"strategy": "relevance"},
        }
    }

    patch = RAGExecutionAgent().execute(plan, {})

    assert len(patch["rag_history"]) == 1
    assert patch["rag_history"][0]["query"] == "q-4"
    assert patch["last_retrieval"]["queries"] == queries
