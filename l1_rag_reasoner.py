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
from l1_reasoner_base import Reasoner
from utils_types import PlanObject
from rag_config import RetrievalConfig
from memory_views import get_evidence_view


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
