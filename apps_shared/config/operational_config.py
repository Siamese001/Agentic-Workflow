"""
Operational configuration for Runtime Agents
Centralized settings for file scanning, deduplication, and operational tasks.

This is separate from structure_blueprint.py which defines compliance rules.
This config is for OPERATIONAL agents that need to know what to scan/exclude.
"""

# ============================================================================
# DIRECTORY EXCLUSIONS - What operational agents should NEVER touch
# ============================================================================

OPERATIONAL_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        # Version control
        ".git",
        # Python environments and caches
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        "venv",
        ".venv",
        "venv_stable",
        "env",
        # Build artifacts
        "dist",
        "build",
        "_build",
        "*.egg-info",
        # IDE and editor
        ".idea",
        ".vscode",
        ".DS_Store",
        "Thumbs.db",
        # Node/JavaScript
        "node_modules",
        # Archives and legacy (NEVER TOUCH)
        "archives",
        "legacy_code",
        "legacy_engines",
        "legacy_resume_gen",
        # Data and logs
        "data",
        "logs",
        "output",
        "chroma_db",
        # Temporary and backup
        ".workflow_state",
        ".sovereign_healing_backup",
        "temp",
        "tmp",
    }
)


# ============================================================================
# SCAN TARGETS - Directories that operational agents SHOULD scan
# ============================================================================

OPERATIONAL_SCAN_TARGETS: list[str] = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "tests",  # Include tests for deduplication
]


# ============================================================================
# ALLOWED DUPLICATES - Files legitimately duplicated across directories
# ============================================================================

OPERATIONAL_ALLOWED_DUPLICATES: frozenset[str] = frozenset(
    {
        # Python package infrastructure (required in every package)
        "__init__.py",
        "__main__.py",
        # Testing infrastructure (pytest requires these)
        "conftest.py",
        # configuration files (can exist per-module)
        "config.py",
        "settings.py",
        # Common base classes (legitimately duplicated)
        "base.py",
        "types.py",
    }
)


# ============================================================================
# FILE EXTENSIONS - What file types to scan
# ============================================================================

OPERATIONAL_PYTHON_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".py",
    }
)

OPERATIONAL_CONFIG_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".json",
        ".yaml",
        ".yml",
        ".toml",
    }
)

OPERATIONAL_ALL_EXTENSIONS: frozenset[str] = (
    OPERATIONAL_PYTHON_EXTENSIONS | OPERATIONAL_CONFIG_EXTENSIONS
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def is_excluded_path(path_str: str) -> bool:
    """
    Check if a path should be excluded from operational scanning.

    Args:
        path_str: String representation of path

    Returns:
        True if path should be excluded
    """
    path_lower = path_str.lower().replace("\\", "/")

    for excluded in OPERATIONAL_EXCLUDED_DIRS:
        if f"/{excluded}/" in path_lower or path_lower.startswith(f"{excluded}/"):
            return True

    return False


def is_allowed_duplicate(filename: str) -> bool:
    """
    Check if a filename is allowed to exist in multiple directories.

    Args:
        filename: Name of the file

    Returns:
        True if file is allowed to be duplicated
    """
    return filename in OPERATIONAL_ALLOWED_DUPLICATES


def should_scan_directory(dir_name: str) -> bool:
    """
    Check if a directory should be scanned by operational agents.

    Args:
        dir_name: Name of the directory

    Returns:
        True if directory should be scanned
    """
    return dir_name in OPERATIONAL_SCAN_TARGETS


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "OPERATIONAL_EXCLUDED_DIRS",
    "OPERATIONAL_SCAN_TARGETS",
    "OPERATIONAL_ALLOWED_DUPLICATES",
    "OPERATIONAL_PYTHON_EXTENSIONS",
    "OPERATIONAL_CONFIG_EXTENSIONS",
    "OPERATIONAL_ALL_EXTENSIONS",
    "is_excluded_path",
    "is_allowed_duplicate",
    "should_scan_directory",
]
