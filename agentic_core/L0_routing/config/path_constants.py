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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

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
QWEN_14B_MODEL_ID: str = "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"

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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_validated_project_root", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_validated_project_root", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_validated_project_root")
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
# EXPORTS
# ============================================================================

__all__ = [
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "AGENTIC_CORE_DIR",
    "APPS_EVAL_DIR",
    "APPS_EVAL_SUBFOLDER_MAP",
    "APPS_EXEC_DIR",
    "APPS_EXEC_SUBFOLDER_MAP",
    "APPS_LIC_DIR",
    "APPS_LIC_SUBFOLDER_MAP",
    "APPS_RESEARCH_DIR",
    "APPS_RESEARCH_SUBFOLDER_MAP",
    "APPS_RFP_DIR",
    "APPS_RFP_SUBFOLDER_MAP",
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

# Export list for __init__.py
__all__ = [
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "AGENTIC_CORE_DIR",
    "APPS_EVAL_DIR",
    "APPS_EVAL_SUBFOLDER_MAP",
    "APPS_EXEC_DIR",
    "APPS_EXEC_SUBFOLDER_MAP",
    "APPS_LIC_DIR",
    "APPS_LIC_SUBFOLDER_MAP",
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
    "MAX_DEPTH",
    "MAX_FILES",
    "MAX_RETRIES",
    "OPS_SCRIPTS_DIR",
    "PROJECT_ROOT_MARKERS",
    "PROJECT_ROOT_WHITELIST",
    "ROOT_ALLOWED_PATTERNS",
    "ROOT_PROTECTED_FILES",
    "ROOT_WHITELIST",
    "RUNTIME_STATE_JSON",
    "SCRIPTS_DIR",
    "SOVEREIGN_EXCLUDED_FOLDERS",
    "SYSTEM_LEARNING_DIR",
    "TESTS_DIR",
    "TESTS_UNIT_DIR",
    "THRESHOLD",
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "SSOT_SCORE_THRESHOLD_DET",
    "SSOT_SCORE_THRESHOLD_QWEN",
    "QWEN_14B_MODEL_ID",
    "TOOLS_DIR",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "get_all_apps_paths",
    "get_apps_directories",
]
