#!/usr/bin/env python3
from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)

"""
scripts/maintenance/territory_ssot_definitions.py
-------------------------------------------------
SSOT: Territory Name Definitions
=================================

Single Source of Truth for all territory names used in agent discovery and dashboard.

CRITICAL: All territory names MUST be defined here and used consistently.
Aligned with SOVEREIGN_TERRITORIES schema (Functional Naming).
"""

# ============================================================================
# CANONICAL TERRITORY NAMES (FUNCTIONAL NAMING)
# ============================================================================

# Base/Root Territory
TERRITORY_SOVEREIGN_BASE = "Sovereign Base Agent"

# Layer Base Agent Territories
TERRITORY_MAINTENANCE_BASE = "L0 Maintenance/Base Agent"
TERRITORY_COGNITION_BASE = "L1 Cognition/Base Agent"
TERRITORY_EXECUTION_BASE = "L2 Execution/Base Agent"
TERRITORY_ORCHESTRATION_BASE = "L3 Orchestration/Base Agent"
TERRITORY_STATE_BASE = "L4 State/Base Agent"
TERRITORY_SAFETY_BASE = "L5 Safety/Base Agent"
TERRITORY_OBSERVABILITY_BASE = "L6_Observability/Base Agent"

# L0 Maintenance Territories
TERRITORY_MAINTENANCE_CORE = "L0 Maintenance/Core"
TERRITORY_MAINTENANCE_INFRASTRUCTURE = "L0 Maintenance/Infrastructure"

# L1 Cognition Territories
TERRITORY_COGNITION_CORE = "L1 Cognition/Core"
TERRITORY_COGNITION_REASONING = "L1 Cognition/Reasoning"
TERRITORY_COGNITION_VALIDATION = "L1 Cognition/Validation"
TERRITORY_COGNITION_MEMORY = "L1 Cognition/Memory"
TERRITORY_COGNITION_PLANNING = "L1 Cognition/Planning"
TERRITORY_COGNITION_SPECIALIZED = "L1 Cognition/Specialized"

# L2 Execution Territories
TERRITORY_EXECUTION_CORE = "L2 Execution/Core"
TERRITORY_EXECUTION_RUNNERS = "L2 Execution/Runners"
TERRITORY_EXECUTION_HANDLERS = "L2 Execution/Handlers"
TERRITORY_EXECUTION_COORDINATORS = "L2 Execution/Coordinators"
TERRITORY_EXECUTION_SPECIALIZED = "L2 Execution/Specialized"

# L3 Orchestration Territories
TERRITORY_ORCHESTRATION_CORE = "L3 Orchestration/Core"
TERRITORY_ORCHESTRATION_DAG = "L3 Orchestration/DAG"
TERRITORY_ORCHESTRATION_WORKFLOW = "L3 Orchestration/Workflow"
TERRITORY_ORCHESTRATION_TERRITORY = "L3 Orchestration/Territory"
TERRITORY_ORCHESTRATION_RL = "L3 Orchestration/RL"
TERRITORY_ORCHESTRATION_ROUTING = "L3 Orchestration/Routing"
TERRITORY_ORCHESTRATION_MONITORING = "L3 Orchestration/Monitoring"
TERRITORY_ORCHESTRATION_INFRASTRUCTURE = "L3 Orchestration/Infrastructure"
TERRITORY_ORCHESTRATION_SPECIALIZED = "L3 Orchestration/Specialized"

# L4 State Territories
TERRITORY_STATE_CORE = "L4 State/Core"
TERRITORY_STATE_INFRASTRUCTURE = "L4 State/Infrastructure"
TERRITORY_STATE_SPECIALIZED = "L4 State/Specialized"

# L5 Safety Territories
TERRITORY_SAFETY_VALIDATORS = "L5 Safety/Validators"
TERRITORY_SAFETY_VALIDATORS_CONTENT = "L5 Safety/Validators/Content"
TERRITORY_SAFETY_VALIDATORS_STRUCTURE = "L5 Safety/Validators/Structure"
TERRITORY_SAFETY_GUARDRAILS = "L5 Safety/Guardrails"
TERRITORY_SAFETY_GUARDRAILS_MCP = "L5 Safety/Guardrails/MCP"
TERRITORY_SAFETY_GUARDRAILS_CORE = "L5 Safety/Guardrails/Core"
TERRITORY_SAFETY_GUARDRAILS_THREAT = "L5 Safety/Guardrails/Threat"
TERRITORY_SAFETY_GUARDRAILS_HYGIENE = "L5 Safety/Guardrails/Hygiene"
TERRITORY_SAFETY_RED_TEAMING = "L5 Safety/Red Teaming"
TERRITORY_SAFETY_GRAVITY = "L5 Safety/Gravity"

# L6 Observability Territories
TERRITORY_OBSERVABILITY_METRICS = "L6_Observability/Metrics"
TERRITORY_OBSERVABILITY_TELEMETRY = "L6_Observability/Telemetry"
TERRITORY_OBSERVABILITY_TRACING = "L6_Observability/Tracing"
TERRITORY_OBSERVABILITY_COMPLIANCE = "L6_Observability/Compliance"

# Apps Territories
TERRITORY_APPS_LIC = "Apps Lic"
TERRITORY_APPS_LIC_ENGINES = "Apps Lic/Engines"
TERRITORY_APPS_LIC_ORCHESTRATION = "Apps Lic/Orchestration"
TERRITORY_APPS_LIC_HOP = "Apps Lic/HOP"
TERRITORY_APPS_LIC_DOMAIN = "Apps Lic/Domain"
TERRITORY_APPS_LIC_UTILITIES = "Apps Lic/Utilities"
TERRITORY_APPS_RG = "Apps Rg"
TERRITORY_APPS_RG_ENGINES = "Apps Rg/Engines"
TERRITORY_APPS_RG_ORCHESTRATION = "Apps Rg/Orchestration"
TERRITORY_APPS_RG_DOMAIN = "Apps Rg/Domain"
TERRITORY_APPS_SHARED = "Apps Shared"

# ============================================================================
# TERRITORY MAPPING FUNCTIONS
# ============================================================================


def get_base_agent_territory(layer: str) -> str:
    """Get the canonical territory name for a base agent."""
    base_territories = {
        "Base": TERRITORY_SOVEREIGN_BASE,
        "L0": TERRITORY_MAINTENANCE_BASE,
        "L1": TERRITORY_COGNITION_BASE,
        "L2": TERRITORY_EXECUTION_BASE,
        "L3": TERRITORY_ORCHESTRATION_BASE,
        "L4": TERRITORY_STATE_BASE,
        "L5": TERRITORY_SAFETY_BASE,
        "L6": TERRITORY_OBSERVABILITY_BASE,
    }
    return base_territories.get(layer, f"{layer}/Base Agent")


def get_territory_from_path(
    layer: str,
    path_str: str,
    is_base_class: bool,
    class_name: str = "",
) -> str:
    """Determine the canonical territory name based on layer, path, and class type."""
    if class_name == "SovereignBaseAgent" or layer == "Base":
        return TERRITORY_SOVEREIGN_BASE

    if is_base_class:
        return get_base_agent_territory(layer)

    if APPS_LIC_DIR in path_str:
        return TERRITORY_APPS_LIC
    elif APPS_RG_DIR in path_str:
        return TERRITORY_APPS_RG
    elif APPS_SHARED_DIR in path_str:
        return TERRITORY_APPS_SHARED

    if layer == "L5":
        if "validators" in path_str or "validator" in path_str:
            return TERRITORY_SAFETY_VALIDATORS
        elif "red_team" in path_str or "red_teaming" in path_str:
            return TERRITORY_SAFETY_RED_TEAMING
        elif "gravity" in path_str:
            return TERRITORY_SAFETY_GRAVITY
        else:
            return TERRITORY_SAFETY_GUARDRAILS

    elif layer == "L4":
        if "filesystem" in path_str or "infrastructure" in path_str:
            return TERRITORY_STATE_INFRASTRUCTURE
        elif "adapter" in path_str:
            return TERRITORY_STATE_SPECIALIZED
        else:
            return TERRITORY_STATE_CORE

    elif layer == "L3":
        if "infrastructure" in path_str:
            return TERRITORY_ORCHESTRATION_INFRASTRUCTURE
        elif "adapter" in path_str:
            return TERRITORY_ORCHESTRATION_SPECIALIZED
        else:
            return TERRITORY_ORCHESTRATION_CORE

    elif layer == "L2":
        if "adapter" in path_str:
            return TERRITORY_EXECUTION_SPECIALIZED
        else:
            return TERRITORY_EXECUTION_CORE

    elif layer == "L1":
        if "adapter" in path_str:
            return TERRITORY_COGNITION_SPECIALIZED
        else:
            return TERRITORY_COGNITION_CORE

    elif layer == "L0":
        if "infrastructure" in path_str:
            return TERRITORY_MAINTENANCE_INFRASTRUCTURE
        else:
            return TERRITORY_MAINTENANCE_CORE

    elif layer == "L6":
        if "metrics" in path_str:
            return TERRITORY_OBSERVABILITY_METRICS
        elif "telemetry" in path_str:
            return TERRITORY_OBSERVABILITY_TELEMETRY
        elif "tracing" in path_str:
            return TERRITORY_OBSERVABILITY_TRACING
        elif "compliance" in path_str:
            return TERRITORY_OBSERVABILITY_COMPLIANCE
        else:
            return TERRITORY_OBSERVABILITY_METRICS

    return layer if layer else "Unknown"


# ============================================================================
# CANONICAL TERRITORY ORDER
# ============================================================================

CANONICAL_TERRITORY_ORDER = [
    TERRITORY_SOVEREIGN_BASE,
    # L6
    TERRITORY_OBSERVABILITY_BASE,
    TERRITORY_OBSERVABILITY_METRICS,
    TERRITORY_OBSERVABILITY_TELEMETRY,
    TERRITORY_OBSERVABILITY_TRACING,
    TERRITORY_OBSERVABILITY_COMPLIANCE,
    # L5
    TERRITORY_SAFETY_BASE,
    TERRITORY_SAFETY_VALIDATORS,
    TERRITORY_SAFETY_VALIDATORS_CONTENT,
    TERRITORY_SAFETY_VALIDATORS_STRUCTURE,
    TERRITORY_SAFETY_GUARDRAILS,
    TERRITORY_SAFETY_GUARDRAILS_MCP,
    TERRITORY_SAFETY_GUARDRAILS_CORE,
    TERRITORY_SAFETY_GUARDRAILS_THREAT,
    TERRITORY_SAFETY_GUARDRAILS_HYGIENE,
    TERRITORY_SAFETY_RED_TEAMING,
    TERRITORY_SAFETY_GRAVITY,
    # L4
    TERRITORY_STATE_BASE,
    TERRITORY_STATE_CORE,
    TERRITORY_STATE_INFRASTRUCTURE,
    TERRITORY_STATE_SPECIALIZED,
    # L3
    TERRITORY_ORCHESTRATION_BASE,
    TERRITORY_ORCHESTRATION_CORE,
    TERRITORY_ORCHESTRATION_DAG,
    TERRITORY_ORCHESTRATION_WORKFLOW,
    TERRITORY_ORCHESTRATION_TERRITORY,
    TERRITORY_ORCHESTRATION_RL,
    TERRITORY_ORCHESTRATION_ROUTING,
    TERRITORY_ORCHESTRATION_MONITORING,
    TERRITORY_ORCHESTRATION_INFRASTRUCTURE,
    TERRITORY_ORCHESTRATION_SPECIALIZED,
    # L2
    TERRITORY_EXECUTION_BASE,
    TERRITORY_EXECUTION_CORE,
    TERRITORY_EXECUTION_RUNNERS,
    TERRITORY_EXECUTION_HANDLERS,
    TERRITORY_EXECUTION_COORDINATORS,
    TERRITORY_EXECUTION_SPECIALIZED,
    # L1
    TERRITORY_COGNITION_BASE,
    TERRITORY_COGNITION_CORE,
    TERRITORY_COGNITION_REASONING,
    TERRITORY_COGNITION_VALIDATION,
    TERRITORY_COGNITION_MEMORY,
    TERRITORY_COGNITION_PLANNING,
    TERRITORY_COGNITION_SPECIALIZED,
    # L0
    TERRITORY_MAINTENANCE_BASE,
    TERRITORY_MAINTENANCE_CORE,
    TERRITORY_MAINTENANCE_INFRASTRUCTURE,
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
]


def get_territory_sort_key(territory: str) -> int:
    try:
        return CANONICAL_TERRITORY_ORDER.index(territory)
    except ValueError:
        return 9999


# ============================================================================
# HIGH-COUNT TERRITORY SUBDIVISION (AST-based)
# ============================================================================

HIGH_COUNT_TERRITORIES = {
    TERRITORY_ORCHESTRATION_CORE,
    TERRITORY_APPS_LIC,
    TERRITORY_EXECUTION_CORE,
    TERRITORY_SAFETY_GUARDRAILS,
    TERRITORY_COGNITION_CORE,
    TERRITORY_APPS_RG,
    TERRITORY_SAFETY_VALIDATORS,
}


def refine_territory_by_ast(territory: str, class_name: str, docstring: str, path_str: str) -> str:
    if territory not in HIGH_COUNT_TERRITORIES:
        return territory

    if territory == TERRITORY_ORCHESTRATION_CORE:
        return _categorize_l3_orchestration(class_name, docstring, path_str)

    if territory == TERRITORY_APPS_LIC:
        return _categorize_apps_lic(class_name, docstring, path_str)

    if territory == TERRITORY_EXECUTION_CORE:
        return _categorize_l2_execution(class_name, docstring, path_str)

    if territory == TERRITORY_SAFETY_GUARDRAILS:
        return _categorize_l5_guardrails(class_name, docstring, path_str)

    if territory == TERRITORY_COGNITION_CORE:
        return _categorize_l1_cognition(class_name, docstring, path_str)

    if territory == TERRITORY_APPS_RG:
        return _categorize_apps_rg(class_name, docstring, path_str)

    if territory == TERRITORY_SAFETY_VALIDATORS:
        return _categorize_l5_validators(class_name, docstring, path_str)

    return territory


def _categorize_l3_orchestration(class_name: str, docstring: str, path_str: str) -> str:
    name_lower = class_name.lower()
    doc_lower = (docstring or "").lower()

    if "dag" in name_lower or "dag" in doc_lower or "graph" in doc_lower:
        return TERRITORY_ORCHESTRATION_DAG

    if any(kw in name_lower for kw in ["ppo", "qlearning", "actorcritic", "reinforcecritic", "rlorchestrat"]):
        return TERRITORY_ORCHESTRATION_RL

    if any(kw in name_lower for kw in ["router", "connection", "permission", "registry", "gatekeeper"]):
        return TERRITORY_ORCHESTRATION_ROUTING

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
        return TERRITORY_ORCHESTRATION_MONITORING

    if any(kw in name_lower for kw in ["territory", "semantic", "mapper", "hierarchy"]):
        return TERRITORY_ORCHESTRATION_TERRITORY

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
        return TERRITORY_ORCHESTRATION_WORKFLOW

    return TERRITORY_ORCHESTRATION_CORE


def _categorize_apps_lic(class_name: str, docstring: str, path_str: str) -> str:
    name_lower = class_name.lower()

    if "hop" in name_lower:
        return TERRITORY_APPS_LIC_HOP

    if any(kw in name_lower for kw in ["orchestrat", "workflow", "supervisor", "s2supervisor", "healing"]):
        return TERRITORY_APPS_LIC_ORCHESTRATION

    if "/utils/" in path_str or any(
        kw in name_lower for kw in ["util", "helper", "formatter", "parser", "converter"]
    ):
        return TERRITORY_APPS_LIC_UTILITIES

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

    return TERRITORY_APPS_LIC_ENGINES


def _categorize_l2_execution(class_name: str, docstring: str, path_str: str) -> str:
    name_lower = class_name.lower()

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
        return TERRITORY_EXECUTION_COORDINATORS

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
        return TERRITORY_EXECUTION_HANDLERS

    return TERRITORY_EXECUTION_RUNNERS


def _categorize_l5_guardrails(class_name: str, docstring: str, path_str: str) -> str:
    name_lower = class_name.lower()
    doc_lower = (docstring or "").lower()

    if any(kw in name_lower for kw in ["mcp", "hardened", "hardening", "rollback", "recovery", "circuit"]):
        return TERRITORY_SAFETY_GUARDRAILS_MCP
    if "mcp" in doc_lower:
        return TERRITORY_SAFETY_GUARDRAILS_MCP

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
        return TERRITORY_SAFETY_GUARDRAILS_HYGIENE

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
        return TERRITORY_SAFETY_GUARDRAILS_THREAT

    return TERRITORY_SAFETY_GUARDRAILS_CORE


def _categorize_l1_cognition(class_name: str, docstring: str, path_str: str) -> str:
    name_lower = class_name.lower()

    if any(kw in name_lower for kw in ["memory", "context", "cache", "recall", "history"]):
        return TERRITORY_COGNITION_MEMORY

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
        return TERRITORY_COGNITION_PLANNING

    if "validator" in name_lower:
        return TERRITORY_COGNITION_VALIDATION

    return TERRITORY_COGNITION_REASONING


def _categorize_apps_rg(class_name: str, docstring: str, path_str: str) -> str:
    name_lower = class_name.lower()

    if any(kw in name_lower for kw in ["orchestrat", "phase", "unified", "planner"]):
        return TERRITORY_APPS_RG_ORCHESTRATION

    if "/domain/" in path_str or "/validators/" in path_str:
        return TERRITORY_APPS_RG_DOMAIN
    if any(
        kw in name_lower
        for kw in ["validator", "quality", "compliance", "checker", "content", "fact", "balance"]
    ):
        return TERRITORY_APPS_RG_DOMAIN

    return TERRITORY_APPS_RG_ENGINES


def _categorize_l5_validators(class_name: str, docstring: str, path_str: str) -> str:
    name_lower = class_name.lower()
    doc_lower = (docstring or "").lower()

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
        return TERRITORY_SAFETY_VALIDATORS_CONTENT
    if any(kw in doc_lower for kw in ["content", "text", "format", "string"]):
        return TERRITORY_SAFETY_VALIDATORS_CONTENT

    return TERRITORY_SAFETY_VALIDATORS_STRUCTURE
