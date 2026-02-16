from __future__ import annotations

# mission_utils_util.py
# L0 Utility Functions for Canon Validator Mission
# PURPOSE: Provides helper functions for dynamic imports, layer ranking, and L2 lookups
# LOCATION: agentic_core/utils/general_helpers/ (SSOT-compliant)
import importlib
from typing import Any

# Import SSOT registries
from agentic_core.L5_safety.config.structure_blueprint_config import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    SOVEREIGN_TERRITORIES,
)


def dynamic_import(module_path: str, class_name: str) -> Any | None:
    """
    Dynamically import classes to avoid gravity violations.

    Args:
        module_path: Dotted module path (e.g., 'agentic_core.L5_safety.enforcement.SafetyGuardrail')
        class_name: Name of the class to import

    Returns:
        The imported class, or None if import fails
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None


def get_layer_rank(path_str: str) -> int:
    """
    Get the authority rank of a layer based on its position in the SSOT registry.
    Lower index = higher authority.

    Args:
        path_str: File path string to check

    Returns:
        Layer rank (0-based index), or -1 if not found
    """
    gravity_layers = SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]
    for i, layer in enumerate(gravity_layers):
        if layer in path_str:
            return i
    return -1


def get_legal_l2_for_l1(root: str, l1_name: str) -> list[str]:
    """
    Pull valid L2 folders directly from imported SSOT maps.

    Args:
        root: Root territory name (agentic_core, apps_rg, apps_lic, apps_shared)
        l1_name: L1 folder name

    Returns:
        List of approved L2 subfolder names
    """
    if root == "agentic_core":
        return CORE_SUBFOLDER_MAP.get(l1_name, [])
    elif root == "apps_rg":
        return APPS_RG_SUBFOLDER_MAP.get(l1_name, [])
    elif root == "apps_lic":
        return APPS_LIC_SUBFOLDER_MAP.get(l1_name, [])
    elif root == "apps_shared":
        return APPS_SHARED_SUBFOLDER_MAP.get(l1_name, [])
    return []


def get_placement_guidance(content_preview: str) -> str:
    """
    Heuristically determine the best L1 placement for code based on content signals.

    Args:
        content_preview: First ~500 chars of file content

    Returns:
        Suggested L1 path (e.g., 'agentic_core/L1_cognition')
    """
    content_lower = content_preview.lower()

    if any(x in content_lower for x in ["planner", "strategy", "reasoning", "mission"]):
        return "agentic_core/L1_cognition"
    if "node" in content_lower or "execute" in content_lower:
        return "agentic_core/L1_cognition/thought_engine"
    if any(x in content_lower for x in ["router", "orchestrator", "fission", "hop"]):
        return "agentic_core/L3_orchestration"
    if any(x in content_lower for x in ["pinecone", "redis", "storage", "cache"]):
        return "agentic_core/L4_state"
    if any(x in content_lower for x in ["safety", "guardrail", "guard", "validator"]):
        return "agentic_core/L5_safety"
    if any(x in content_lower for x in ["Metric", "telemetry", "trace", "observ"]):
        return "agentic_core/observability"
    if any(x in content_lower for x in ["prompt", "persona", "instruct"]):
        return "agentic_core/prompt_governance"
    if any(x in content_lower for x in ["schema", "model", "request", "response"]):
        return "agentic_core/runtime/types"

    # Default fallback
    return "agentic_core/L1_cognition"


def get_best_target_l1(folder_name: str, approved_l1: set) -> str:
    """
    Heuristically determine the best approved L1 folder for a non-approved folder.

    Args:
        folder_name: Name of the folder to relocate
        approved_l1: Set of approved L1 folder names

    Returns:
        Best matching approved L1 folder name
    """
    name_lower = folder_name.lower()

    # Mapping based on common patterns
    if any(x in name_lower for x in ["cognit", "thought", "reason", "intent", "strateg"]):
        return "L1_cognition"
    if any(x in name_lower for x in ["exec", "action", "tool", "handler"]):
        return "L2_execution"
    if any(x in name_lower for x in ["orchestr", "workflow", "fission", "Route", "hop"]):
        return "L3_orchestration"
    if any(x in name_lower for x in ["state", "memory", "cache", "audit", "ledger", "context"]):
        return "L4_state"
    if any(x in name_lower for x in ["safe", "guard", "policy", "red_team", "gravity"]):
        return "L5_safety"
    if any(x in name_lower for x in ["maint", "script", "log", "bench"]):
        return "L0_routing"
    if any(x in name_lower for x in ["config", "env", "setting"]):
        return "config"
    if any(x in name_lower for x in ["schema", "model", "request", "response"]):
        return "schemas"
    if any(x in name_lower for x in ["prompt", "persona", "instruct"]):
        return "prompt_governance"
    if any(x in name_lower for x in ["runtime", "shared"]):
        return "runtime"
    if any(x in name_lower for x in ["observ", "Metric", "telemetry"]):
        return "observability"
    if any(x in name_lower for x in ["util", "helper", "extension"]):
        return "utils"
    if any(x in name_lower for x in ["pattern", "role", "flow"]):
        return "patterns"
    if any(x in name_lower for x in ["semantic", "vector", "embed"]):
        return "semantic_memory"
    if any(x in name_lower for x in ["knowledge", "rag", "document", "research"]):
        return "knowledge"

    # Default fallback
    return "utils"


def get_best_target_l2(l1_name: str, item_name: str) -> str:
    """
    Heuristically determine the best approved L2 folder within an L1.

    Args:
        l1_name: L1 folder name
        item_name: Name of file/folder to place

    Returns:
        Best matching L2 folder name
    """
    approved_l2 = CORE_SUBFOLDER_MAP.get(l1_name, [])
    if not approved_l2:
        return "workflow_engines"  # Fallback default

    name_lower = item_name.lower()

    # Try to match based on name patterns
    for l2 in approved_l2:
        if l2.lower() in name_lower or name_lower in l2.lower():
            return l2

    # Return first approved L2 as fallback
    return approved_l2[0]
