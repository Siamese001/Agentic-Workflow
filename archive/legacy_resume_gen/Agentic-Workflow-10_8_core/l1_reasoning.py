"""Layer 1 reasoning module consolidating reasoner implementations."""



from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List

from injection_profiles import DEFAULT_FRAMING_PROFILE
from l4_memory import get_evidence_view
from meta_profile import META_PROFILE
from retrieval import RetrievalConfig
from utils_types import PlanObject


"""
L1 — Core Reasoner Base

Defines an abstract interface for cognition-layer planners. Implementations
should supply planning logic elsewhere while keeping this layer focused on
contracts only.
"""


class Reasoner(ABC):
    """Abstract base class for L1 planners."""

    @abstractmethod
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        """Return a plan object derived from the current orchestration state."""
        raise NotImplementedError


"""
L1 — Strategy Reasoner

Responsibilities:
    • Generate multi-step strategic plans for complex objectives.
    • Coordinate decomposition of tasks for downstream execution agents.
    • Provide structured intents to L3 orchestrators without enforcing control flow.

Implements deterministic planning logic that emits only PlanObject instances.
"""


def _as_list(value: Any) -> List[str]:
    """Normalize arbitrary input into a sorted list of strings."""

    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return [str(value)]


def _objective_from_state(state: Dict[str, Any]) -> str:
    """Extract a stable objective string from the orchestration state."""

    for key in ("objective", "task", "goal"):
        candidate = state.get(key)
        if candidate:
            return str(candidate)
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
            {
                "id": "clarify",
                "action": "analyze_objective",
                "details": objective,
            },
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

        plan: PlanObject = PlanObject(
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
                    "preferred_executor": "bullet",
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


"""
L1 — Retrieval-Augmented Reasoner

Responsibilities:
    • Decide when and how to leverage retrieval for evidence-aware reasoning.
    • Formulate retrieval intents and ranking criteria for L2 RAG execution.
    • Maintain alignment with safety constraints handed off to L5 gateways.

Implements deterministic planning logic that emits only PlanObject instances.
"""


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
L1 — Drafting Reasoner

Responsibilities:
    • Plan narrative or structured drafts aligned with task objectives.
    • Translate strategy intents into drafting briefs for L2 execution agents.
    • Incorporate retrieval or bullet inputs while deferring orchestration to L3.

Implements deterministic planning logic that emits only PlanObject instances.
"""


def _collect_sections(state: Dict[str, Any]) -> List[str]:
    """Assemble deterministic section headings for the draft."""

    if state.get("outline"):
        return [str(section) for section in state["outline"]]

    bullets = state.get("bullets") or []
    if bullets:
        return [f"Section {index + 1}: {bullet}" for index, bullet in enumerate(bullets)]

    return ["Introduction", "Body", "Conclusion"]


class DraftingReasoner(Reasoner):
    """Create drafting briefs for L2 executors without side effects."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective", "unspecified-objective")
        tone = state.get("tone", "neutral")
        audience = state.get("audience", "general")
        sections = _collect_sections(state)

        plan: PlanObject = PlanObject(
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
