"""
L0 Path Constants — Pure SSOT for structural paths.

This module contains ONLY stdlib-dependent constants extracted from
L5_safety.config.structure_blueprint for use by L0 modules without
creating upward import violations.

SSOT: These values are canonical. L5 structure_blueprint re-exports
these for backward compatibility.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Final

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
APPS_LIC_DIR: Final[str] = "apps_lic"
APPS_RG_DIR: Final[str] = "apps_rg"
APPS_SHARED_DIR: Final[str] = "apps_shared"
ARCHIVES_DIR: Final[str] = "archives"
OPS_SCRIPTS_DIR: Final[str] = "ops_scripts"
SCRIPTS_DIR: Final[str] = "scripts"
SYSTEM_LEARNING_DIR: Final[str] = "system_learning"
TESTS_DIR: Final[str] = "tests"
TESTS_UNIT_DIR: Final[str] = "tests/unit"
TOOLS_DIR: Final[str] = "tools"
DASHBOARD_DIR: Final[str] = "agentic_core/L6_observability/dashboards"
REPORTS_DIR: Final[str] = "reports"

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
    }
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
        "apps_lic",
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
    }
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
    }
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
    }
)

VARIABLE_DEPTH_SUBFOLDERS: Final[frozenset[str]] = frozenset(
    {
        "types",
        "config",
        "unit",
        "unit_min_deps",
        "integration",
    }
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
    }
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
    }
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
    "apps_lic": 2,
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
        "apps_lic",
        "apps_rg",
        "apps_shared",
        "archives",
        "data",
        "docs",
        "ops_scripts",
        "tests",
    }
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

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "AGENTIC_CORE_DIR",
    "APPS_LIC_DIR",
    "APPS_LIC_SUBFOLDER_MAP",
    "APPS_RG_DIR",
    "APPS_RG_SUBFOLDER_MAP",
    "APPS_SHARED_DIR",
    "APPS_SHARED_SUBFOLDER_MAP",
    "ARCHIVES_DIR",
    "CORE_SUBFOLDER_MAP",
    "DASHBOARD_DIR",
    "DEPTH_RULES",
    "SYSTEM_LEARNING_DIR",
    "TOOLS_DIR",
    "GLOBAL_EXCLUDED_DIRS",
    "L0_MAINTENANCE_DIR",
    "L0_ROUTING_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L3_ORCHESTRATION_DIR",
    "L4_APPROVED_FOLDERS",
    "L4_STATE_DIR",
    "L5_SAFETY_DIR",
    "L6_OBSERVABILITY_DIR",
    "LAYER_ROOTS",
    "OPS_SCRIPTS_DIR",
    "PROJECT_ROOT_MARKERS",
    "PROJECT_ROOT_WHITELIST",
    "ROOT_ALLOWED_PATTERNS",
    "ROOT_PROTECTED_FILES",
    "ROOT_WHITELIST",
    "RUNTIME_STATE_JSON",
    "SCRIPTS_DIR",
    "SOVEREIGN_EXCLUDED_FOLDERS",
    "TESTS_DIR",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "get_validated_project_root",
]
