from __future__ import annotations

from typing import Any, Dict, List

from injection_profiles import DEFAULT_FRAMING_PROFILE
from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from ranking import bm25_rank, dense_rank, hybrid_rank
from retrieval import RetrievalConfig
from utils_types import BudgetConfig, PlanObject, StatePatch


# ---------------------------------------------------------------------
# Low-level RAG transforms (transformer-style utilities)
# ---------------------------------------------------------------------


def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic shallow normalization of retrieval results."""
    normed: List[Dict[str, Any]] = []
    for r in results:
        normed.append(
            {
                "query": r.get("query", ""),
                "rank": r.get("rank", 0),
                "evidence": r.get("evidence", ""),
            }
        )
    return normed


def dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministically remove duplicate (query, evidence) pairs."""
    seen = set()
    out: List[Dict[str, Any]] = []
    for r in results:
        key = (r.get("query", ""), r.get("evidence", ""))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def rerank_results(
    results: List[Dict[str, Any]],
    strategy: str = "relevance_then_recency",
) -> List[Dict[str, Any]]:
    """
    Fallback reranker when no explicit strategy is provided.
    Deterministic: sort by rank ascending.
    """
    return sorted(results, key=lambda r: r.get("rank", 0))


def fuse_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Stable grouping of results by query; output is flat but query-sorted."""
    return sorted(results, key=lambda r: r.get("query", ""))


def apply_ranker(
    results: List[Dict[str, Any]],
    strategy: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Apply the configured ranking strategy:

      - 'bm25'   → bm25_rank
      - 'dense'  → dense_rank
      - 'hybrid' → hybrid_rank
      - None     → rerank_results fallback
    """
    if strategy == "bm25":
        return bm25_rank(results)
    if strategy == "dense":
        return dense_rank(results)
    if strategy == "hybrid":
        return hybrid_rank(results)
    return rerank_results(results, strategy or "relevance_then_recency")


def truncate_by_budget(
    results: List[Dict[str, Any]],
    config: BudgetConfig,
) -> List[Dict[str, Any]]:
    """
    Trim the result list to respect BudgetConfig.max_rag_items.
    Deterministic tail-truncation to keep the "most recent" slice.
    """
    if len(results) <= config.max_rag_items:
        return results
    return results[-config.max_rag_items:]


# ---------------------------------------------------------------------
# L1 RAG planning helpers
# ---------------------------------------------------------------------


def _latest_user_message(state: Dict[str, Any]) -> str:
    """Return the most recent user message content from state['messages']."""
    messages = state.get("messages") or []
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            content = message.get("content")
            if content:
                return str(content)
    return ""


def _build_queries(state: Dict[str, Any]) -> List[str]:
    """
    Create deterministic RAG queries from state signals:

      - explicit state['rag_queries'] if provided
      - objective / task
      - latest user message
    """
    explicit_queries = state.get("rag_queries") or []
    if explicit_queries:
        return [str(q) for q in explicit_queries]

    objective = state.get("objective") or state.get("task")
    latest_message = _latest_user_message(state)
    queries: List[str] = []
    if objective:
        queries.append(f"evidence supporting: {objective}")
    if latest_message:
        queries.append(f"recent user intent: {latest_message}")

    return queries or ["general background"]


def plan_rag(state: Dict[str, Any]) -> PlanObject:
    """
    L1-style RAG planning function.

    Emits a PlanObject describing retrieval + ranking intents for L2.
    """
    queries = _build_queries(state)
    filters = state.get("rag_filters") or {}
    objective = state.get("objective", "unspecified-objective")

    rc = RetrievalConfig(
        queries=queries,
        filters=filters,
        ranking={
            "strategy": "hybrid",
            "limit": state.get("rag_limit", 5),
        },
        metadata={
            "ranker_strategy": "hybrid",
            "fusion_strategy": "query_rank_merge",
            "hybrid_ranker_enabled": True,
        },
    )
    retrieval_fragment = rc.to_plan_fragment()

    plan: PlanObject = PlanObject(
        {
            "layer": "l1",
            "mode": "rag",
            "objective": str(objective),
            "retrieval": retrieval_fragment,
            "ranking": retrieval_fragment["ranking"],
            "handoff": {
                "target_layer": "l2",
                "preferred_executor": "rag",
            },
        }
    )
    plan["retrieval_metadata"] = retrieval_fragment.get("metadata", {})
    plan["injection_framing"] = {
        "global_goal": DEFAULT_FRAMING_PROFILE.global_goal,
        "success_criteria": DEFAULT_FRAMING_PROFILE.success_criteria,
        "task_mode": DEFAULT_FRAMING_PROFILE.task_mode,
        "scope_boundaries": DEFAULT_FRAMING_PROFILE.scope_boundaries,
        "cost_latency": DEFAULT_FRAMING_PROFILE.cost_latency,
    }
    plan["injection_reasoning"] = {
        "failure_anticipation_enabled": True,
        "self_consistency_enabled": True,
        "reason_then_answer": True,
        "error_simulation_enabled": True,
    }
    plan["safety_metadata"] = {
        "objective": str(objective),
        "sensitivity": "low",
        "audience": state.get("audience", "general"),
        "tags": ["planning"],
    }
    return plan


# ---------------------------------------------------------------------
# L2 RAG execution
# ---------------------------------------------------------------------


def _synthesize_result(query: str, index: int) -> Dict[str, Any]:
    """Create a deterministic retrieval result for a query."""
    return {
        "query": query,
        "rank": index + 1,
        "evidence": f"Evidence synthesized for '{query}'",
    }


def execute_rag(plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
    """
    L2-style RAG execution function.

    Consumes a PlanObject from plan_rag(...) and returns a StatePatch
    containing RAG history and last_retrieval metadata.
    """
    retrieval = plan.get("retrieval", {})
    queries: List[str] = [str(q) for q in retrieval.get("queries", [])]
    filters = retrieval.get("filters", {})
    ranking = retrieval.get("ranking", {})
    metadata = retrieval.get("metadata", {})

    # Deterministic synthetic results; in a real system this would call
    # the actual retrievers, but for now we keep it stubbed yet structured.
    results = [_synthesize_result(query, idx) for idx, query in enumerate(queries)]

    # Transform pipeline
    transformed = normalize_documents(results)
    transformed = dedupe_results(transformed)
    transformed = apply_ranker(
        transformed,
        metadata.get("ranker_strategy") or ranking.get("strategy"),
    )
    transformed = fuse_sources(transformed)

    # Budgeting
    budget_config = BudgetConfig()
    transformed = truncate_by_budget(transformed, budget_config)

    history = list(state.get("rag_history", [])) + transformed

    patch: StatePatch = StatePatch(
        {
            "rag_history": history,
            "last_retrieval": {
                "queries": queries,
                "filters": filters,
                "ranking": ranking,
                "metadata": metadata,
                "status": "completed",
            },
        }
    )
    patch["tooling_injection"] = {
        "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
        "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
        "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
    }
    patch["retrieval_injection"] = {"hybrid_ranker_enabled": True}
    return patch
