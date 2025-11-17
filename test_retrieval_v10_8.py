"""
Test Suite — Retrieval v10.8

Validates deterministic hybrid ranking, fusion, and retrieval metadata.
"""

from l1_rag_reasoner import RAGReasoner
from l2_rag_execution import RAGExecutionAgent
from evidence_fusion import fuse_results
from rankers import bm25_rank, dense_rank, hybrid_rank


def test_rankers_are_deterministic_and_scored():
    items = [
        {"query": "alpha", "evidence": "short"},
        {"query": "beta", "evidence": "long evidence blob"},
    ]

    bm25_first = bm25_rank(items)
    bm25_second = bm25_rank(items)
    assert bm25_first == bm25_second
    assert bm25_first[0]["bm25_score"] >= bm25_first[1]["bm25_score"]

    dense_first = dense_rank(items)
    dense_second = dense_rank(items)
    assert dense_first == dense_second
    assert dense_first[0]["dense_score"] >= dense_first[1]["dense_score"]

    hybrid_first = hybrid_rank(items)
    hybrid_second = hybrid_rank(items)
    assert hybrid_first == hybrid_second
    assert hybrid_first[0]["hybrid_score"] >= hybrid_first[1]["hybrid_score"]


def test_evidence_fusion_orders_by_query_then_rank():
    fused = fuse_results(
        [
            [{"query": "b", "rank": 2}, {"query": "a", "rank": 1}],
            [{"query": "a", "rank": 3}],
        ]
    )

    assert [entry["query"] for entry in fused] == ["a", "a", "b"]
    assert [entry["rank"] for entry in fused] == [1, 3, 2]


def test_retrieval_injection_metadata_is_present():
    plan = RAGReasoner().plan({"objective": "hybrid metadata"})
    patch = RAGExecutionAgent().execute(plan, {})

    assert patch["retrieval_injection"] == {"hybrid_ranker_enabled": True}
    assert patch["last_retrieval"]["metadata"].get("ranker_strategy") == "hybrid"


def test_rag_history_growth_is_deterministic():
    plan = {
        "retrieval": {
            "queries": ["q1", "q2"],
            "filters": {},
            "ranking": {"strategy": "bm25"},
            "metadata": {"ranker_strategy": "bm25"},
        }
    }

    initial_state = {"rag_history": [{"query": "seed", "rank": 0, "evidence": "seed"}]}
    agent = RAGExecutionAgent()

    first_patch = agent.execute(plan, initial_state)
    assert [entry["query"] for entry in first_patch["rag_history"][:1]] == ["seed"]

    second_patch = agent.execute(plan, {"rag_history": first_patch["rag_history"]})

    assert len(first_patch["rag_history"]) + 2 == len(second_patch["rag_history"])
    assert second_patch["rag_history"][: len(first_patch["rag_history"])] == first_patch["rag_history"]

