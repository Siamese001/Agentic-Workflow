"""
Territories Module — New Territory API (replaces SOVEREIGN_TERRITORIES).

This module provides the canonical API for accessing territory metadata:
- get_territory_metadata(name) — Get metadata for a specific territory
- get_all_territories() — Get all territory definitions (read-only)
- is_valid_root_folder(name) — Check if folder is allowed at project root

Note: SOVEREIGN_TERRITORIES and build_sovereign_territories() are no longer
exported. Use the functions above instead. Internal code can still access
SOVEREIGN_TERRITORIES via _constants if absolutely necessary.
"""

from __future__ import annotations

from collections.abc import Mapping

from agentic_core.L5_safety.config.structure_blueprint._constants import (
    SOVEREIGN_TERRITORIES,  # Internal use only - not re-exported
    SubfolderDefinition,  # noqa: F401
    TerritoryDefinition,  # noqa: F401
)


def get_territory_metadata(territory_name: str) -> TerritoryDefinition | None:
    """Get metadata for a specific territory.

    Args:
        territory_name: Name of the territory (e.g., "apps_shared", "agentic_core")

    Returns:
        Territory definition dict with keys like 'purpose', 'subfolders', 'depth', etc.
        Returns None if territory not found.

    Example:
        >>> meta = get_territory_metadata("apps_shared")
        >>> if meta:
        ...     print(meta.get("purpose"))
    """
    return SOVEREIGN_TERRITORIES.get(territory_name)


def get_all_territories() -> Mapping[str, TerritoryDefinition]:
    """Get all territory definitions (read-only).

    Returns:
        Immutable mapping of territory_name -> TerritoryDefinition.
        This is a read-only view — mutations will raise TypeError.

    Example:
        >>> territories = get_all_territories()
        >>> for name, meta in territories.items():
        ...     print(f"{name}: {meta.get('purpose')}")
    """
    return SOVEREIGN_TERRITORIES


def is_valid_root_folder(folder_name: str) -> bool:
    """Check if folder is allowed at project root.

    Args:
        folder_name: Name of the folder to check (e.g., "apps_shared", ".git")

    Returns:
        True if folder is in the project root whitelist, False otherwise.

    Example:
        >>> is_valid_root_folder("apps_shared")
        True
        >>> is_valid_root_folder("random_folder")
        False
    """
    # Import locally to avoid circular dependency (ssot imports from territories)
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        PROJECT_ROOT_WHITELIST,
    )

    return folder_name in PROJECT_ROOT_WHITELIST
