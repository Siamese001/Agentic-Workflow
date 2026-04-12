"""
Blueprint Compiler: Derives all secondary registries from SOVEREIGN_TERRITORIES.

This module eliminates duplication by computing CORE_SUBFOLDER_MAP, SUBFOLDER_METADATA,
APPS_*_SUBFOLDER_MAP, L4_SUBFOLDER_MAP, L4_APPROVED_FOLDERS, and VARIABLE_DEPTH_SUBFOLDERS
from the single SSOT: SOVEREIGN_TERRITORIES.

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Usage:
    from agentic_core.L5_safety.config.blueprint_compiler import compile_blueprint
    compiled = compile_blueprint(SOVEREIGN_TERRITORIES)
    CORE_SUBFOLDER_MAP = compiled.core_subfolder_map
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

from agentic_core.L0_routing.config import (
    DASHBOARD_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TOOLS_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "blueprint_compiler")
# Standard LCD subfolders for L0-L6 layers
STANDARD_LCD_SUBFOLDERS: Final[tuple[str, ...]] = (
    "config",
    "types",
    "reasoning",
    "enforcement",
    "validators",
    "utils",
)


@dataclass(frozen=True)
class CompiledBlueprint:
    """Immutable compiled blueprint derived from SOVEREIGN_TERRITORIES."""

    core_subfolder_map: Mapping[str, Sequence[str]]
    subfolder_metadata: Mapping[str, Mapping[str, Any]]
    apps_rg_subfolder_map: Mapping[str, Sequence[str]]
    apps_lic_subfolder_map: Mapping[str, Sequence[str]]
    apps_shared_subfolder_map: Mapping[str, Sequence[str]]
    l4_subfolder_map: Mapping[str, Mapping[str, Sequence[str]]]
    l4_approved_folders: frozenset[str]
    variable_depth_subfolders: frozenset[str]
    layer_subfolder_lists: Mapping[str, Sequence[str]]


def make_lcd_layer(
    layer_name: str,
    purpose: str,
    extras: Sequence[str] | None = None,
    forbidden_capabilities: Sequence[str] | None = None,
    notes: str | None = None,
) -> Mapping[str, Any]:
    """
    Generate a standard LCD layer definition with optional extras.

    Args:
        layer_name: e.g., "L0_routing"
        purpose: Layer purpose description
        extras: Additional subfolders beyond the standard 6 (e.g., ["scripts"])
        forbidden_capabilities: Capabilities this layer must not have
        notes: Additional notes

    Returns:
        Layer definition dict suitable for SOVEREIGN_TERRITORIES
    """
    subfolders = {}
    for sf in STANDARD_LCD_SUBFOLDERS:
        subfolders[sf] = {"purpose": f"{layer_name} {sf}"}

    if extras:
        for extra in extras:
            subfolders[extra] = {"purpose": f"{layer_name} {extra} (nuance)"}

    result: dict[str, Any] = {
        "purpose": purpose,
        "subfolders": subfolders,
    }

    if forbidden_capabilities:
        result["forbidden_capabilities"] = list(forbidden_capabilities)
    if notes:
        result["notes"] = notes

    return result


def _extract_subfolder_names(subfolders: Any) -> list[str]:
    """Extract subfolder names from various formats in SOVEREIGN_TERRITORIES."""
    if isinstance(subfolders, dict):
        return list(subfolders.keys())
    if isinstance(subfolders, (list, tuple)):
        return list(subfolders)
    return []


def _extract_nested_subfolders(subfolders: Any) -> Mapping[str, Sequence[str]]:
    """Extract nested subfolder structure for apps/tests."""
    result: dict[str, list[str]] = {}
    if isinstance(subfolders, dict):
        for name, value in subfolders.items():
            if isinstance(value, dict) and "subfolders" in value:
                result[name] = _extract_subfolder_names(value["subfolders"])
            elif isinstance(value, (list, tuple)):
                result[name] = list(value)
            else:
                result[name] = []
    return result


def _build_subfolder_metadata(territory_name: str, territory_def: Mapping[str, Any]) -> Mapping[str, Any]:
    """Build metadata entry for a territory."""
    purpose = territory_def.get("purpose", f"{territory_name} domain")
    notes = territory_def.get("notes", "")
    execution_allowed = territory_def.get("execution_allowed", False)

    # Infer content_types from subfolders if not explicit
    subfolders = territory_def.get("subfolders", {})
    content_types = []
    if isinstance(subfolders, dict):
        for sf_name, sf_def in subfolders.items():
            if isinstance(sf_def, dict):
                content_types.append(sf_def.get("purpose", sf_name))

    return {
        "purpose": purpose,
        "content_types": content_types or [territory_name],
        "execution_allowed": execution_allowed,
        "notes": notes,
    }


def _identify_l4_folders(
    territories: Mapping[str, Any],
) -> tuple[Mapping[str, Mapping[str, Sequence[str]]], frozenset[str]]:
    """Identify L4-depth folders and their specializations."""
    l4_map: dict[str, dict[str, list[str]]] = {}
    l4_approved: set[str] = set()

    # Known L4 folders from territory definitions
    l4_indicators = ("l4_specializations", "l4_depth", "depth_4")

    for territory_name, territory_def in territories.items():
        if not isinstance(territory_def, dict):
            continue

        subfolders = territory_def.get("subfolders", {})
        if not isinstance(subfolders, dict):
            continue

        for sf_name, sf_def in subfolders.items():
            if not isinstance(sf_def, dict):
                continue

            # Check for L4 indicators
            if any(ind in sf_def for ind in l4_indicators):
                folder_path = f"agentic_core/{territory_name}/{sf_name}"
                l4_approved.add(folder_path)

                specs = sf_def.get("l4_specializations", {})
                if specs:
                    l4_map[sf_name] = dict(specs)

    # Add known L4 folders from layer nuances
    known_l4 = [
        DASHBOARD_DIR,
        "agentic_core/L0_routing/scripts",
        "agentic_core/L0_routing/reasoning",
        "agentic_core/L3_orchestration/reasoning",
    ]
    for path in known_l4:
        l4_approved.add(path)

    return l4_map, frozenset(l4_approved)


def _identify_variable_depth_subfolders(territories: Mapping[str, Any]) -> frozenset[str]:
    """Identify subfolders that allow variable depth."""
    variable_depth: set[str] = set()

    # Standard LCD subfolders always allow variable depth
    variable_depth.update(STANDARD_LCD_SUBFOLDERS)

    # Add layer roots
    for territory_name in territories:
        if territory_name.startswith("L") and "_" in territory_name:
            variable_depth.add(territory_name)

    # Add known variable-depth folders
    known_variable = [
        "scripts",
        TOOLS_DIR,
        "memory",
        "dashboards",
        "base_agents",
        "prompt_governance",
        "knowledge",
        "runtime",
    ]
    variable_depth.update(known_variable)

    return frozenset(variable_depth)


def compile_blueprint(territories: Mapping[str, Any]) -> CompiledBlueprint:
    """
    Compile SOVEREIGN_TERRITORIES into all derived registries.

    This is the core function that eliminates duplication by deriving
    CORE_SUBFOLDER_MAP, SUBFOLDER_METADATA, and other registries from
    the single SSOT.

    Args:
        territories: The SOVEREIGN_TERRITORIES mapping

    Returns:
        CompiledBlueprint with all derived registries
    """
    core_subfolder_map: dict[str, list[str]] = {}
    subfolder_metadata: dict[str, dict[str, Any]] = {}
    layer_subfolder_lists: dict[str, list[str]] = {}

    # Apps subfolder maps
    apps_rg_map: dict[str, list[str]] = {}
    apps_lic_map: dict[str, list[str]] = {}
    apps_shared_map: dict[str, list[str]] = {}

    for territory_name, territory_def in territories.items():
        if not isinstance(territory_def, dict):
            continue

        subfolders = territory_def.get("subfolders", {})

        # Build core_subfolder_map for agentic_core territories
        if territory_name == AGENTIC_CORE_DIR:
            # Process agentic_core's nested structure
            for domain_name, domain_def in subfolders.items():
                if isinstance(domain_def, dict):
                    nested_sfs = domain_def.get("subfolders", {})
                    core_subfolder_map[domain_name] = _extract_subfolder_names(nested_sfs)

                    # Build metadata
                    subfolder_metadata[domain_name] = _build_subfolder_metadata(domain_name, domain_def)

                    # Track layer subfolder lists
                    if domain_name.startswith("L") and "_" in domain_name:
                        layer_subfolder_lists[domain_name] = core_subfolder_map[domain_name]
                else:
                    core_subfolder_map[domain_name] = []

        elif territory_name == APPS_RG_DIR:
            apps_rg_map = dict(_extract_nested_subfolders(subfolders))

        elif territory_name == APPS_LIC_DIR:
            apps_lic_map = dict(_extract_nested_subfolders(subfolders))

        elif territory_name == APPS_SHARED_DIR:
            apps_shared_map = dict(_extract_nested_subfolders(subfolders))

    # Derive L4 structures
    l4_map, l4_approved = _identify_l4_folders(territories)

    # Derive variable depth subfolders
    variable_depth = _identify_variable_depth_subfolders(territories)

    return CompiledBlueprint(
        core_subfolder_map=core_subfolder_map,
        subfolder_metadata=subfolder_metadata,
        apps_rg_subfolder_map=apps_rg_map,
        apps_lic_subfolder_map=apps_lic_map,
        apps_shared_subfolder_map=apps_shared_map,
        l4_subfolder_map=l4_map,
        l4_approved_folders=l4_approved,
        variable_depth_subfolders=variable_depth,
        layer_subfolder_lists=layer_subfolder_lists,
    )


def verify_blueprint_consistency(
    compiled: CompiledBlueprint,
    legacy_core_map: Mapping[str, Sequence[str]] | None = None,
    legacy_metadata: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[str]:
    """
    Verify that compiled blueprint matches legacy registries.

    Returns list of discrepancies (empty if consistent).
    """
    discrepancies: list[str] = []

    if legacy_core_map:
        for key in legacy_core_map:
            if key not in compiled.core_subfolder_map:
                discrepancies.append(f"Missing in compiled: {key}")
            elif set(legacy_core_map[key]) != set(compiled.core_subfolder_map.get(key, [])):
                discrepancies.append(
                    f"Mismatch for {key}: legacy={list(legacy_core_map[key])}, "
                    f"compiled={list(compiled.core_subfolder_map.get(key, []))}",
                )

    if legacy_metadata:
        for key in legacy_metadata:
            if key not in compiled.subfolder_metadata:
                discrepancies.append(f"Missing metadata in compiled: {key}")

    return discrepancies
