"""
L0 Path Constants — Pure SSOT for structural paths.

This module contains ONLY stdlib-dependent constants extracted from
L5_safety.config.structure_blueprint for use by L0 modules without
creating upward import violations.

SSOT: These values are canonical. L5 structure_blueprint re-exports
these for backward compatibility.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from re import Pattern
from typing import Any, Final


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ============================================================================
# HEALING TIER THRESHOLDS (Moved from L2 to L0 - L0 can be imported by any layer)
# ============================================================================

# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
HEALING_CONFIDENCE_X: float = 0.80  # Upper threshold: conf > X  → DETERMINISTIC
HEALING_CONFIDENCE_Y: float = 0.50  # Lower threshold: conf <= Y → GEMINI 2.5 Pro

# SSOT score thresholds for integer-score routing (S = 3C+4B+3A+2N+4F)
SSOT_SCORE_THRESHOLD_DET: int = 13  # S <= 13  → DETERMINISTIC
SSOT_SCORE_THRESHOLD_QWEN: int = 26  # S <= 26  → QWEN; S > 26 → GEMINI

# Qwen 14B model identifier
QWEN_14B_MODEL_ID: Final[str] = "qwen/qwen-14b-chat"

# Architecture layer constants - SSOT for layer naming
AGENTIC_CORE_LAYERS: Final[list[str]] = [
    "L0_routing",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
]

# Application package constants - SSOT for app package naming
APPS_PACKAGES: Final[list[str]] = [
    "apps_lic",
    "apps_rg",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_shared",
    "apps_underwriting_ai",
]

# ============================================================================
# PROJECT ROOT DETECTION
# ============================================================================

PROJECT_ROOT_MARKERS: Final[tuple[str, ...]] = (
    ".git",
    "pyproject.toml",
    ".windsurfrules",
)


@lru_cache(maxsize=1)
def get_validated_project_root() -> Path:
    """Return the validated project root directory.

    Walks up from CWD looking for PROJECT_ROOT_MARKERS.
    Caches result for performance.
    """
    current = Path.cwd().resolve()
    for parent in [current, *current.parents]:
        if any((parent / marker).exists() for marker in PROJECT_ROOT_MARKERS):
            return parent
    # Fallback to CWD if no markers found
    return current


# ============================================================================
# DIRECTORY CONSTANTS (relative to project root)
# ============================================================================

AGENTIC_CORE_DIR: Final[str] = "agentic_core"
INFRASTRUCTURE_DIR: Final[str] = "infrastructure"
APPS_EVAL_DIR: Final[str] = "apps_eval"
APPS_EXEC_DIR: Final[str] = "apps_exec"
APPS_LIC_DIR: Final[str] = "apps_lic"
APPS_RESEARCH_DIR: Final[str] = "apps_research"
APPS_RFP_DIR: Final[str] = "apps_rfp"
APPS_RG_DIR: Final[str] = "apps_rg"
APPS_SHARED_DIR: Final[str] = "apps_shared"
ARCHIVES_DIR: Final[str] = "archives"
OPS_SCRIPTS_DIR: Final[str] = "ops_scripts"
SCRIPTS_DIR: Final[str] = "scripts"
SYSTEM_LEARNING_DIR: Final[str] = "system_learning"
TESTS_DIR: Final[str] = "tests"
WINDSURF_SCRIPTS_DIR: Final[str] = ".windsurf/scripts"
TESTS_UNIT_DIR: Final[str] = "tests/unit"
TOOLS_DIR: Final[str] = "tools"
DASHBOARD_DIR: Final[str] = "agentic_core/L6_observability/dashboards"
REPORTS_DIR: Final[str] = "reports"

# ============================================================================
# DYNAMIC DIRECTORY DISCOVERY
# ============================================================================


@lru_cache(maxsize=1)
def get_apps_directories() -> list[str]:
    """Dynamically discover all apps_* directories in the repository.

    Returns:
        List of directory names starting with 'apps_' that exist in the repo.
        Cached for performance.
    """
    project_root = get_validated_project_root()
    apps_dirs = []

    for item in project_root.iterdir():
        if item.is_dir() and item.name.startswith("apps_"):
            apps_dirs.append(item.name)

    # Sort for deterministic ordering
    return sorted(apps_dirs)


@lru_cache(maxsize=1)
def get_all_apps_paths() -> list[Path]:
    """Get absolute paths for all apps_* directories.

    Returns:
        List of Path objects for all apps_* directories.
        Cached for performance.
    """
    project_root = get_validated_project_root()
    apps_dirs = get_apps_directories()
    return [project_root / dir_name for dir_name in apps_dirs]


# Layer-specific directories
L0_MAINTENANCE_DIR: Final[str] = "agentic_core/L0_maintenance"
L0_ROUTING_DIR: Final[str] = "agentic_core/L0_routing"
L1_COGNITION_DIR: Final[str] = "agentic_core/L1_cognition"
L2_EXECUTION_DIR: Final[str] = "agentic_core/L2_execution"
L3_ORCHESTRATION_DIR: Final[str] = "agentic_core/L3_orchestration"
L4_STATE_DIR: Final[str] = "agentic_core/L4_state"
L5_SAFETY_DIR: Final[str] = "agentic_core/L5_safety"
L6_OBSERVABILITY_DIR: Final[str] = "agentic_core/L6_observability"

# ============================================================================
# FILE CONSTANTS
# ============================================================================

AGENT_DISCOVERY_JSON: Final[str] = "agent_discovery.json"
AGENT_DISCOVERY_MANIFEST_JSON: Final[str] = "agent_discovery_manifest.json"
RUNTIME_STATE_JSON: Final[str] = "runtime_state.json"

# ============================================================================
# LAYER ROOTS
# ============================================================================

LAYER_ROOTS: Final[frozenset[str]] = frozenset(
    {
        "L0_routing",
        "L0_maintenance",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    },
)

# ============================================================================
# WHITELISTS
# ============================================================================

ROOT_WHITELIST: Final[frozenset[str]] = frozenset(
    {
        ".backup",
        ".github",
        ".gravity_state",
        "agentic_core",
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rfp",
        "apps_rg",
        "apps_shared",
        "archives",
        "artifacts",
        "data",
        "docs",
        "logs",
        "ops_scripts",
        "system_learning",
        "tests",
        "tools",
    },
)

ROOT_PROTECTED_FILES: Final[frozenset[str]] = frozenset(
    {
        ".gitignore",
        ".gitattributes",
        ".pre-commit-config.yaml",
        ".windsurfrules",
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "MANIFEST.in",
        "LICENSE",
        "README.md",
        "conftest.py",
        "pytest.ini",
        "canon_validator_agentic_v2_thin.py",
    },
)

ROOT_ALLOWED_PATTERNS: Final[tuple[str, ...]] = (
    r"^\..*",  # Hidden files
    r"^[A-Z]+\.md$",  # Uppercase markdown (README, LICENSE, etc.)
    r"^[a-z_]+\.py$",  # Lowercase python files at root
    r"^requirements.*\.txt$",  # Requirements files
)

SOVEREIGN_EXCLUDED_FOLDERS: Final[frozenset[str]] = frozenset(
    {
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "artifacts",
        ".sovereign_healing_backup",
        ".healing_backups",
    },
)

VARIABLE_DEPTH_SUBFOLDERS: Final[frozenset[str]] = frozenset(
    {
        "types",
        "config",
        "unit",
        "unit_min_deps",
        "integration",
    },
)

L4_APPROVED_FOLDERS: Final[frozenset[str]] = frozenset(
    {
        "P1_core",
        "P2_extended",
        "memory",
        "types",
        "config",
        "reasoning",
        "utils",
        "agentic_core/L4_state/memory",  # runtime ADG store: otel_mcp + FileBackedRuntimeADGStore
    },
)

GLOBAL_EXCLUDED_DIRS: Final[frozenset[str]] = frozenset(
    {
        ".git",
        ".github",
        ".venv",
        ".windsurf",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        "venv",
        "build",
        "dist",
        "htmlcov",
        ".tox",
        ".nox",
        "eggs",
        "*.egg-info",
    },
)

DISCOVERY_EXCLUDED_TERRITORIES: Final[frozenset[str]] = frozenset(
    {"runtime_shared", "legacy_code", "legacy_engines", "archives", "stubs", "examples"},
)

# ============================================================================
# STRUCTURAL DEPTH RULES (literal copy from L5 derived.py)
# Source: agentic_core.L5_safety.config.structure_blueprint.derived.DEPTH_RULES
# ============================================================================

DEPTH_RULES: Final[Mapping[str, int]] = {
    ".backup": 2,
    ".github": 2,
    ".gravity_state": 2,
    "agentic_core": 3,
    "apps_eval": 2,
    "apps_exec": 2,
    "apps_lic": 2,
    "apps_research": 2,
    "apps_rfp": 2,
    "apps_rg": 2,
    "apps_shared": 2,
    "archives": 3,
    "artifacts": 2,
    "data": 3,
    "docs": 3,
    "logs": 2,
    "ops_scripts": 2,
    "system_learning": 2,
    "tests": 2,
    "tools": 2,
}

# ============================================================================
# PROJECT ROOT WHITELIST (literal copy from L5 ssot.py)
# Source: agentic_core.L5_safety.config.structure_blueprint.ssot.PROJECT_ROOT_WHITELIST
# ============================================================================

PROJECT_ROOT_WHITELIST: Final[frozenset[str]] = frozenset(
    {
        ".backup",
        ".git",
        ".github",
        ".gravity_state",
        ".vscode",
        "agentic_core",
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rfp",
        "apps_rg",
        "apps_shared",
        "archives",
        "data",
        "docs",
        "ops_scripts",
        "tests",
    },
)

# ============================================================================
# SUBFOLDER MAPS (literal copy from L5 derived.py)
# Source: agentic_core.L5_safety.config.structure_blueprint.derived.*_SUBFOLDER_MAP
# ============================================================================

CORE_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "L0_routing": [],
    "L1_cognition": [],
    "L2_execution": [],
    "L3_orchestration": [],
    "L4_state": [],
    "L5_safety": [],
    "L6_observability": [],
    "_compat": [],
    "adg": [],
    "agents": [],
    "base_agents": [],
    "cache": [],
    "config": [],
    "enforcement": [],
    "evaluation": [],
    "interfaces": [],
    "knowledge": [],
    "mixins": [],
    "prompt_governance": [],
    "runtime": [],
    "seams": [],
    "utils": [],
}

APPS_RG_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "config": [],
    "domain": ["entities", "models", "value_objects"],
    "enforcement": [],
    "engines": [],
    "reasoning": [],
    "scripts": [],
    "tools": [],
    "types": [],
    "utils": [],
    "validators": [],
}

APPS_LIC_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "config": [],
    "domain": ["config", "utils", "models"],
    "enforcement": [],
    "engines": [],
    "reasoning": [],
    "scripts": [],
    "tools": [],
    "types": [],
    "utils": [],
    "validators": [],
}

APPS_SHARED_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "agents": [],
    "config": [],
    "core_components": [],
    "data": [],
    "enforcement": [],
    "integration": [],
    "llm": [],
    "mixins": [],
    "reasoning": [],
    "scripts": [],
    "spine": [],
    "tools": [],
    "types": [],
    "utils": [],
    "validators": [],
}

APPS_EVAL_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "config": [],
    "engines": [],
    "enforcement": [],
    "reasoning": [],
    "scripts": [],
    "tools": [],
    "types": [],
    "utils": [],
    "validators": [],
}

APPS_EXEC_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "config": [],
    "engines": [],
    "enforcement": [],
    "reasoning": [],
    "scripts": [],
    "tools": [],
    "types": [],
    "utils": [],
    "validators": [],
}

APPS_RESEARCH_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "config": [],
    "engines": [],
    "enforcement": [],
    "reasoning": [],
    "scripts": [],
    "tools": [],
    "types": [],
    "utils": [],
    "validators": [],
}

APPS_RFP_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "config": [],
    "engines": [],
    "enforcement": [],
    "reasoning": [],
    "scripts": [],
    "tools": [],
    "types": [],
    "utils": [],
    "validators": [],
}

# ============================================================================
# ALLOWED DUPLICATE FILENAMES (migrated from L5 structure_blueprint)
# ============================================================================
# Files permitted to exist with the same name across multiple directories.
ALLOWED_DUPLICATE_FILENAMES: frozenset[str] = frozenset(
    {
        "__init__.py",
        "__main__.py",
        "conftest.py",
        "context.py",
        "config.py",
        "constants.py",
        "exceptions.py",
        "types.py",
        "models.py",
        "base.py",
        "utils.py",
        "helpers.py",
        "common.py",
        "observability.py",
        "metrics.py",
        "logging.py",
        "tracing.py",
        "proactive.py",
        "autonomous.py",
        "self_healing.py",
        "prompts.py",
        "templates.py",
    },
)

# ============================================================================
# FLAT DIRECTORIES (migrated from L5 structure_blueprint)
# ============================================================================
# Directories marked flat: files MUST live directly in them — no subdirectories.
FLAT_DIRECTORIES: Final[frozenset[str]] = frozenset(
    {
        "cache",
        "config",
        "embeddings",
        "gateway",
        "interfaces",
        "mixins",
        "patterns",
        "planning",
        "base_agents",
    },
)

# ============================================================================
# TERRITORY FLAGS (migrated from L5 structure_blueprint)
# ============================================================================
# Territories that permit a .py file directly at depth-1 (allow_root_py flag).
# Currently empty — no territory has this flag set in YAML.
ALLOW_ROOT_PY_TERRITORIES: Final[frozenset[str]] = frozenset()

# Territories that use L0-L6 prefixes intentionally (layer_prefix_exempt flag).
# Currently empty — no territory has this flag set in YAML.
LAYER_PREFIX_EXEMPT_TERRITORIES: Final[frozenset[str]] = frozenset()

# ============================================================================
# FORBIDDEN PATTERNS (migrated from L5 structure_blueprint)
# ============================================================================
FORBIDDEN_FOLDER_PATTERN: Pattern = re.compile(r"^\d+_")

FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset(
    {"legacy_code", "legacy_engines", "legacy_resume_gen", "old_core"},
)


# ============================================================================
# PATH VALIDATION FUNCTIONS (migrated from L5 structure_blueprint)
# ============================================================================


def validate_path_within_project(path, project_root=None) -> bool:
    """Validate that a path is within the project root."""
    if project_root is None:
        project_root = get_validated_project_root()

    try:
        path = Path(path).resolve()
        project_root = Path(project_root).resolve()
        path.relative_to(project_root)
        return True
    except ValueError:
        return False


def safe_path_join(project_root, *parts) -> Path:
    """Safely join path parts and validate result is within project root."""
    project_root = Path(project_root).resolve()
    result = project_root.joinpath(*parts).resolve()

    if not validate_path_within_project(result, project_root):
        raise ValueError(f"SAFETY VIOLATION: Path '{result}' is outside project root '{project_root}'")

    return result


def validate_flat_directory(path_parts: Sequence[str]) -> dict[str, Any] | None:
    """Detect files nested inside directories that must be flat (no subfolders).

    Args:
        path_parts: tuple/list of path components (e.g. Path.parts).

    Returns:
        None if compliant, or a violation dict with:
        - domain: the flat directory that was violated
        - illegal_child: the subdirectory found inside it
        - message: human-readable explanation
    """
    for i, part in enumerate(path_parts):  # progress_bar: bounded path-parts loop, max ~10 items, no I/O
        if part in FLAT_DIRECTORIES:
            remaining = path_parts[i + 1 :]
            if len(remaining) > 1:
                illegal_child = remaining[0]
                if illegal_child == "__pycache__":
                    return None
                return {
                    "domain": part,
                    "illegal_child": illegal_child,
                    "message": (
                        f"FLAT VIOLATION: '{part}/' must not contain subdirectory "
                        f"'{illegal_child}/'. All files must live directly in '{part}/'."
                    ),
                }
    return None


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "AGENTIC_CORE_DIR",
    "AGENTIC_CORE_LAYERS",
    "ALLOW_ROOT_PY_TERRITORIES",
    "ALLOWED_DUPLICATE_FILENAMES",
    "APPS_EVAL_DIR",
    "APPS_EVAL_SUBFOLDER_MAP",
    "APPS_EXEC_DIR",
    "APPS_EXEC_SUBFOLDER_MAP",
    "APPS_LIC_DIR",
    "APPS_LIC_SUBFOLDER_MAP",
    "APPS_PACKAGES",
    "APPS_RESEARCH_DIR",
    "APPS_RESEARCH_SUBFOLDER_MAP",
    "APPS_RFP_DIR",
    "APPS_RFP_SUBFOLDER_MAP",
    "APPS_RG_DIR",
    "APPS_RG_SUBFOLDER_MAP",
    "APPS_SHARED_DIR",
    "APPS_SHARED_SUBFOLDER_MAP",
    "ARCHIVES_DIR",
    "BATCH_SIZE",
    "BUFFER_SIZE",
    "CORE_SUBFOLDER_MAP",
    "DASHBOARD_DIR",
    "DEFAULT_SLEEP",
    "DEFAULT_TIMEOUT",
    "DEPTH_RULES",
    "FLAT_DIRECTORIES",
    "FORBIDDEN_FOLDER_PATTERN",
    "FORBIDDEN_ROOT_FOLDERS",
    "GLOBAL_EXCLUDED_DIRS",
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "L0_MAINTENANCE_DIR",
    "L0_ROUTING_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L3_ORCHESTRATION_DIR",
    "L4_APPROVED_FOLDERS",
    "L4_STATE_DIR",
    "L5_SAFETY_DIR",
    "L6_OBSERVABILITY_DIR",
    "LAYER_PREFIX_EXEMPT_TERRITORIES",
    "LAYER_ROOTS",
    "MAX_DEPTH",
    "MAX_FILES",
    "MAX_RETRIES",
    "OPS_SCRIPTS_DIR",
    "PROJECT_ROOT_MARKERS",
    "PROJECT_ROOT_WHITELIST",
    "QWEN_14B_MODEL_ID",
    "ROOT_ALLOWED_PATTERNS",
    "ROOT_PROTECTED_FILES",
    "ROOT_WHITELIST",
    "RUNTIME_STATE_JSON",
    "SCRIPTS_DIR",
    "SOVEREIGN_EXCLUDED_FOLDERS",
    "SSOT_SCORE_THRESHOLD_DET",
    "SSOT_SCORE_THRESHOLD_QWEN",
    "SYSTEM_LEARNING_DIR",
    "TESTS_DIR",
    "TESTS_UNIT_DIR",
    "THRESHOLD",
    "TOOLS_DIR",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "WINDSURF_SCRIPTS_DIR",
    "get_all_apps_paths",
    "get_apps_directories",
    "get_validated_project_root",
    "safe_path_join",
    "validate_flat_directory",
    "validate_path_within_project",
]
