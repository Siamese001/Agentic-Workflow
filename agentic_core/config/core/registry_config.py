"""
SSOT for Sovereign Registry configuration.

SINGLE SOURCE OF TRUTH: SOVEREIGN_REGISTRY is now derived from
SOVEREIGN_TERRITORIES (agentic_core/L5_safety/config/structure_blueprint/_constants.py).
Do NOT add territory definitions here — add them to _constants.py instead.
"""

import os


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _derive_registry() -> dict:
    """Build SOVEREIGN_REGISTRY from SOVEREIGN_TERRITORIES (the true SSOT).

    Produces the flat {name: {depth, subfolders}} shape expected by
    LocationHealerAgent._autonomous_void_violation_resolution().
    """
    from collections.abc import Mapping as _Mapping

    from agentic_core.L5_safety.config.structure_blueprint import (
        SOVEREIGN_TERRITORIES,
    )

    registry: dict = {}
    for name, cfg in SOVEREIGN_TERRITORIES.items():
        subfolders = cfg.get("subfolders", {})
        if isinstance(subfolders, _Mapping):
            subfolder_list = sorted(subfolders.keys())
        elif isinstance(subfolders, (list, tuple, frozenset, set)):
            subfolder_list = sorted(subfolders)
        else:
            subfolder_list = []
        entry: dict = {
            "depth": cfg.get("depth", 2),
            "subfolders": subfolder_list,
        }
        if cfg.get("layer_prefix_exempt"):
            entry["layer_prefix_exempt"] = True
        if cfg.get("volatile"):
            entry["volatile"] = True
        registry[name] = entry
    return registry


SOVEREIGN_REGISTRY: dict = _derive_registry()

# ============================================================================
# HEALING CONFIGURATION
# ============================================================================
HEALING_CONFIG: dict = {
    "max_rounds": int(os.getenv("MAX_HEALING_ROUNDS", "10")),
    "max_per_file": int(os.getenv("MAX_HEALING_PER_FILE", "8")),
    "global_budget": int(os.getenv("GLOBAL_HEALING_BUDGET", "500")),
    "max_moves_per_run": 250,
    "max_fissions_per_run": 50,
    "dust_threshold": 40,  # Minimum lines for a module to exist (Span-of-Two)
}

# ============================================================================
# CORE SUBFOLDER MAPS
# ============================================================================
CORE_SUBFOLDER_MAP: dict = {
    "L0_routing": ["scripts", "logs", "benchmarks", "mixins"],
    "L1_cognition": ["thought_engine", "intent_analysis", "planning"],
    "L2_execution": ["tool_registry", "action_handlers", "mcp", "tool_registry"],
    "L3_orchestration": [
        "workflow_engines",
        "fission_logic",
        "S3_vitality",
        "mcp",
        "meta_learning",
        "interfaces",
    ],
    "L4_state": ["ValidationContext", "ledger", "filesystem", "memory", "validation_context"],
    "L5_safety": [
        "guardrails",
        "red_teaming",
        "gravity",
        "validators",
        "agents",
        "bases",
        "policies",
        "utils",
        "verifiability",
    ],
    "L6_observability": [
        "dashboards",
        "reports",
        "metrics",
        "telemetry",
        "tracing",
        "compliance",
        "agents",
    ],
    # DISSOLVED: "schemas" removed — deported to runtime/types, L4/contracts, L6/engine+types
    "config": ["core", "environments", "feature_flags", "secrets_manager"],
    "prompt_governance": ["meta_prompts", "version_registry", "rendering", "templates"],
    "runtime": ["shared_runtime", "environment_setup", "shared", "resource_management"],
    "utils": ["core_extensions", "wrappers", "general_helpers", "naming", "deduplicated"],
    "patterns": ["agent_roles", "communication_flow", "interaction_patterns", "reasoning_patterns"],
    "semantic_memory": ["store", "embeddings", "retrieval", "index"],
    "knowledge": ["document_loaders", "static_index", "ResearchCache"],
}

# ============================================================================
# VARIABLE DEPTH SUBFOLDERS
# ============================================================================
# These subfolders are exempt from strict depth enforcement.
VARIABLE_DEPTH_SUBFOLDERS: frozenset = frozenset(
    {
        "utils",
        "config",
        "common",
        "observability",
        "L6_observability",
        "L3_orchestration",
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L4_state",
        "L5_safety",
        "prompt_governance",
        "runtime",
        "patterns",
        "semantic_memory",
        "knowledge",
    },
)

# ============================================================================
# L4 APPROVED FOLDERS (Depth-4 Structure)
# ============================================================================
L4_APPROVED_FOLDERS: set = {
    "agentic_core/L6_observability/dashboards",
    "agentic_core/L0_routing/scripts",
    "agentic_core/L3_orchestration/reasoning",
    "agentic_core/L1_cognition/thought_engine",
    "agentic_core/L5_safety/enforcement",
    "agentic_core/L5_safety/validators",
    "agentic_core/L2_execution/reasoning",
    "agentic_core/L2_execution/enforcement",
    "agentic_core/L4_state/memory",
    # DISSOLVED: "agentic_core/schemas/models" removed
    "agentic_core/utils/core_extensions",
    "agentic_core/config/core",  # DISSOLVED: was blueprint_sovereign
}

# ============================================================================
# GRAVITY CONFIGURATION
# ============================================================================
GRAVITY_CONFIG: dict = {
    "enabled": True,
    "UPSTREAM_SOVEREIGN_ROOTS": ["agentic_core"],
    "downstream_domains": ["apps_rg", "apps_lic", "apps_shared", "tests"],
    "exemptions": [],
}

# ============================================================================
# MISSION CONFIGURATION
# ============================================================================
MISSION_CONFIG: dict = {
    "GRAVITY_SURGERY_ENABLED": True,
    "hierarchy_healing_enabled": True,
    "span_surgery_enabled": True,
    "fission_enabled": True,
    "run_full_mission": True,
    "run_hierarchy_healing": True,
    "run_gravity_refactor": True,
    "run_sprawl_surgery": True,
    "structural_only_mode": False,
    "timeout_seconds": int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800")),
}

# ============================================================================
# AGENT RESILIENCE CONFIGURATION
# ============================================================================
AGENT_RESILIENCE_CONFIG: dict = {
    "retry_count": int(os.getenv("AGENT_RETRY_COUNT", "3")),
    "backoff_base": float(os.getenv("AGENT_RETRY_BACKOFF_BASE", "0.5")),
}

# ============================================================================
# MCP CAPABILITIES
# ============================================================================
MCP_CAPABILITIES: dict = {
    "router": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "marketplace_filter": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "filesystem": {"enabled": True, "path": "agentic_core.L4_state.filesystem"},
    "figma": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "fetch": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "semantic_cache": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
}

# ============================================================================
# LAYER DIRECTORIES MAPPING
# ============================================================================
LAYER_DIRS: dict = {
    "L0": "L0_routing",
    "L1": "L1_cognition",
    "L2": "L2_execution",
    "L3": "L3_orchestration",
    "L4": "L4_state",
    "L5": "L5_safety",
    "L6": "L6_observability",
}

# ============================================================================
# L2 TO L1 REVERSE MAPPING
# ============================================================================
L2_TO_L1_MAP: dict = {
    "thought_engine": "L1_cognition",
    "intent_analysis": "L1_cognition",
    "planning": "L1_cognition",
    "tool_registry": "L2_execution",
    "action_handlers": "L2_execution",
    "mcp": "L2_execution",
    "workflow_engines": "L3_orchestration",
    "fission_logic": "L3_orchestration",
    "meta_learning": "L3_orchestration",
    "S3_vitality": "L3_orchestration",
    "ValidationContext": "L4_state",
    "ledger": "L4_state",
    "memory": "L4_state",
    "filesystem": "L4_state",
    "guardrails": "L5_safety",
    "validators": "L5_safety",
    "gravity": "L5_safety",
    "red_teaming": "L5_safety",
    "core_extensions": "utils",
    "naming": "utils",
    "wrappers": "utils",
    "general_helpers": "utils",
    "metrics": "observability",
    "tracing": "observability",
    "telemetry": "observability",
    "compliance": "observability",
    "models": "runtime",
    "messages": "runtime",
    "types": "runtime",
    "templates": "prompt_governance",
    "meta_prompts": "prompt_governance",
    "rendering": "prompt_governance",
    "version_registry": "prompt_governance",
    "environments": "config",
    "feature_flags": "config",
    "scripts": "L0_routing",
    "logs": "L0_routing",
    "benchmarks": "L0_routing",
}

__all__ = [
    "SOVEREIGN_REGISTRY",
    "HEALING_CONFIG",
    "CORE_SUBFOLDER_MAP",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "L4_APPROVED_FOLDERS",
    "GRAVITY_CONFIG",
    "MISSION_CONFIG",
    "AGENT_RESILIENCE_CONFIG",
    "MCP_CAPABILITIES",
    "LAYER_DIRS",
    "L2_TO_L1_MAP",
]
