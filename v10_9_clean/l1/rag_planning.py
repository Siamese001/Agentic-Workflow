# FILE: v10_9_clean/l1/rag_planning.py
"""
L1 — RAG Planning (v10_9)

Pure planning layer for retrieval-augmented generation.
Creates deterministic retrieval plan fragments for L2 executors.
No execution, no state mutation, no external calls.
"""

from __future__ import annotations
from typing import Any, Dict, List

from shared.models import PlanObject
from .planning_utils import extract_job_profile, extract_resume_profile


def _latest_user_message(state: Dict[str, Any]) -> str:
    msgs = state.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, dict) and m.get("role") == "user":
            c = m.get("content")
            if c:
                return str(c)
    return ""


def _build_queries(state: Dict[str, Any]) -> List[str]:
    explicit = state.get("rag_queries")
    if explicit:
        return [str(q) for q in explicit]

    objective = (
        state.get("objective")
        or state.get("task")
        or "unspecified-objective"
    )
    latest = _latest_user_message(state)

    job_profile = extract_job_profile(state)
    resume_profile = extract_resume_profile(state)

    queries: List[str] = []

    if objective:
        queries.append(f"evidence supporting: {objective}")

    if latest:
        queries.append(f"user intent: {latest}")

    if job_profile.get("title"):
        queries.append(f"industry context: {job_profile['title']} at {job_profile.get('company','')}")

    if resume_profile.get("summary"):
        summary = resume_profile["summary"]
        if summary:
            queries.append(f"match resume summary: {summary[:120]}")

    return [q for q in queries if q] or ["general background"]


def _extract_filters(state: Dict[str, Any]) -> Dict[str, Any]:
    f = state.get("rag_filters")
    return f if isinstance(f, dict) else {}


def _ranking_config(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "strategy": state.get("rag_ranking_strategy", "hybrid"),
        "limit": state.get("rag_limit", 5),
    }


def build_rag_plan(state: Dict[str, Any]) -> PlanObject:
    objective = (
        state.get("objective")
        or state.get("task")
        or "unspecified-objective"
    )

    queries = _build_queries(state)
    filters = _extract_filters(state)
    ranking = _ranking_config(state)

    steps = [
        {
            "id": "retrieve",
            "action": "execute_rag",
            "queries": queries,
            "filters": filters,
            "ranking": ranking,
        }
    ]

    return PlanObject(
        plan_id="l1-rag-plan",
        description=f"RAG plan for: {objective}",
        steps=steps,
        layer="l1",
        mode="rag",
        objective=str(objective),
        retrieval={
            "queries": queries,
            "filters": filters,
            "ranking": ranking,
        },
        ranking=ranking,
        handoff={
            "target_layer": "l2",
            "preferred_executor": "rag",
        },
        injection_framing=state.get("injection_framing", {}),
        injection_reasoning=state.get("injection_reasoning", {}),
        safety_metadata={
            "objective": str(objective),
            "sensitivity": "low",
            "audience": state.get("audience", "general"),
            "tags": ["planning", "rag"],
        },
    )


def plan(state: Dict[str, Any]) -> PlanObject:
    return build_rag_plan(state)
