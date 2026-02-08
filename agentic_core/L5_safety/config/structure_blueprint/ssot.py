"""
SSOT Module - HOT PATH (Minimal Import Cost)

This module contains ONLY the lightweight, frequently-accessed constants and
functions that must be available immediately on import. Heavy registries and
regex patterns are loaded lazily from cold modules.

Design Principles:
1. NO regex compilation at import time
2. NO heavy dict/list literals (>50 items)
3. NO filesystem reads
4. Lazy loaders for cold module data
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

# ============================================================================
# LAYER VALIDATION API (Phase 1 Hardening — 2026-02-07)
# ============================================================================

LAYER_ROOTS: Final[frozenset[str]] = frozenset(
    {
        "L0_maintenance",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    },
)

REQUIRED_LCD_SUBFOLDERS: Final[frozenset[str]] = frozenset(
    {
        "reasoning",
        "enforcement",
        "config",
        "types",
        "validators",
        "utils",
    },
)

LEAF_DOMAINS_NO_LCD: Final[frozenset[str]] = frozenset(
    {
        "prompt_governance",
        "knowledge",
        "mixins",
        "runtime",
        "interfaces",
        "base_agents",
        "config",
    },
)

STANDARD_LAYER_STRUCTURE: Final[list[str]] = [
    "config",
    "types",
    "reasoning",
    "enforcement",
    "validators",
    "utils",
]


def is_layer_root(name: str) -> bool:
    """Return True if *name* is a canonical L0–L6 layer root."""
    return name in LAYER_ROOTS


def is_allowed_subfolder(layer: str, subfolder: str) -> bool:
    """Return True if *subfolder* is a required LCD subfolder under *layer*."""
    if layer not in LAYER_ROOTS:
        return False
    return subfolder in REQUIRED_LCD_SUBFOLDERS


def validate_no_nested_lcd(path_parts: Sequence[str]) -> dict[str, Any] | None:
    """Detect leaf domains that illegally sprout LCD subtrees.

    Args:
        path_parts: tuple/list of path components (e.g. Path.parts).

    Returns:
        None if compliant, or a violation dict with:
        - domain: the leaf domain that is sprouting
        - illegal_subfolder: the LCD subfolder it created
        - message: human-readable explanation
    """
    for i, part in enumerate(path_parts):
        if part in LEAF_DOMAINS_NO_LCD:
            for j in range(i + 1, len(path_parts)):
                child = path_parts[j]
                if child in REQUIRED_LCD_SUBFOLDERS:
                    has_layer_root_ancestor = any(path_parts[k] in LAYER_ROOTS for k in range(i))
                    if has_layer_root_ancestor:
                        break
                    return {
                        "domain": part,
                        "illegal_subfolder": child,
                        "message": (
                            f"Leaf domain '{part}' must not sprout LCD subfolder "
                            f"'{child}/'. Only L0–L6 layer roots may have LCD subtrees."
                        ),
                    }
    return None


# ============================================================================
# ALLOWLISTS (Path-Based for Collision Prevention)
# ============================================================================

L5_SUBPROCESS_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        "agentic_core/L5_safety/enforcement/safe_subprocess_handler.py",
        "agentic_core/L5_safety/utils/subprocess_security_util.py",
        "agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py",
        "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py",
        "agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py",
        "agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py",
        "agentic_core/L5_safety/utils/pre_deploy_check_util.py",
    },
)

L6_HYBRID_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        "agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py",
    },
)

SCRIPTS_FORBIDDEN_PATTERNS: Final[Sequence[str]] = [
    r"^[A-Z]",
    r"^test_",
]


# ============================================================================
# PATH CONSTANTS (SSOT for Directory References)
# ============================================================================

AGENTIC_CORE_DIR: Final[str] = "agentic_core"
APPS_RG_DIR: Final[str] = "apps_rg"
APPS_LIC_DIR: Final[str] = "apps_lic"
APPS_SHARED_DIR: Final[str] = "apps_shared"

AGENT_DISCOVERY_JSON: str = "agent_discovery_full.json"
AGENT_DISCOVERY_MANIFEST_JSON: str = "agent_discovery_full.manifest.json"
RUNTIME_STATE_JSON: str = "runtime_state.json"

OPS_SCRIPTS_DIR: str = "ops_scripts"
TESTS_DIR: str = "tests"

L0_MAINTENANCE_DIR: str = "agentic_core/L0_maintenance"
L1_COGNITION_DIR: str = "agentic_core/L1_cognition"
L2_EXECUTION_DIR: str = "agentic_core/L2_execution"
L3_ORCHESTRATION_DIR: str = "agentic_core/L3_orchestration"
L4_STATE_DIR: str = "agentic_core/L4_state"
L5_SAFETY_DIR: str = "agentic_core/L5_safety"
L6_OBSERVABILITY_DIR: str = "agentic_core/L6_observability"

DASHBOARD_DIR: str = "agentic_core/L6_observability/dashboards"
BLUEPRINT_SOVEREIGN_DIR: str = "agentic_core/config/core"
SCHEMAS_DIR: str = "agentic_core/runtime/types"
PROMPT_GOVERNANCE_DIR: str = "agentic_core/prompt_governance"
UTILS_DIR: str = "agentic_core/utils"
RUNTIME_DIR: str = "agentic_core/runtime"

TESTS_UNIT_DIR: str = "tests/unit"
TESTS_INTEGRATION_DIR: str = "tests/integration"
TESTS_E2E_DIR: str = "tests/e2e"
TESTS_AUTOGEN_DIR: str = "tests/autogen"

REPORTS_DIR: str = "reports"
ARCHIVES_DIR: str = "archives"
COVERAGE_HTML_DIR: str = "reports/coverage_html"
DOCS_REPORTS_PLANS: str = "docs/reports/plans"

KNOWN_GOOD_HASHES: Final[Mapping[str, str]] = {
    "forensic_discovery_prep.py": "3fadb7164353e0d7072d985da0ba06187a4f3a003588dd3341a43dd94eaa86d0",
}

PROJECT_ROOT_MARKERS: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "canon_validator_agentic_v2_thin.py",
        "agentic_core",
        ".git",
    },
)


def get_validated_project_root() -> Path:
    """Get the validated project root by searching upward from this file."""
    current = Path(__file__).resolve()

    for parent in [current] + list(current.parents):
        markers_found = sum(1 for marker in PROJECT_ROOT_MARKERS if (parent / marker).exists())
        if markers_found >= 2:
            return parent

    raise ValueError(f"Could not find valid project root from {__file__}")


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


# ============================================================================
# VARIABLE DEPTH SUBFOLDERS
# ============================================================================

VARIABLE_DEPTH_SUBFOLDERS: frozenset[str] = frozenset(
    {
        "base_agents",
        "utils",
        "config",
        "reasoning",
        "enforcement",
        "validators",
        "L6_observability",
        "L3_orchestration",
        "L0_maintenance",
        "L1_cognition",
        "L2_execution",
        "L4_state",
        "L5_safety",
        "prompt_governance",
        "runtime",
        "semantic_memory",
        "agentic_core",
        "apps_rg",
        "apps_lic",
        "apps_shared",
        "ops_scripts",
        "tests",
        "docs",
        "reports",
        "logs",
        "archives",
        ".gravity_state",
        ".backup",
        "knowledge",
    },
)


# ============================================================================
# LAZY LOADERS FOR COLD MODULES
# ============================================================================


@lru_cache(maxsize=1)
def get_sovereign_territories() -> Mapping[str, Any]:
    """Lazy load SOVEREIGN_TERRITORIES from territories module."""
    from agentic_core.L5_safety.config.structure_blueprint.territories import SOVEREIGN_TERRITORIES

    return SOVEREIGN_TERRITORIES


@lru_cache(maxsize=1)
def get_core_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Lazy load CORE_SUBFOLDER_MAP from derived module."""
    from agentic_core.L5_safety.config.structure_blueprint.derived import CORE_SUBFOLDER_MAP

    return CORE_SUBFOLDER_MAP


@lru_cache(maxsize=1)
def get_subfolder_metadata() -> Mapping[str, Mapping[str, Any]]:
    """Lazy load SUBFOLDER_METADATA from derived module."""
    from agentic_core.L5_safety.config.structure_blueprint.derived import SUBFOLDER_METADATA

    return SUBFOLDER_METADATA


@lru_cache(maxsize=1)
def get_apps_rg_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Lazy load APPS_RG_SUBFOLDER_MAP from derived module."""
    from agentic_core.L5_safety.config.structure_blueprint.derived import APPS_RG_SUBFOLDER_MAP

    return APPS_RG_SUBFOLDER_MAP


@lru_cache(maxsize=1)
def get_apps_lic_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Lazy load APPS_LIC_SUBFOLDER_MAP from derived module."""
    from agentic_core.L5_safety.config.structure_blueprint.derived import APPS_LIC_SUBFOLDER_MAP

    return APPS_LIC_SUBFOLDER_MAP


@lru_cache(maxsize=1)
def get_apps_shared_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Lazy load APPS_SHARED_SUBFOLDER_MAP from derived module."""
    from agentic_core.L5_safety.config.structure_blueprint.derived import APPS_SHARED_SUBFOLDER_MAP

    return APPS_SHARED_SUBFOLDER_MAP
