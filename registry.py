# FILE: 10_10/registry.py
"""
Registry / Control Plane (v10_10 · Phase 2)
==========================================

This module provides the **central control plane** for the v10_10 refactor.
It fixes G22, G29–G33, G37 by defining:

    • Agent registry
    • Tool registry
    • Model routing registry
    • Safety bundle registry
    • Profile registry (bridge to config_profiles_v10_10)
    • Prompt registry linkage
    • Skill/domain classifier registry
    • RAG strategy registry (Phase 0 scaffolding)

Phase 2 extensions (Prompt / Context / ACL governance):
    • Prompt registry bridge delegates to prompt_system_v10_10.get_prompt
      so ACLs are enforced consistently.
    • Model-tier + execution-profile routing helper for prompts.
    • Prompt version helpers for validation and diff tooling.
"""

from __future__ import annotations

from typing import Any, Dict, Callable, Optional, List, Iterable
from dataclasses import dataclass, field

from models import (
    ExecutionProfile,
    PromptDefinition,
    PromptVersion,
    RetrievalConfig,
    PolicyDecisionEvent,
    ContextBudget,
)
from config_profiles_v10_10 import EXECUTION_PROFILES, ExecutionProfileSpec, ModelTier
from prompt_system_v10_10 import (
    PROMPT_REGISTRY,
    PROMPT_ACLS,
    PromptACL,
    PromptActorRole,
    get_prompt as _prompt_system_get_prompt,
)


# ======================================================================
# AGENT REGISTRY
# ======================================================================


@dataclass
class AgentCard:
    """
    Unique agent identity card.

    Fields:
        • id: unique agent string
        • role: descriptive role (planner, drafter, qa, safety, rag, router)
        • capabilities: set of capabilities for least-privilege micro-agents
        • version: optional version of the agent implementation
        • metadata: free-form metadata
    """

    id: str
    role: str
    capabilities: List[str]
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


AGENT_REGISTRY: Dict[str, AgentCard] = {}


def register_agent(agent_card: AgentCard) -> None:
    AGENT_REGISTRY[agent_card.id] = agent_card


def get_agent(agent_id: str) -> AgentCard:
    if agent_id not in AGENT_REGISTRY:
        raise KeyError(f"Unknown agent id: {agent_id}")
    return AGENT_REGISTRY[agent_id]


def list_agents() -> List[AgentCard]:
    return list(AGENT_REGISTRY.values())


# ======================================================================
# TOOL REGISTRY
# ======================================================================


@dataclass
class ToolCard:
    """
    Metadata descriptor for tools (RAG retrievers, model clients, formatters).

    Fields:
        • id
        • description
        • config
        • metadata
    """

    id: str
    description: str
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


TOOL_REGISTRY: Dict[str, ToolCard] = {}


def register_tool(tool: ToolCard) -> None:
    TOOL_REGISTRY[tool.id] = tool


def get_tool(tool_id: str) -> ToolCard:
    if tool_id not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool id: {tool_id}")
    return TOOL_REGISTRY[tool_id]


def list_tools() -> List[ToolCard]:
    return list(TOOL_REGISTRY.values())


# ======================================================================
# MODEL ROUTING REGISTRY (STATIC FOR NOW; DYNAMIC IN PHASE 3)
# ======================================================================


@dataclass
class ModelRoute:
    """
    Defines a model route (model name, endpoint, usage metadata).
    """

    id: str
    model_name: str
    endpoint: str
    metadata: Dict[str, Any] = field(default_factory=dict)


MODEL_ROUTES: Dict[str, ModelRoute] = {}


def register_model_route(route: ModelRoute) -> None:
    MODEL_ROUTES[route.id] = route


def get_model_route(route_id: str) -> ModelRoute:
    if route_id not in MODEL_ROUTES:
        raise KeyError(f"Unknown model route id: {route_id}")
    return MODEL_ROUTES[route_id]


def list_model_routes() -> List[ModelRoute]:
    return list(MODEL_ROUTES.values())


# ======================================================================
# SAFETY BUNDLE REGISTRY
# ======================================================================


@dataclass
class SafetyBundle:
    """
    Safety bundle representing a collection of safety checks / policies.

    • tier: "strict", "standard", "relaxed", "debug"
    """

    tier: str
    description: str
    context_budget: ContextBudget
    policy_events: List[PolicyDecisionEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


SAFETY_BUNDLES: Dict[str, SafetyBundle] = {}


def register_safety_bundle(bundle: SafetyBundle) -> None:
    SAFETY_BUNDLES[bundle.tier] = bundle


def get_safety_bundle(tier: str) -> SafetyBundle:
    if tier not in SAFETY_BUNDLES:
        raise KeyError(f"Unknown safety tier: {tier}")
    return SAFETY_BUNDLES[tier]


# ======================================================================
# EXECUTION PROFILES REGISTRY (BRIDGE TO config_profiles_v10_10)
# ======================================================================


def get_execution_profile(profile_id: str) -> ExecutionProfile:
    """
    Pull a hard execution profile from Phase 2 profile catalog.

    NOTE: the underlying object is an ExecutionProfileSpec; this
    function preserves the original ExecutionProfile type hint for
    backward compatibility.
    """
    return EXECUTION_PROFILES[profile_id]  # type: ignore[return-value]


def list_execution_profiles() -> List[str]:
    return list(EXECUTION_PROFILES.keys())


# ======================================================================
# PROMPT REGISTRY BRIDGE & GOVERNANCE (PHASE 2)
# ======================================================================


def get_prompt(
    prompt_id: str,
    actor_role: PromptActorRole = PromptActorRole.ENGINE,
) -> PromptDefinition:
    """
    Retrieve a prompt by ID using the central prompt system.

    This delegates to ``prompt_system_v10_10.get_prompt`` so that:
        • ACLs are enforced for the given actor role.
        • All reads go through a single governance surface.
    """
    return _prompt_system_get_prompt(prompt_id, actor_role=actor_role)


def list_prompts() -> List[str]:
    """Return all registered prompt IDs."""
    return list(PROMPT_REGISTRY.keys())


def get_prompt_acl(prompt_id: str) -> Optional[PromptACL]:
    """Return the PromptACL object for a given prompt, if any."""
    return PROMPT_ACLS.get(prompt_id)


def get_prompt_model_tier(prompt_id: str, profile_id: Optional[str] = None) -> str:
    """
    Resolve the effective model tier for a prompt under an execution profile.

    Resolution order:
        1. If ``profile_id`` is provided and known, use its ``model_tier``.
        2. Otherwise, use the prompt metadata field ``default_model_tier``
           if present, falling back to ``"balanced"``.
        3. If the prompt defines ACL metadata restricting ``model_tiers``,
           clamp the result to the first allowed tier.

    This is advisory; the actual model selection is performed by the
    RoutingPolicy in routing.py.
    """

    # 1) Profile-driven tier.
    tier: Optional[str] = None
    if profile_id is not None and profile_id in EXECUTION_PROFILES:
        spec: ExecutionProfileSpec = EXECUTION_PROFILES[profile_id]
        # ModelTier enums carry the string tier in their ``value`` field.
        mt = getattr(spec.model_tier, "value", str(spec.model_tier))
        tier = str(mt)

    # 2) Prompt metadata fallback.
    prompt_def: Optional[PromptDefinition] = PROMPT_REGISTRY.get(prompt_id)
    meta: Dict[str, Any] = (
        prompt_def.metadata if prompt_def and prompt_def.metadata else {}
    )
    if tier is None:
        tier = str(meta.get("default_model_tier", "balanced"))

    # 3) ACL metadata clamping (allowed model_tiers).
    acl_meta: Dict[str, Any] = (meta.get("acl") or {})
    allowed_tiers = acl_meta.get("model_tiers") or []
    if allowed_tiers and tier not in allowed_tiers:
        # Clamp to first allowed tier; enforcement of this decision happens
        # downstream in routing / model selection.
        tier = str(allowed_tiers[0])

    return tier


def resolve_prompt_for_profile(
    prompt_id: str,
    profile_id: str,
    actor_role: PromptActorRole = PromptActorRole.ENGINE,
) -> PromptDefinition:
    """
    Convenience helper that:
        • verifies the prompt is accessible for the given actor role, and
        • resolves model-tier compatibility with the execution profile.

    It returns the PromptDefinition; callers can separately query the
    model tier via :func:`get_prompt_model_tier` if needed.
    """

    # Ensure ACL-based access is valid.
    prompt_def = get_prompt(prompt_id, actor_role=actor_role)
    # Resolve tier (clamped against ACL metadata if necessary). The return
    # value is intentionally unused here; the call acts as a validation hook.
    _ = get_prompt_model_tier(prompt_id, profile_id)
    return prompt_def


def get_prompt_version(prompt_id: str) -> PromptVersion:
    """Return the semantic PromptVersion for a prompt ID."""
    if prompt_id not in PROMPT_REGISTRY:
        raise KeyError(f"Unknown prompt id: {prompt_id}")
    return PROMPT_REGISTRY[prompt_id].version


def ensure_prompt_version(prompt_id: str, expected: PromptVersion) -> bool:
    """
    Check whether the concrete prompt definition matches an expected version.

    This is a thin helper used by tests and higher-level validation layers
    to detect version drift without changing runtime behavior.
    """
    actual = get_prompt_version(prompt_id)
    return actual.as_str() == expected.as_str()


# ======================================================================
# RETRIEVAL / RAG STRATEGY REGISTRY (Phase 0 placeholder)
# ======================================================================


@dataclass
class RAGStrategyCard:
    """
    Defines a retrieval strategy (bm25, dense, hybrid, hyde, weighted).
    """

    id: str
    description: str
    retrieval_config: RetrievalConfig
    metadata: Dict[str, Any] = field(default_factory=dict)


RAG_STRATEGIES: Dict[str, RAGStrategyCard] = {}


def register_rag_strategy(card: RAGStrategyCard) -> None:
    RAG_STRATEGIES[card.id] = card


def get_rag_strategy(strategy_id: str) -> RAGStrategyCard:
    if strategy_id not in RAG_STRATEGIES:
        raise KeyError(f"Unknown RAG strategy id: {strategy_id}")
    return RAG_STRATEGIES[strategy_id]


def list_rag_strategies() -> List[str]:
    return list(RAG_STRATEGIES.keys())


# ======================================================================
# SKILL / DOMAIN CLASSIFIER REGISTRY (placeholder for G32–G33)
# ======================================================================


@dataclass
class ClassificationModelCard:
    """
    Lightweight descriptor for skill/domain classifiers.
    """

    id: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    classifier_fn: Optional[Callable[[str], Dict[str, Any]]] = None


CLASSIFIER_REGISTRY: Dict[str, ClassificationModelCard] = {}


def register_classifier(card: ClassificationModelCard) -> None:
    CLASSIFIER_REGISTRY[card.id] = card


def get_classifier(card_id: str) -> ClassificationModelCard:
    if card_id not in CLASSIFIER_REGISTRY:
        raise KeyError(f"Unknown classifier id: {card_id}")
    return CLASSIFIER_REGISTRY[card_id]


def list_classifiers() -> List[str]:
    return list(CLASSIFIER_REGISTRY.keys())


# ======================================================================
# VERSION METADATA (lightweight Phase 2 hook)
# ======================================================================

VERSION_METADATA: Dict[str, Any] = {
    "registry_version": "phase2.0",
    "profiles_version": "phase0.1",
    "prompt_registry_version": "phase2.0",
}


# ======================================================================
# RESET (useful for unit tests)
# ======================================================================


def reset_registry() -> None:
    AGENT_REGISTRY.clear()
    TOOL_REGISTRY.clear()
    MODEL_ROUTES.clear()
    SAFETY_BUNDLES.clear()
    CLASSIFIER_REGISTRY.clear()
    RAG_STRATEGIES.clear()
