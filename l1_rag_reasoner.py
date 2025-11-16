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

from l1_reasoner_base import Reasoner
from utils_types import PlanObject


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
        queries = _build_queries(state)
        filters = state.get("rag_filters") or {}
        objective = state.get("objective", "unspecified-objective")

        plan: PlanObject = PlanObject(
            {
                "layer": "l1",
                "mode": "rag",
                "objective": str(objective),
                "queries": queries,
                "filters": filters,
                "ranking": {
                    "strategy": "relevance_then_recency",
                    "limit": state.get("rag_limit", 5),
                },
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "rag",
                },
            }
        )
        plan["safety_metadata"] = {
            "objective": str(objective),
            "sensitivity": "low",
            "audience": state.get("audience", "general"),
            "tags": ["planning", "deterministic"],
        }
        return plan
