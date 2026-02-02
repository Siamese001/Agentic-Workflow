from __future__ import annotations

"""
Shared utility functions for location-based operations.

Extracted from LocationAgent.py during SRP fission.
All location-related agents should import from this module.
"""


import os
from pathlib import Path


def normalize_location_path(path: str) -> str:
    """
    Standardizes path formatting for comparison.

    Args:
        path: Path string to normalize

    Returns:
        Normalized path with forward slashes
    """
    return os.path.normpath(path).replace("\\", "/")


def get_agent_files(root_dir: str) -> list[str]:
    """
    Discovers all .py files within the agentic_core structure.

    Args:
        root_dir: Root directory to search

    Returns:
        List of Python file paths
    """
    agent_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                agent_files.append(os.path.join(root, file))
    return agent_files


def compute_module_path(file_path: Path, project_root: Path | None = None) -> str:
    """
    Compute Python module path from file path.

    Args:
        file_path: Path to Python file
        project_root: Optional project root (auto-detected if None)

    Returns:
        Module path string (e.g., 'agentic_core.L5_safety.validators.LocationAgent')
    """
    if project_root is None:
        from agentic_core.L5_safety.validators.structure_blueprint_config import get_validated_project_root

        project_root = get_validated_project_root()

    try:
        rel_path = file_path.relative_to(project_root)
        module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        return ".".join(module_parts)
    except ValueError:
        # File not within project root
        return file_path.stem


def is_path_compliant(file_path: str | Path, project_root: Path | None = None) -> bool:
    r"""
    L5 Sovereign Structural SSOT - Hard-enforcement of path validity.

    This is the Supreme Court for structural compliance. All L3 and L2 agents
    that need to validate file paths MUST call this function instead of
    implementing their own path validation logic.

    Enforces:
    1. Path must be within project root
    2. Root folder must be in SOVEREIGN_TERRITORIES (whitelist)
    3. Depth must not exceed MAX_ALLOWED_DEPTH per root
    4. No forbidden root folders (legacy_*, old_*)
    5. No numbered folder prefixes (^\d+_)

    Args:
        file_path: Path to validate (str or Path)
        project_root: Optional project root (auto-detected if None)

    Returns:
        True if path is structurally compliant, False otherwise

    Example:
        >>> is_path_compliant('agentic_core/L5_safety/validators/LocationAgent.py')
        True
        >>> is_path_compliant('legacy_code/old_agent.py')
        False
        >>> is_path_compliant('agentic_core/L1/L2/L3/L4/L5/deep.py')  # Too deep
        False
    """
    from agentic_core.L5_safety.validators.structure_blueprint_config import (
        FORBIDDEN_FOLDER_PATTERN,
        FORBIDDEN_ROOT_FOLDERS,
        ROOT_WHITELIST,
        SOVEREIGN_TERRITORIES,
        get_validated_project_root,
    )

    # Auto-detect project root if not provided
    if project_root is None:
        project_root = get_validated_project_root()

    # Convert to Path object
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Ensure absolute path
    if not file_path.is_absolute():
        file_path = project_root / file_path

    # Check if path is within project
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        return False  # Path not within project

    parts = rel_path.parts
    if not parts:
        return False  # Empty path

    root_folder = parts[0]

    # Check 1: Root must be in whitelist
    if root_folder not in ROOT_WHITELIST:
        return False

    # Check 2: No forbidden folders at any depth
    for part in parts:
        if part in FORBIDDEN_ROOT_FOLDERS:
            return False
        if hasattr(FORBIDDEN_FOLDER_PATTERN, "match"):
            if FORBIDDEN_FOLDER_PATTERN.match(part):
                return False

    # Check 3: Numbered root folders forbidden
    if len(root_folder) >= 3 and root_folder[:2].isdigit() and root_folder[2:3] == "_":
        return False

    # Check 4: Depth requirements
    expected_depth = SOVEREIGN_TERRITORIES.get(root_folder, {}).get("depth")
    if expected_depth is not None:
        actual_depth = len(parts) - 1
        if actual_depth != expected_depth:
            # Allow variable depth for certain subfolders
            from agentic_core.L5_safety.validators.structure_blueprint_config import (
                VARIABLE_DEPTH_SUBFOLDERS,
            )

            if root_folder == "agentic_core" and len(parts) > 1:
                subfolder = parts[1]
                if subfolder in VARIABLE_DEPTH_SUBFOLDERS and actual_depth >= 2:
                    return True  # Variable depth allowed
            return False  # Depth violation

    return True
