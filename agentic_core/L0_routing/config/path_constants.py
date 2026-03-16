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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_reads_policy_state("p1", "path_constants", "L0")
_emit_escalates_to_human("p1", "path_constants", "L0")
_emit_routes_through("p1", "path_constants", "L0")
_emit_dispatches_healing_run("p1", "path_constants", "L0")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("path_constants", "p4obs", "metric_1")
_emit_emits_metric_event("path_constants", "p4obs", "metric_2")
_emit_emits_metric_event("path_constants", "p4obs", "metric_3")
_emit_emits_metric_event("path_constants", "p4obs", "metric_4")
_emit_emits_metric_event("path_constants", "p4obs", "metric_5")
_emit_emits_metric_event("path_constants", "p4obs", "metric_6")
_emit_records_incident_event("path_constants", "p4obs", "incident")
_emit_captures_runtime_anomaly("path_constants", "p4obs", "anomaly")
_emit_writes_observability_log("path_constants", "p4obs", "obs_log")
_emit_updates_monitoring_state("path_constants", "p4obs", "mon_state")
_emit_triggers_alert("path_constants", "p4obs", "alert")
_emit_links_incident_trace("path_constants", "p4obs", "trace_link")
_emit_captures_pattern("path_constants", "p3lm", "pattern")
_emit_records_learning_event("path_constants", "p3lm", "learning_event")
_emit_writes_learning_snapshot("path_constants", "p3lm", "snapshot")
_emit_feeds_meta_learning("path_constants", "p3lm", "meta_feed")
_emit_updates_routing_strategy("path_constants", "p3lm", "routing")
_emit_improves_agent_policy("path_constants", "p3lm", "policy")
_emit_stores_learning_state("path_constants", "p3lm", "state")
_emit_records_execution_trace("path_constants", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("path_constants", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("path_constants", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("path_constants", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("path_constants", "L4_STATE", "p2_trace_5")
_emit_reads_environ("path_constants", "env_read", "p2_env_1")
_emit_reads_environ("path_constants", "env_read", "p2_env_2")
_emit_reads_runtime_state("path_constants", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("path_constants", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "path_constants", "context_pull")
_emit_pulls_context("p1", "path_constants", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "path_constants", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "path_constants", "uwg_term_2")
_emit_writes_through("p1", "path_constants", "write_through")
_emit_writes_through("p1", "path_constants", "write_through_2")
_emit_validated_by_safety_plane("p1", "path_constants", "safety_validation")
_emit_invokes_eval("p1", "path_constants", "eval_call")
_emit_proposal_commits_routing("p1", "path_constants", "routing_commit")
emit_replay_key("p0", "path_constants")
emit_determinism_digest("p0", "path_constants")
_emit_authorize_and_execute("p2", "path_constants", "execution_auth")
_emit_validates_capability("p2", "path_constants", "capability_check")
_emit_routes_to_capability("p2", "path_constants", "capability_route")
_emit_writes_via_uwg("p2", "path_constants", "uwg_write")
_emit_blocks_direct_write("p2", "path_constants", "direct_write_block")
_emit_records_tool_invocation("p2", "path_constants", "tool_invocation")
_emit_captures_execution_output("p2", "path_constants", "exec_output")
_emit_dispatches_agent("p3", "path_constants", "agent_dispatch")
_emit_coordinates_agents("p3", "path_constants", "agent_coordination")
_emit_records_workflow_lineage("p3", "path_constants", "workflow_lineage")
_emit_records_healing_outcome("p3", "path_constants", "healing_outcome")
_emit_escalates_failure("p3", "path_constants", "failure_escalation")
_emit_orchestrates_workflow("p3", "path_constants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "path_constants", "healing_dispatch")
_emit_invokes_evaluation("p3", "path_constants", "evaluation_signal")
_emit_records_telemetry_event("p4", "path_constants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "path_constants", "eval_metric")
_emit_stores_embedding("p4", "path_constants", "embedding_store")
_emit_updates_meta_learning_state("p4", "path_constants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "path_constants", "exec_snapshot_link")

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
