"""
Derived Module - COLD PATH (Derived Registries and Compilation)

This module contains derived registries that are computed from
SOVEREIGN_TERRITORIES, eliminating static duplication.

Loaded lazily on first access.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from agentic_core.L5_safety.config.structure_blueprint._constants import (
    SOVEREIGN_TERRITORIES,
)

# ============================================================================
# DERIVATION FUNCTIONS
# ============================================================================


def _derive_core_subfolder_map() -> dict[str, list[str]]:
    """Derive CORE_SUBFOLDER_MAP from SOVEREIGN_TERRITORIES."""
    result: dict[str, list[str]] = {}
    agentic_core = SOVEREIGN_TERRITORIES.get("agentic_core", {})
    subfolders = agentic_core.get("subfolders", {})

    for domain_name, domain_def in subfolders.items():
        if isinstance(domain_def, dict):
            nested = domain_def.get("subfolders", {})
            if isinstance(nested, dict):
                result[domain_name] = list(nested.keys())
            else:
                result[domain_name] = []
        else:
            result[domain_name] = []

    return result


def _derive_subfolder_metadata() -> dict[str, dict[str, Any]]:
    """Derive SUBFOLDER_METADATA from SOVEREIGN_TERRITORIES."""
    result: dict[str, dict[str, Any]] = {}
    agentic_core = SOVEREIGN_TERRITORIES.get("agentic_core", {})
    subfolders = agentic_core.get("subfolders", {})

    for domain_name, domain_def in subfolders.items():
        if isinstance(domain_def, dict):
            result[domain_name] = {
                "purpose": domain_def.get("purpose", f"{domain_name} domain"),
                "content_types": list(domain_def.get("subfolders", {}).keys()) or [domain_name],
                "execution_allowed": domain_def.get("execution_allowed", False),
                "notes": domain_def.get("notes", ""),
            }

    return result


def _derive_apps_subfolder_map(territory_name: str) -> dict[str, list[str]]:
    """Derive APPS_*_SUBFOLDER_MAP from SOVEREIGN_TERRITORIES."""
    result: dict[str, list[str]] = {}
    territory = SOVEREIGN_TERRITORIES.get(territory_name, {})
    if not isinstance(territory, dict):
        return result

    subfolders = territory.get("subfolders", {})

    if isinstance(subfolders, (list, tuple)):
        for sf_name in subfolders:
            result[sf_name] = []
        return result

    if not isinstance(subfolders, dict):
        return result

    for sf_name, sf_def in subfolders.items():
        if isinstance(sf_def, dict):
            nested = sf_def.get("subfolders", {})
            if isinstance(nested, dict):
                result[sf_name] = list(nested.keys())
            elif isinstance(nested, (list, tuple)):
                result[sf_name] = list(nested)
            else:
                result[sf_name] = []
        elif isinstance(sf_def, (list, tuple)):
            result[sf_name] = list(sf_def)
        else:
            result[sf_name] = []

    return result


# ============================================================================
# DERIVED REGISTRIES
# ============================================================================

CORE_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_core_subfolder_map()
SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = _derive_subfolder_metadata()
APPS_RG_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map("apps_rg")
APPS_LIC_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map("apps_lic")
APPS_SHARED_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map("apps_shared")

# Type-safe alias
agentic_core_registry: Final[Mapping[str, Sequence[str]]] = CORE_SUBFOLDER_MAP


# ============================================================================
# L4 SUBFOLDER MAP
# ============================================================================

L4_SUBFOLDER_MAP: Final[Mapping[str, Mapping[str, Sequence[str]]]] = {
    "dashboards": {
        "generators": ["dashboard_generators", "data_generators"],
        "templates": ["html_templates", "component_templates"],
        "components": ["ui_components", "chart_components"],
        "data": ["json_data", "runtime_data"],
        "tests": ["unit_tests", "e2e_tests"],
        "js": ["components", "controllers", "renderers", "utils", "constants"],
        "css": ["themes", "layouts"],
        "config": ["dashboard_config"],
    },
    "reasoning": {
        "healing": ["audit_healing_strategy"],
    },
    "scripts": {
        "healing": ["healing_strategies", "healing_engines"],
        "validation": ["validators", "checkers"],
        "utilities": ["file_utilities", "code_utilities"],
        "workflows": ["workflow_scripts", "pipeline_scripts"],
        "installation": ["install_scripts"],
        "maintenance": ["maintenance_scripts"],
        "test_utilities": ["test_helpers"],
    },
    "L3_reasoning": {
        "core": ["base_orchestrators", "orchestration_types"],
        "dag": ["dag_executors", "dag_managers"],
        "rl": ["rl_orchestrators", "rl_coordinators"],
        "mission": ["mission_controllers", "mission_runners"],
        "mcp": ["mcp_routers", "mcp_managers"],
        "safety": ["safety_orchestrators"],
        "state": ["state_managers"],
        "rag": ["rag_orchestrators"],
        "telemetry": ["telemetry_agents", "metrics_agents"],
    },
    "L1_reasoning": {
        "engines": ["reasoning_engines", "logic_processors"],
        "planning": ["planners", "schedulers"],
        "memory": ["memory_managers", "context_handlers"],
        "analysis": ["analyzers", "evaluators"],
        "synthesis": ["synthesizers", "generators"],
        "evaluation": ["evaluators", "scorers"],
    },
    "enforcement": {
        "security": ["pii_guards", "injection_guards", "auth_guards"],
        "quality": ["code_quality", "format_guards"],
        "structural": ["hierarchy_healers", "structure_guards"],
        "constitutional": ["constitutional_ai", "governance_guards"],
        "resource": ["resource_guards", "budget_guards"],
        "mcp": ["mcp_security", "mcp_guards"],
        "detection": ["duplicate_detectors", "threat_detectors"],
    },
    "L2_reasoning": {
        "core": ["registry_core", "registry_types"],
        "tools": ["tool_implementations"],
        "handlers": ["tool_handlers"],
        "validators": ["tool_validators"],
        "adapters": ["tool_adapters"],
    },
    "L5_enforcement": {
        "governance": ["governance_policies", "compliance_rules"],
        "security": ["security_guards", "access_control"],
    },
    "L6_dashboards": {
        "core": ["dashboard_core"],
        "css": ["themes", "layouts"],
        "data": ["json_data", "runtime_data"],
        "js": {
            "components": ["ui_components"],
            "constants": ["js_constants"],
            "controllers": ["dashboard_controllers"],
            "renderers": ["chart_renderers"],
            "utils": ["js_utils"],
        },
        "renderers": ["server_renderers"],
    },
    "prompt_governance": {
        "meta_prompts": {
            "orchestration": ["agents", "flows"],
            "reasoning": ["cot", "tot", "react"],
            "security": ["guards", "pii"],
            "personas": ["roles", "behavioral"],
        },
        "templates": {
            "instructional": ["cognition", "execution", "safety"],
            "specialized": ["domain", "format"],
            "fragments": ["partials", "blocks"],
            "rendering": ["engines", "filters"],
        },
        "scripts": {
            "audit": ["syntax_checks", "compliance_scans"],
            "migration": ["version_porters", "legacy_converters"],
            "maintenance": ["registry_cleaners", "cache_managers"],
        },
        "version_registry": {
            "manifests": ["active", "history"],
            "locks": ["commit_locks"],
            "lineage": ["parents", "forks"],
        },
    },
}

L4_APPROVED_FOLDERS: Final[frozenset[str]] = frozenset(
    {
        "agentic_core/L6_observability/dashboards",
        "agentic_core/L0_routing/scripts",
        "agentic_core/L0_routing/reasoning",
        "agentic_core/L3_orchestration/reasoning",
        "agentic_core/L1_cognition/reasoning",
        "agentic_core/L5_safety/enforcement",
        "agentic_core/L5_safety/validators",
        "agentic_core/L5_safety/reasoning",
        "agentic_core/L5_safety/config",
        "agentic_core/L2_execution/reasoning",
        "agentic_core/L2_execution/tools",
        "agentic_core/L4_state/memory",
        "agentic_core/config/core",
        "agentic_core/prompt_governance/meta_prompts",
        "agentic_core/prompt_governance/templates",
        "agentic_core/prompt_governance/scripts",
        "agentic_core/prompt_governance/version_registry",
        "agentic_core/prompt_governance/registry",
        "agentic_core/prompt_governance/security",
        "agentic_core/seams/contracts",
    },
)


# ============================================================================
# SCRIPTS PLACEMENT RULES
# ============================================================================

SCRIPTS_PLACEMENT_RULES: Final[Mapping[str, Mapping[str, Any]]] = {
    "root_ops_scripts": {
        "description": "Standalone utilities (setup, pip, env) with NO core dependencies.",
        "forbidden_imports": ["agentic_core"],
        "allowed_depth": 1,
        "violation_destination": "agentic_core/L0_routing/scripts",
    },
    "l0_maintenance_scripts": {
        "description": "System maintenance, healing, and sovereign agents.",
        "required_capabilities": ["core_access"],
        "preferred_location": "agentic_core/L0_routing/scripts",
    },
}


# ============================================================================
# TESTS SUBFOLDER MAP
# ============================================================================

TESTS_L2_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "unit": [],
    "integration": [],
    "e2e": [],
    "functional": [],
    "fixtures": [],
    "core": [],
    "apps_rg": [],
    "apps_lic": [],
}

TESTS_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = TESTS_L2_SUBFOLDER_MAP


# ============================================================================
# VERIFICATION FUNCTION
# ============================================================================


def verify_derived_registries() -> list[str]:
    """Verify derived registries are consistent with SOVEREIGN_TERRITORIES."""

    discrepancies: list[str] = []

    standard_lcd = {"config", "types", "reasoning", "enforcement", "validators", "utils"}
    for layer in [
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    ]:
        derived = set(CORE_SUBFOLDER_MAP.get(layer, []))
        if not standard_lcd.issubset(derived):
            missing = standard_lcd - derived
            discrepancies.append(f"{layer} missing LCD subfolders: {missing}")

    for key in CORE_SUBFOLDER_MAP:
        if key not in SUBFOLDER_METADATA:
            discrepancies.append(f"SUBFOLDER_METADATA missing key: {key}")

    if not APPS_RG_SUBFOLDER_MAP:
        discrepancies.append("APPS_RG_SUBFOLDER_MAP is empty")

    return discrepancies
