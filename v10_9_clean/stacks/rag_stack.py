"""
L1 — Retrieval-Augmented Reasoner

Responsibilities:
    • Decide when and how to leverage retrieval for evidence-aware reasoning.
    • Formulate retrieval intents and ranking criteria for L2 RAG execution.
    • Maintain alignment with safety constraints handed off to L5 gateways.

Implements deterministic planning logic that emits only PlanObject instances.
"""
from __future__ import annotations

from typing import Any, Dict, List

from injection_profiles import DEFAULT_FRAMING_PROFILE
from l1_reasoning import Reasoner
from utils_types import PlanObject
from retrieval import RetrievalConfig
from l4_memory import get_evidence_view


def _latest_user_message(state: Dict[str, Any]) -> str:
    """Return the most recent user message content from state messages."""

    messages = state.get("messages") or []
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            content = message.get("content")
            if content:
                return str(content)
    return ""


def _build_queries(state: Dict[str, Any]) -> List[str]:
    """Create deterministic RAG queries from state signals."""

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


class RAGReasoner(Reasoner):
    """Plan deterministic retrieval intents for downstream execution."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        evidence_view = get_evidence_view(state)
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
"""
L2 — RAG Execution Agent

Responsibilities:
    • Execute retrieval, ranking, and evidence extraction operations.
    • Apply RAG intents from L1 reasoning while respecting L5 safety constraints.
    • Emit structured artifacts consumable by L4 state managers.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""
from __future__ import annotations

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from l2_execution import ExecutionAgent
from retrieval import fuse_results
from retrieval import (
    normalize_documents,
    dedupe_results,
    rerank_results,
    fuse_sources,
    truncate_by_budget,
    apply_ranker,
)
from l4_memory import ContextBudget
from utils_types import BudgetConfig, PlanObject, StatePatch


def _synthesize_result(query: str, index: int) -> Dict[str, Any]:
    """Create a deterministic retrieval result for a query."""

    return {
        "query": query,
        "rank": index + 1,
        "evidence": f"Evidence synthesized for '{query}'",
    }


class RAGExecutionAgent(ExecutionAgent):
    """Deterministic retrieval executor that returns state patches only."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        retrieval = plan.get("retrieval", {})
        queries: List[str] = [str(q) for q in retrieval.get("queries", [])]
        filters = retrieval.get("filters", {})
        ranking = retrieval.get("ranking", {})
        metadata = retrieval.get("metadata", {})
        results = [_synthesize_result(query, idx) for idx, query in enumerate(queries)]

        transformed = normalize_documents(results)
        transformed = dedupe_results(transformed)
        transformed = rerank_results(transformed, ranking.get("strategy"))
        transformed = apply_ranker(transformed, metadata.get("ranker_strategy") or ranking.get("strategy"))
        transformed = fuse_results([fuse_sources(transformed)])
        budget_config = BudgetConfig()
        context_budget = ContextBudget(budget_config)

        transformed = truncate_by_budget(transformed, budget_config)
        transformed = context_budget.prune_rag_items_by_tokens(transformed)

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
"""L1 RAG planning stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from bullet_planning import extract_job_profile, extract_resume_profile


def describe_experience(resume_profile: Dict[str, Any]) -> List[str]:
    experiences = []
    for item in resume_profile.get("experience", []) if isinstance(resume_profile, dict) else []:
        if isinstance(item, dict):
            title = item.get("title") or item.get("role") or "Experience"
            desc = item.get("description") or ""
            experiences.append(f"{title}: {desc}")
    return experiences


class RAGPlan(BaseModel):
    goal: str = "Retrieve evidence to strengthen bullets."
    context_inputs: List[str] = []
    retrieval_queries: List[str] = []
    prioritization: str = "hybrid"
    risk_checks: List[str] = []


class RAGPlanningStack:
    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        experiences = describe_experience(resume_profile)

        queries = []
        if isinstance(job_profile, dict):
            queries.extend([str(v) for v in job_profile.values() if isinstance(v, str)])
        queries.extend(experiences)
        queries = [q for q in queries if q]

        plan = RAGPlan(
            context_inputs=experiences,
            retrieval_queries=queries[:5],
            risk_checks=["ensure relevance", "avoid hallucination"],
        )

        return {"rag": {"plan": plan.model_dump()}}
"""L2 RAG execution stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from rag_planning import RAGPlan


class RAGExecutionStack:
    """Hybrid retrieval stub that returns deterministic patches."""

    def _load_plan(self, state: Dict[str, Any]) -> RAGPlan:
        plan_data = state.get("rag", {}).get("plan") or {}
        if isinstance(plan_data, RAGPlan):
            return plan_data
        if isinstance(plan_data, dict):
            return RAGPlan(**plan_data)
        return RAGPlan()

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._load_plan(state)
        queries = plan.retrieval_queries or ["experience impact"]

        candidates: List[Dict[str, Any]] = []
        for idx, query in enumerate(queries):
            candidates.append({"query": query, "source": "chroma", "score": 1.0 - idx * 0.05})
            candidates.append({"query": query, "source": "bm25", "score": 0.9 - idx * 0.05})

        ranked = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
        top_k = ranked[:5]

        metadata = {
            "goal": plan.goal,
            "context_inputs": plan.context_inputs,
            "risk_checks": plan.risk_checks,
            "candidate_count": len(candidates),
            "top_candidate": top_k[0] if top_k else None,
        }

        return {
            "resume": {"experience_bullets": top_k},
            "rag": {"plan": plan.model_dump(), "metadata": metadata},
        }
from typing import Any, Dict, List

from ranking import bm25_rank, dense_rank, hybrid_rank
from utils_types import BudgetConfig


def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Deterministic shallow normalization
    normed = []
    for r in results:
        normed.append({
            "query": r.get("query", ""),
            "rank": r.get("rank", 0),
            "evidence": r.get("evidence", ""),
        })
    return normed


def dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for r in results:
        key = (r.get("query", ""), r.get("evidence", ""))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def rerank_results(results: List[Dict[str, Any]], strategy: str = "relevance_then_recency") -> List[Dict[str, Any]]:
    # Deterministic: sort by rank ascending
    return sorted(results, key=lambda r: r.get("rank", 0))


def fuse_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Deterministic grouping by query
    # (Flat output, but stable order)
    return sorted(results, key=lambda r: r.get("query", ""))


def truncate_by_budget(results: List[Dict[str, Any]], config: BudgetConfig) -> List[Dict[str, Any]]:
    # Trim to max_rag_items
    if len(results) <= config.max_rag_items:
        return results
    return results[-config.max_rag_items:]


def apply_ranker(results: List[Dict[str, Any]], strategy: str | None = None) -> List[Dict[str, Any]]:
    if strategy == "bm25":
        return bm25_rank(results)
    if strategy == "dense":
        return dense_rank(results)
    if strategy == "hybrid":
        return hybrid_rank(results)
    return rerank_results(results, strategy or "relevance_then_recency")
