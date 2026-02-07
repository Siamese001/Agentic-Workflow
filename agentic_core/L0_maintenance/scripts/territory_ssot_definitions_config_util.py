#!/usr/bin/env python3
"""
SSOT: Territory Name Definitions
=================================

Single Source of Truth for all territory names used in agent discovery and dashboard.

CRITICAL: All territory names MUST be defined here and used consistently across:
- full_agent_discovery.py (agent categorization)
- regenerate_dashboard_data.py (dashboard generation)
- All test files (validation)

DO NOT hardcode territory names anywhere else.
"""

# ============================================================================
# CANONICAL TERRITORY NAMES
# ============================================================================

# Base/Root Territory
TERRITORY_SOVEREIGN_BASE = "Sovereign Base Agent"

# Layer Base Agent Territories
TERRITORY_L0_BASE = "L0 Maintenance/Base Agent"
TERRITORY_L1_BASE = "L1 Cognition/Base Agent"
TERRITORY_L2_BASE = "L2 Execution/Base Agent"
TERRITORY_L3_BASE = "L3 Orchestration/Base Agent"
TERRITORY_L4_BASE = "L4 State/Base Agent"
TERRITORY_L5_BASE = "L5 Safety/Base Agent"
TERRITORY_L6_BASE = "L6_Observability/Base Agent"

# L0 Maintenance Territories
TERRITORY_L0_CORE = "L0 Maintenance/Core"
TERRITORY_L0_INFRASTRUCTURE = "L0 Maintenance/Infrastructure"

# L1 Cognition Territories
TERRITORY_L1_CORE = "L1 Cognition/Core"
TERRITORY_L1_REASONING = "L1 Cognition/Reasoning"
TERRITORY_L1_VALIDATION = "L1 Cognition/Validation"  # Validators in L1
TERRITORY_L1_MEMORY = "L1 Cognition/Memory"
TERRITORY_L1_PLANNING = "L1 Cognition/Planning"
TERRITORY_L1_SPECIALIZED = "L1 Cognition/Specialized"

# L2 Execution Territories
TERRITORY_L2_CORE = "L2 Execution/Core"
TERRITORY_L2_RUNNERS = "L2 Execution/Runners"
TERRITORY_L2_HANDLERS = "L2 Execution/Handlers"
TERRITORY_L2_COORDINATORS = "L2 Execution/Coordinators"
TERRITORY_L2_SPECIALIZED = "L2 Execution/Specialized"

# L3 Orchestration Territories
TERRITORY_L3_CORE = "L3 Orchestration/Core"
TERRITORY_L3_DAG = "L3 Orchestration/DAG"
TERRITORY_L3_WORKFLOW = "L3 Orchestration/Workflow"
TERRITORY_L3_TERRITORY = "L3 Orchestration/Territory"  # Territory and semantic mapping
TERRITORY_L3_RL = "L3 Orchestration/RL"  # Reinforcement Learning orchestrators
TERRITORY_L3_ROUTING = "L3 Orchestration/Routing"
TERRITORY_L3_MONITORING = "L3 Orchestration/Monitoring"
TERRITORY_L3_INFRASTRUCTURE = "L3 Orchestration/Infrastructure"
TERRITORY_L3_SPECIALIZED = "L3 Orchestration/Specialized"

# L4 State Territories
TERRITORY_L4_CORE = "L4 State/Core"
TERRITORY_L4_INFRASTRUCTURE = "L4 State/Infrastructure"
TERRITORY_L4_SPECIALIZED = "L4 State/Specialized"

# L5 Safety Territories
TERRITORY_L5_VALIDATORS = "L5 Safety/Validators"
TERRITORY_L5_VALIDATORS_CONTENT = "L5 Safety/Validators/Content"
TERRITORY_L5_VALIDATORS_STRUCTURE = "L5 Safety/Validators/Structure"
TERRITORY_L5_GUARDRAILS = "L5 Safety/Guardrails"
TERRITORY_L5_GUARDRAILS_MCP = "L5 Safety/Guardrails/MCP"
TERRITORY_L5_GUARDRAILS_CORE = "L5 Safety/Guardrails/Core"
TERRITORY_L5_GUARDRAILS_THREAT = "L5 Safety/Guardrails/Threat"  # Threat detection and red teaming
TERRITORY_L5_GUARDRAILS_HYGIENE = "L5 Safety/Guardrails/Hygiene"  # Code hygiene and cleanup
TERRITORY_L5_RED_TEAMING = "L5 Safety/Red Teaming"
TERRITORY_L5_GRAVITY = "L5 Safety/Gravity"

# L6 observability Territories
TERRITORY_L6_METRICS = "L6_Observability/Metrics"
TERRITORY_L6_TELEMETRY = "L6_Observability/Telemetry"
TERRITORY_L6_TRACING = "L6_Observability/Tracing"
TERRITORY_L6_COMPLIANCE = "L6_Observability/Compliance"

# Apps Territories
TERRITORY_APPS_LIC = "Apps Lic"
TERRITORY_APPS_LIC_ENGINES = "Apps Lic/Engines"
TERRITORY_APPS_LIC_ORCHESTRATION = "Apps Lic/Orchestration"  # Orchestrators and workflow agents
TERRITORY_APPS_LIC_HOP = "Apps Lic/HOP"  # HOP pipeline agents
TERRITORY_APPS_LIC_DOMAIN = "Apps Lic/Domain"
TERRITORY_APPS_LIC_UTILITIES = "Apps Lic/Utilities"
TERRITORY_APPS_RG = "Apps Rg"
TERRITORY_APPS_RG_ENGINES = "Apps Rg/Engines"
TERRITORY_APPS_RG_ORCHESTRATION = "Apps Rg/Orchestration"  # Orchestrators and phase agents
TERRITORY_APPS_RG_DOMAIN = "Apps Rg/Domain"
TERRITORY_APPS_SHARED = "Apps Shared"

# Utils Territory (DEPRECATED - now maps to Apps Shared)
TERRITORY_UTILS = "Apps Shared"  # Changed from "Utils" to "Apps Shared"

# ============================================================================
# TERRITORY MAPPING FUNCTIONS
# ============================================================================


def get_base_agent_territory(layer: str) -> str:
    """
    Get the canonical territory name for a base agent in a given layer.

    Args:
        layer: Layer name (e.g., 'L0', 'L1', 'Base')

    Returns:
        Canonical territory name for the base agent
    """
    base_territories = {
        "Base": TERRITORY_SOVEREIGN_BASE,
        "L0": TERRITORY_L0_BASE,
        "L1": TERRITORY_L1_BASE,
        "L2": TERRITORY_L2_BASE,
        "L3": TERRITORY_L3_BASE,
        "L4": TERRITORY_L4_BASE,
        "L5": TERRITORY_L5_BASE,
        "L6": TERRITORY_L6_BASE,
    }
    return base_territories.get(layer, f"{layer}/Base Agent")


def get_territory_from_path(layer: str, path_str: str, is_base_class: bool, class_name: str = "") -> str:
    """
    Determine the canonical territory name based on layer, path, and class type.

    Args:
        layer: Layer name (e.g., 'L0', 'L1', 'Base')
        path_str: Lowercase path string (e.g., 'agentic_core/l5_safety/validators')
        is_base_class: Whether this is a base agent class
        class_name: Name of the class (optional, for special cases)

    Returns:
        Canonical territory name
    """
    # Special case: SovereignBaseAgent
    if class_name == "SovereignBaseAgent" or layer == "Base":
        return TERRITORY_SOVEREIGN_BASE

    # Base agents get their layer's base territory
    if is_base_class:
        return get_base_agent_territory(layer)

    # Apps territories
    if "apps_lic" in path_str:
        return TERRITORY_APPS_LIC
    elif "apps_rg" in path_str:
        return TERRITORY_APPS_RG
    elif "apps_shared" in path_str:
        return TERRITORY_APPS_SHARED

    # Utils territory
    if "utils" in path_str:
        return TERRITORY_UTILS

    # Layer-specific territories
    if layer == "L5":
        if "validators" in path_str or "validator" in path_str:
            return TERRITORY_L5_VALIDATORS
        elif "red_team" in path_str or "red_teaming" in path_str:
            return TERRITORY_L5_RED_TEAMING
        elif "gravity" in path_str:
            return TERRITORY_L5_GRAVITY
        else:
            return TERRITORY_L5_GUARDRAILS

    elif layer == "L4":
        if "filesystem" in path_str or "infrastructure" in path_str:
            return TERRITORY_L4_INFRASTRUCTURE
        elif "adapter" in path_str:
            return TERRITORY_L4_SPECIALIZED
        else:
            return TERRITORY_L4_CORE

    elif layer == "L3":
        if "infrastructure" in path_str:
            return TERRITORY_L3_INFRASTRUCTURE
        elif "adapter" in path_str:
            return TERRITORY_L3_SPECIALIZED
        else:
            return TERRITORY_L3_CORE

    elif layer == "L2":
        if "adapter" in path_str:
            return TERRITORY_L2_SPECIALIZED
        else:
            return TERRITORY_L2_CORE

    elif layer == "L1":
        if "adapter" in path_str:
            return TERRITORY_L1_SPECIALIZED
        else:
            return TERRITORY_L1_CORE

    elif layer == "L0":
        if "infrastructure" in path_str:
            return TERRITORY_L0_INFRASTRUCTURE
        else:
            return TERRITORY_L0_CORE

    elif layer == "L6":
        if "metrics" in path_str:
            return TERRITORY_L6_METRICS
        elif "telemetry" in path_str:
            return TERRITORY_L6_TELEMETRY
        elif "tracing" in path_str:
            return TERRITORY_L6_TRACING
        elif "compliance" in path_str:
            return TERRITORY_L6_COMPLIANCE
        else:
            return TERRITORY_L6_METRICS

    # Fallback
    return layer if layer else "Unknown"


# ============================================================================
# CANONICAL TERRITORY ORDER (for dashboard sorting)
# ============================================================================

CANONICAL_TERRITORY_ORDER = [
    # Sovereign Base Agent always first
    TERRITORY_SOVEREIGN_BASE,
    # L6 observability
    TERRITORY_L6_BASE,
    TERRITORY_L6_METRICS,
    TERRITORY_L6_TELEMETRY,
    TERRITORY_L6_TRACING,
    TERRITORY_L6_COMPLIANCE,
    # L5 Safety
    TERRITORY_L5_BASE,
    TERRITORY_L5_VALIDATORS,
    TERRITORY_L5_VALIDATORS_CONTENT,
    TERRITORY_L5_VALIDATORS_STRUCTURE,
    TERRITORY_L5_GUARDRAILS,
    TERRITORY_L5_GUARDRAILS_MCP,
    TERRITORY_L5_GUARDRAILS_CORE,
    TERRITORY_L5_GUARDRAILS_THREAT,
    TERRITORY_L5_GUARDRAILS_HYGIENE,
    TERRITORY_L5_RED_TEAMING,
    TERRITORY_L5_GRAVITY,
    # L4 State
    TERRITORY_L4_BASE,
    TERRITORY_L4_CORE,
    TERRITORY_L4_INFRASTRUCTURE,
    TERRITORY_L4_SPECIALIZED,
    # L3 Orchestration
    TERRITORY_L3_BASE,
    TERRITORY_L3_CORE,
    TERRITORY_L3_DAG,
    TERRITORY_L3_WORKFLOW,
    TERRITORY_L3_TERRITORY,
    TERRITORY_L3_RL,
    TERRITORY_L3_ROUTING,
    TERRITORY_L3_MONITORING,
    TERRITORY_L3_INFRASTRUCTURE,
    TERRITORY_L3_SPECIALIZED,
    # L2 Execution
    TERRITORY_L2_BASE,
    TERRITORY_L2_CORE,
    TERRITORY_L2_RUNNERS,
    TERRITORY_L2_HANDLERS,
    TERRITORY_L2_COORDINATORS,
    TERRITORY_L2_SPECIALIZED,
    # L1 Cognition
    TERRITORY_L1_BASE,
    TERRITORY_L1_CORE,
    TERRITORY_L1_REASONING,
    TERRITORY_L1_VALIDATION,
    TERRITORY_L1_MEMORY,
    TERRITORY_L1_PLANNING,
    TERRITORY_L1_SPECIALIZED,
    # L0 Maintenance
    TERRITORY_L0_BASE,
    TERRITORY_L0_CORE,
    TERRITORY_L0_INFRASTRUCTURE,
    # Apps
    TERRITORY_APPS_LIC,
    TERRITORY_APPS_LIC_ENGINES,
    TERRITORY_APPS_LIC_ORCHESTRATION,
    TERRITORY_APPS_LIC_HOP,
    TERRITORY_APPS_LIC_DOMAIN,
    TERRITORY_APPS_LIC_UTILITIES,
    TERRITORY_APPS_RG,
    TERRITORY_APPS_RG_ENGINES,
    TERRITORY_APPS_RG_ORCHESTRATION,
    TERRITORY_APPS_RG_DOMAIN,
    TERRITORY_APPS_SHARED,
    # Utils
    TERRITORY_UTILS,
]


def get_territory_sort_key(territory: str) -> int:
    """
    Get the sort key for a territory (for canonical ordering).

    Args:
        territory: Territory name

    Returns:
        Sort key (lower = earlier in list)
    """
    try:
        return CANONICAL_TERRITORY_ORDER.index(territory)
    except ValueError:
        # Unknown territories go to the end
        return 9999


# ============================================================================
# HIGH-COUNT TERRITORY SUBDIVISION (AST-based)
# ============================================================================

# Territories with >15 agents that need subdivision
HIGH_COUNT_TERRITORIES = {
    TERRITORY_L3_CORE,
    TERRITORY_APPS_LIC,
    TERRITORY_L2_CORE,
    TERRITORY_L5_GUARDRAILS,
    TERRITORY_L1_CORE,
    TERRITORY_APPS_RG,
    TERRITORY_L5_VALIDATORS,
}


def refine_territory_by_ast(territory: str, class_name: str, docstring: str, path_str: str) -> str:
    """
    Refine high-count territories into sub-territories using AST analysis.

    This function subdivides territories with >15 agents into semantically
    meaningful sub-territories based on class name patterns, docstring keywords,
    and directory structure.

    Args:
        territory: Current territory from get_territory_from_path()
        class_name: Agent class name
        docstring: Class docstring (first line or full)
        path_str: Normalized path string (lowercase, forward slashes)

    Returns:
        Refined territory name or original if no subdivision needed
    """
    # Only subdivide high-count territories
    if territory not in HIGH_COUNT_TERRITORIES:
        return territory

    # L3 Orchestration/Core → 4 sub-territories
    if territory == TERRITORY_L3_CORE:
        return _categorize_l3_orchestration(class_name, docstring, path_str)

    # Apps Lic → 3 sub-territories
    if territory == TERRITORY_APPS_LIC:
        return _categorize_apps_lic(class_name, docstring, path_str)

    # L2 Execution/Core → 3 sub-territories
    if territory == TERRITORY_L2_CORE:
        return _categorize_l2_execution(class_name, docstring, path_str)

    # L5 Safety/Guardrails → 2 sub-territories
    if territory == TERRITORY_L5_GUARDRAILS:
        return _categorize_l5_guardrails(class_name, docstring, path_str)

    # L1 Cognition/Core → 3 sub-territories
    if territory == TERRITORY_L1_CORE:
        return _categorize_l1_cognition(class_name, docstring, path_str)

    # Apps Rg → 2 sub-territories
    if territory == TERRITORY_APPS_RG:
        return _categorize_apps_rg(class_name, docstring, path_str)

    # L5 Safety/Validators → 2 sub-territories
    if territory == TERRITORY_L5_VALIDATORS:
        return _categorize_l5_validators(class_name, docstring, path_str)

    return territory


def _categorize_l3_orchestration(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L3 Orchestration/Core agents into 5 sub-territories."""
    name_lower = class_name.lower()
    doc_lower = (docstring or "").lower()

    # DAG-related agents
    if "dag" in name_lower or "dag" in doc_lower or "graph" in doc_lower:
        return TERRITORY_L3_DAG

    # Reinforcement Learning orchestrators (PPO, RL, Q-Learning, Actor-Critic)
    if any(kw in name_lower for kw in ["ppo", "qlearning", "actorcritic", "reinforcecritic", "rlorchestrat"]):
        return TERRITORY_L3_RL

    # Routing and connection management
    if any(kw in name_lower for kw in ["router", "connection", "permission", "registry", "gatekeeper"]):
        return TERRITORY_L3_ROUTING

    # Monitoring, metrics, coverage, detection, telemetry, observability, cost, reporting
    if any(
        kw in name_lower
        for kw in [
            "metric",
            "coverage",
            "detector",
            "monitor",
            "benchmark",
            "inspector",
            "telemetry",
            "observability",
            "cost",
            "report",
            "auditor",
            "track",
        ]
    ):
        return TERRITORY_L3_MONITORING

    # Territory and semantic mapping agents
    if any(kw in name_lower for kw in ["territory", "semantic", "mapper", "hierarchy"]):
        return TERRITORY_L3_TERRITORY

    # Workflow orchestration, fission, healing
    if any(
        kw in name_lower
        for kw in [
            "workflow",
            "orchestrat",
            "nervous",
            "phase",
            "handshake",
            "fission",
            "healer",
            "governor",
            "signature",
            "canon",
            "subatomic",
            "testpilot",
            "exerciser",
            "ssot",
            "rag",
            "cached",
            "scope",
            "git",
        ]
    ):
        return TERRITORY_L3_WORKFLOW

    # Fallback: Keep in Core
    return TERRITORY_L3_CORE


def _categorize_apps_lic(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize Apps Lic agents into 5 sub-territories."""
    name_lower = class_name.lower()

    # HOP pipeline agents (HOP1-HOP8, HOPOrchestrator)
    if "hop" in name_lower:
        return TERRITORY_APPS_LIC_HOP

    # Orchestration agents (orchestrators, workflow, supervisor, healing)
    if any(kw in name_lower for kw in ["orchestrat", "workflow", "supervisor", "s2supervisor", "healing"]):
        return TERRITORY_APPS_LIC_ORCHESTRATION

    # Utilities - helpers, formatters, parsers
    if "/utils/" in path_str or any(
        kw in name_lower for kw in ["util", "helper", "formatter", "parser", "converter"]
    ):
        return TERRITORY_APPS_LIC_UTILITIES

    # Domain agents - validators, quality, content, test, validation (check before engines)
    if "/domain/" in path_str or "/validators/" in path_str:
        return TERRITORY_APPS_LIC_DOMAIN
    if any(
        kw in name_lower
        for kw in [
            "validator",
            "quality",
            "compliance",
            "checker",
            "enforcer",
            "test",
            "validation",
        ]
    ):
        return TERRITORY_APPS_LIC_DOMAIN

    # Engines (default for apps_lic)
    return TERRITORY_APPS_LIC_ENGINES


def _categorize_l2_execution(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L2 Execution/Core agents into 3 sub-territories."""
    name_lower = class_name.lower()

    # Coordinators and managers (check first - more specific)
    if any(
        kw in name_lower
        for kw in [
            "coordinator",
            "manager",
            "scheduler",
            "dispatcher",
            "orchestrator",
            "architect",
            "strategist",
            "curator",
            "diplomat",
            "governor",
        ]
    ):
        return TERRITORY_L2_COORDINATORS

    # Event handlers and validators
    if any(
        kw in name_lower
        for kw in [
            "handler",
            "event",
            "listener",
            "callback",
            "validator",
            "enforcer",
            "detector",
            "inspector",
            "auditor",
            "gate",
            "boundary",
            "seal",
        ]
    ):
        return TERRITORY_L2_HANDLERS

    # Task runners and executors (default - includes tools, healers, agents)
    return TERRITORY_L2_RUNNERS


def _categorize_l5_guardrails(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L5 Safety/Guardrails agents into 3 sub-territories."""
    name_lower = class_name.lower()
    doc_lower = (docstring or "").lower()

    # MCP-related safety and hardening
    if any(kw in name_lower for kw in ["mcp", "hardened", "hardening", "rollback", "recovery", "circuit"]):
        return TERRITORY_L5_GUARDRAILS_MCP
    if "mcp" in doc_lower:
        return TERRITORY_L5_GUARDRAILS_MCP

    # Code hygiene and cleanup agents
    if any(
        kw in name_lower
        for kw in [
            "hygiene",
            "cleanup",
            "formatter",
            "duplicate",
            "import",
            "file",
            "dependency",
            "pruning",
            "lock",
            "git",
            "hierarchy",
            "structural",
            "healer",
        ]
    ):
        return TERRITORY_L5_GUARDRAILS_HYGIENE

    # Threat detection and red teaming agents
    if any(
        kw in name_lower
        for kw in [
            "threat",
            "adversarial",
            "red",
            "sentinel",
            "hunter",
            "autoimmune",
            "neural",
            "policy",
            "safety",
            "inspector",
            "debugger",
        ]
    ):
        return TERRITORY_L5_GUARDRAILS_THREAT

    # Core guardrails (cost, composite, exerciser, integrity, checkpoint, config)
    return TERRITORY_L5_GUARDRAILS_CORE


def _categorize_l1_cognition(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L1 Cognition/Core agents into 4 sub-territories."""
    name_lower = class_name.lower()
    (docstring or "").lower()

    # Memory and context
    if any(kw in name_lower for kw in ["memory", "context", "cache", "recall", "history"]):
        return TERRITORY_L1_MEMORY

    # Planning, strategy, orchestration, governance
    if any(
        kw in name_lower
        for kw in [
            "plan",
            "strategy",
            "goal",
            "intent",
            "decision",
            "orchestrat",
            "governance",
            "budget",
            "router",
            "mapper",
            "metalearning",
            "meta",
        ]
    ):
        return TERRITORY_L1_PLANNING

    # Validation agents (validators that are in L1)
    if "validator" in name_lower:
        return TERRITORY_L1_VALIDATION

    # Reasoning and LLM (default for cognition)
    return TERRITORY_L1_REASONING


def _categorize_apps_rg(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize Apps Rg agents into 3 sub-territories."""
    name_lower = class_name.lower()

    # Orchestration agents (orchestrators, phase agents)
    if any(kw in name_lower for kw in ["orchestrat", "phase", "unified", "planner"]):
        return TERRITORY_APPS_RG_ORCHESTRATION

    # Domain agents - validators, quality, content
    if "/domain/" in path_str or "/validators/" in path_str:
        return TERRITORY_APPS_RG_DOMAIN
    if any(
        kw in name_lower
        for kw in ["validator", "quality", "compliance", "checker", "content", "fact", "balance"]
    ):
        return TERRITORY_APPS_RG_DOMAIN

    # Engines (default for apps_rg)
    return TERRITORY_APPS_RG_ENGINES


def _categorize_l5_validators(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L5 Safety/Validators agents into 2 sub-territories."""
    name_lower = class_name.lower()
    doc_lower = (docstring or "").lower()

    # Content validation - text, format, naming, documentation, syntax, type hints
    if any(
        kw in name_lower
        for kw in [
            "content",
            "text",
            "ascii",
            "format",
            "string",
            "message",
            "naming",
            "doc",
            "print",
            "debug",
            "eval",
            "exec",
            "http",
            "builtin",
            "bare",
            "empty",
            "async",
            "blocking",
            "syntax",
            "typehint",
            "pascal",
            "python",
            "input",
        ]
    ):
        return TERRITORY_L5_VALIDATORS_CONTENT
    if any(kw in doc_lower for kw in ["content", "text", "format", "string"]):
        return TERRITORY_L5_VALIDATORS_CONTENT

    # Structure validation (default) - schema, hierarchy, contract, base class
    return TERRITORY_L5_VALIDATORS_STRUCTURE
