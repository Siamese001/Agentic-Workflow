# FILE: 10_10/registry.py
"""
Registry / Control Plane (v10_10 · Phase 0)
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
    • Versioning / metadata registry (lightweight)

The Registry exists to:
    1. Maintain deterministic lookup for all pluggable components.
    2. Provide a single authority for orchestration & agent identity.
    3. Facilitate dynamic discovery in later phases (multi-agent routing).
    4. Avoid ghost code and “invisible behaviors” seen in v10_10.
    5. Provide clean hooks for meta-learning (Phase 4).
"""

from __future__ import annotations

from typing import Any, Dict, Callable, Optional, List
from dataclasses import dataclass, field

from .models import (
    ExecutionProfile,
    PromptDefinition,
    RetrievalConfig,
    PolicyDecisionEvent,
    ContextBudget,
)

from .config_profiles_v10_10 import EXECUTION_PROFILES
from .prompt_system_v10_10 import PROMPT_REGISTRY, PROMPT_ACLS


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
    • checks: list of safety check identifiers
    • metadata: optional info
    """

    tier: str
    checks: List[str]
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
    Pull a hard execution profile from Phase 0 profile catalog.
    """
    return EXECUTION_PROFILES[profile_id]


def list_execution_profiles() -> List[str]:
    return list(EXECUTION_PROFILES.keys())


# ======================================================================
# PROMPT REGISTRY BRIDGE
# ======================================================================

def get_prompt(prompt_id: str) -> PromptDefinition:
    if prompt_id not in PROMPT_REGISTRY:
        raise KeyError(f"Unknown prompt id: {prompt_id}")
    return PROMPT_REGISTRY[prompt_id]


def list_prompts() -> List[str]:
    return list(PROMPT_REGISTRY.keys())


def get_prompt_acl(prompt_id: str):
    return PROMPT_ACLS.get(prompt_id)


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
# VERSION METADATA (lightweight Phase 0 hook)
# ======================================================================

VERSION_METADATA: Dict[str, Any] = {
    "registry_version": "phase0.1",
    "profiles_version": "phase0.1",
    "prompt_registry_version": "phase0.1",
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
