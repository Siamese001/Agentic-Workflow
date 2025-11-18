# FILE: v10_9_clean/l1_core.py
"""
L1 Cognition Core (v10_9)

Contains all L1 reasoner classes:
    • StrategyReasoner
    • RAGReasoner
    • DraftingReasoner

Pure cognition: no execution, no orchestration, no state mutation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List

from config import DEFAULT_FRAMING_PROFILE
from meta_profile import META_PROFILE
from models import PlanObject
from l1_planners import extract_job_profile, extract_resume_profile  # shared planning utils


# ---------------------------------------------------------------------------
# Base Reasoner
# ---------------------------------------------------------------------------

class Reasoner(ABC):
    """Abstract base class for L1 planners."""

    @abstractmethod
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Strategy Reasoner
# ---------------------------------------------------------------------------

def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(v) for v in value]
    return [str(value)]


def _objective_from_state(state: Dict[str, Any]) -> str:
    for key in ("objective", "task", "goal"):
        v = state.get(key)
        if v:
            return str(v)
    return "unspecified-objective"


class StrategyReasoner(Reasoner):
    """Deterministic multi-step strategy planner for L1."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = _objective_from_state(state)
        constraints = sorted(_as_list(state.get("constraints")))
        dependencies = sorted(_as_list(state.get("dependencies")))
        deliverables = sorted(_as_list(state.get("deliverables"))) or [
            "summary",
            "next-actions",
        ]

        if META_PROFILE.planning_bias.get("conservative"):
            deliverables = deliverables[:2]

        steps = [
            {"id": "clarify", "action": "analyze_objective", "details": objective},
            {
                "id": "context",
                "action": "assess_context",
                "summary": state.get("summary", ""),
                "dependencies": dependencies,
            },
            {
                "id": "structure",
                "action": "outline_deliverables",
                "deliverables": deliverables,
                "constraints": constraints,
            },
        ]

        if META_PROFILE.planning_bias.get("conservative"):
            steps = steps[:2]

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "strategy",
                "objective": objective,
                "constraints": constraints,
                "dependencies": dependencies,
                "deliverables": deliverables,
                "steps": steps,
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "strategy",
                    "expected_outputs": deliverables,
                },
            }
        )

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
            "objective": objective,
            "sensitivity": "low",
            "audience": state.get("audience", "general"),
            "tags": ["planning"],
        }

        return plan


# ---------------------------------------------------------------------------
# RAG Reasoner
# ---------------------------------------------------------------------------

def _latest_user_message(state: Dict[str, Any]) -> str:
    msgs = state.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, dict) and m.get("role") == "user":
            c = m.get("content")
            if c:
                return str(c)
    return ""


def _build_rag_queries(state: Dict[str, Any]) -> List[str]:
    explicit = state.get("rag_queries")
    if explicit:
        return [str(q) for q in explicit]

    objective = state.get("objective") or "unspecified-objective"
    latest = _latest_user_message(state)

    job_profile = extract_job_profile(state)
    resume_profile = extract_resume_profile(state)

    queries: List[str] = []

    if objective:
        queries.append(f"evidence supporting: {objective}")
    if latest:
        queries.append(f"user intent: {latest}")
    if job_profile.get("title"):
        queries.append(f"industry context: {job_profile['title']}")
    if resume_profile.get("summary"):
        q = resume_profile["summary"]
        queries.append(f"match resume summary: {q[:120]}")

    return queries or ["general background"]


class RAGReasoner(Reasoner):
    """Plan deterministic retrieval intents for downstream execution."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        queries = _build_rag_queries(state)
        filters = state.get("rag_filters") or {}
        objective = str(state.get("objective", "unspecified-objective"))

        ranking_cfg = {
            "strategy": "hybrid",
            "limit": state.get("rag_limit", 5),
        }

        retrieval_fragment = {
            "queries": queries,
            "filters": filters,
            "ranking": ranking_cfg,
            "metadata": {
                "ranker_strategy": "hybrid",
                "fusion_strategy": "query_rank_merge",
                "hybrid_ranker_enabled": True,
            },
        }

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "rag",
                "objective": objective,
                "retrieval": retrieval_fragment,
                "ranking": ranking_cfg,
                "handoff": {"target_layer": "l2", "preferred_executor": "rag"},
            }
        )

        plan["retrieval_metadata"] = retrieval_fragment["metadata"]
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
            "objective": objective,
            "sensitivity": "low",
            "audience": state.get("audience", "general"),
            "tags": ["planning"],
        }

        return plan


# ---------------------------------------------------------------------------
# Drafting Reasoner
# ---------------------------------------------------------------------------

class DraftingReasoner(Reasoner):
    """Create drafting briefs for L2 executors without side effects."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective", "unspecified-objective")
        tone = state.get("tone", "neutral")
        audience = state.get("audience", "general")

        # Sections determined by planners, imported from l1_planners later
        from l1_planners import collect_sections

        sections = collect_sections(state)

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "drafting",
                "objective": str(objective),
                "tone": tone,
                "audience": audience,
                "sections": sections,
                "constraints": state.get("constraints", []),
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "drafting",
                    "format": "narrative",
                },
            }
        )

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
            "audience": audience,
            "tags": ["planning"],
        }

        return plan
