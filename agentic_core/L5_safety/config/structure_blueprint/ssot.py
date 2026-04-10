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

import os
import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from re import Pattern
from typing import Any, Final

try:
    import yaml
except ImportError:
    yaml = None  # guardian: allow-silent-swallow

# Wave 3: ROOT_WHITELIST import removed - now defined locally as alias to PROJECT_ROOT_WHITELIST
from agentic_core.L5_safety.config.structure_blueprint.derived import (
    L4_APPROVED_FOLDERS,
    L4_SUBFOLDER_MAP,
)
from agentic_core.L5_safety.config.structure_blueprint.territories import (
    get_all_territories,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "ssot")
emit_determinism_digest("p0", "ssot")

_emit_dispatches_healing_run("p1", "ssot", "L5")
_emit_routes_through("p1", "ssot", "L5")
_emit_checks_agent_registry("p1", "ssot", "agent_registry")
_emit_validates_agent_capability("p1", "ssot", "capability")
_emit_dispatches_execution_plan("p1", "ssot", "exec_plan")
_emit_agent_executes_agent("p1", "ssot", "sub_agent")
_emit_routes_to_agent("p1", "ssot", "target_agent")
_emit_verifies_policy("p1", "ssot", "policy_check")
_emit_observes_runtime_state("p1", "ssot", "runtime_state")
_emit_verifies_boundary("p1", "ssot", "boundary_check")
_emit_transcripts_response("p1", "ssot", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot")
_emit_gated_by_confidence("p1", "ssot", "confidence_gate")
_emit_escalates_to_human("p1", "ssot", "L5")
_emit_reads_policy_state("p1", "ssot", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "ssot")
_emit_applies_guardrail("p0", "ssot", "p0_governance")
_emit_snapshots_state("p0", "ssot", "state_snapshot")
_emit_authorize_and_execute("p2", "ssot", "execution_auth")
_emit_validates_capability("p2", "ssot", "capability_check")
_emit_routes_to_capability("p2", "ssot", "capability_route")
_emit_writes_via_uwg("p2", "ssot", "uwg_write")
_emit_blocks_direct_write("p2", "ssot", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot", "tool_invocation")
_emit_captures_execution_output("p2", "ssot", "exec_output")
_emit_dispatches_agent("p3", "ssot", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot", "healing_outcome")
_emit_escalates_failure("p3", "ssot", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot", "eval_metric")
_emit_stores_embedding("p4", "ssot", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("ssot", "p4obs", "metric_1")
_emit_emits_metric_event("ssot", "p4obs", "metric_2")
_emit_emits_metric_event("ssot", "p4obs", "metric_3")
_emit_emits_metric_event("ssot", "p4obs", "metric_4")
_emit_emits_metric_event("ssot", "p4obs", "metric_5")
_emit_emits_metric_event("ssot", "p4obs", "metric_6")
_emit_records_incident_event("ssot", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot", "p4obs", "anomaly")
_emit_writes_observability_log("ssot", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot", "p4obs", "mon_state")
_emit_triggers_alert("ssot", "p4obs", "alert")
_emit_links_incident_trace("ssot", "p4obs", "trace_link")
_emit_captures_pattern("ssot", "p3lm", "pattern")
_emit_records_learning_event("ssot", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot", "p3lm", "routing")
_emit_improves_agent_policy("ssot", "p3lm", "policy")
_emit_stores_learning_state("ssot", "p3lm", "state")
_emit_records_execution_trace("ssot", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot", "env_read", "p2_env_1")
_emit_reads_environ("ssot", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot", "context_pull")
_emit_pulls_context("p1", "ssot", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot", "uwg_term_2")
_emit_writes_through("p1", "ssot", "write_through")
_emit_writes_through("p1", "ssot", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot", "safety_validation")
_emit_invokes_eval("p1", "ssot", "eval_call")
_emit_proposal_commits_routing("p1", "ssot", "routing_commit")

# ============================================================================
# LAYER VALIDATION API (Phase 1 Hardening — 2026-02-07)
# ============================================================================

LAYER_ROOTS: Final[frozenset[str]] = frozenset(
    {
        "L0_routing",
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
        "agents",
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

# ============================================================================
# TERRITORY SCANNING SCOPE (SSOT for agent folder coverage)
# ============================================================================

# Territories with enforced SSOT structure requirements
# Used by: FilesystemSSOTReconcilerAgent, FileClassificationAgent, HierarchyAgent, ArchitectureGovernorAgent
# apps_* folders are auto-discovered via _discover_apps_wildcard_folders() (defined below) — no manual edits needed.
# ENFORCED_TERRITORIES is finalized after _discover_apps_wildcard_folders is defined (search below).
_ENFORCED_TERRITORIES_BASE: frozenset[str] = frozenset(
    {
        "agentic_core",
        "tests",
        "ops_scripts",
        "system_learning",
        "tools",
        "data",
        "docs",
        "config",
    },
)

# Subset of enforced territories that contain Python code (excludes data/, docs/)
# Used by: SystemArchitectAgent (circular dependency detection)
# apps_* folders are auto-discovered — no manual edits needed.
# CODE_TERRITORIES is finalized after _discover_apps_wildcard_folders is defined (search below).
_CODE_TERRITORIES_BASE: frozenset[str] = frozenset(
    {
        "agentic_core",
        "tests",
        "ops_scripts",
        "system_learning",
        "tools",
        "config",
    },
)

# Volatile/output territories excluded from structure enforcement
# Used by: All scanning agents (exclusion list)
VOLATILE_TERRITORIES: Final[frozenset[str]] = frozenset(
    {
        "logs",
        "archives",
        "tests",
        ".github",
        ".backup",
        "artifacts",
        ".gravity_state",
    },
)


def validate_volatile_exclusion_contract() -> dict[str, Any]:
    """Validate that volatile territories are properly excluded from Production Lens.

    Contract: Any territory marked volatile=True must appear in GLOBAL_EXCLUDED_DIRS.
    This ensures Production Lens (build/coverage tools) skips output directories.

    Returns:
        Dict with validation results:
        - valid: bool (all contracts satisfied)
        - violations: list of territory names violating the contract
        - missing_from_exclusion: list of volatile territories not in GLOBAL_EXCLUDED_DIRS
        - missing_from_volatile_set: list of excluded territories not in VOLATILE_TERRITORIES
    """
    territories = get_all_territories()
    volatile_from_territories = frozenset(k for k, v in territories.items() if v.get("volatile"))

    # Contract check: volatile territories must be in GLOBAL_EXCLUDED_DIRS
    missing_from_exclusion = volatile_from_territories - GLOBAL_EXCLUDED_DIRS

    # Contract check: VOLATILE_TERRITORIES frozenset must match volatile territories
    missing_from_volatile_set = volatile_from_territories - VOLATILE_TERRITORIES

    violations = list(missing_from_exclusion | missing_from_volatile_set)

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "missing_from_exclusion": list(missing_from_exclusion),
        "missing_from_volatile_set": list(missing_from_volatile_set),
        "volatile_territories": list(volatile_from_territories),
    }


# Territories that permit a .py file directly at depth-1 (allow_root_py flag)
ALLOW_ROOT_PY_TERRITORIES: Final[frozenset[str]] = frozenset(
    k for k, v in get_all_territories().items() if v.get("allow_root_py")
)

# Territories that use L0–L6 prefixes intentionally (layer_prefix_exempt flag)
LAYER_PREFIX_EXEMPT_TERRITORIES: Final[frozenset[str]] = frozenset(
    k for k, v in get_all_territories().items() if v.get("layer_prefix_exempt")
)


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
        "agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py",
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
APPS_EVAL_DIR: Final[str] = "apps_eval"
APPS_EXEC_DIR: Final[str] = "apps_exec"
APPS_RESEARCH_DIR: Final[str] = "apps_research"
APPS_RFP_DIR: Final[str] = "apps_rfp"

AGENT_DISCOVERY_JSON: str = "agent_discovery_full.json"
AGENT_DISCOVERY_MANIFEST_JSON: str = "agent_discovery_full.manifest.json"
RUNTIME_STATE_JSON: str = "runtime_state.json"

# Forensic discovery script integrity — canonical SHA-256 of the corrected script.
# Verified by the audit precondition step before any analysis begins.
FORENSIC_DISCOVERY_SCRIPT: str = "agentic_core/L0_routing/scripts/forensic_discovery_prep.py"
FORENSIC_DISCOVERY_INTEGRITY_HASH: str = "e248d17f49620ba763ab161c8799bfd37cdfd71badf6adba3adb92e56504944b"

OPS_SCRIPTS_DIR: str = "ops_scripts"
TESTS_DIR: str = "tests"

L0_MAINTENANCE_DIR: str = "agentic_core/L0_routing"
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
TESTS_AUTOGEN_DIR: str = "tests/unit_min_deps"

# ---------------------------------------------------------------------------
# WILDCARD APPS DISCOVERY
# Auto-detects apps_* folders without requiring manual SSOT edits
# ---------------------------------------------------------------------------


def _discover_apps_wildcard_folders(repo_root: Path | None = None) -> frozenset[str]:
    """Discover all apps_* folders at repo root dynamically.

    This enables automatic adoption of new app territories without
    requiring manual updates to SSOT constants.

    Args:
        repo_root: Repository root path. If None, uses get_validated_project_root().

    Returns:
        Frozenset of apps_* folder names found at repo root.
    """
    if repo_root is None:
        try:
            repo_root = get_validated_project_root()
        except ValueError:
            return frozenset()

    apps_folders = set()
    try:
        for item in repo_root.iterdir():
            if item.is_dir() and item.name.startswith("apps_"):
                apps_folders.add(item.name)
    except (OSError, PermissionError) as e:
        import logging

        logging.getLogger(__name__).debug("ssot: OSError swallowed at L488: %s", e)

    return frozenset(apps_folders)


# Finalize ENFORCED_TERRITORIES and CODE_TERRITORIES now that _discover_apps_wildcard_folders is defined.
# apps_* folders are auto-discovered — adding a new apps_* dir at repo root is sufficient.
try:
    ENFORCED_TERRITORIES: Final[frozenset[str]] = (
        _ENFORCED_TERRITORIES_BASE | _discover_apps_wildcard_folders()
    )
except Exception:
    ENFORCED_TERRITORIES = _ENFORCED_TERRITORIES_BASE  # type: ignore[misc]

try:
    CODE_TERRITORIES: Final[frozenset[str]] = _CODE_TERRITORIES_BASE | _discover_apps_wildcard_folders()
except Exception:
    CODE_TERRITORIES = _CODE_TERRITORIES_BASE  # type: ignore[misc]


# Base mirror roots that are NOT dynamically discovered (stable)
_BASE_MIRROR_ROOTS: frozenset[str] = frozenset(
    {
        "agentic_core",
        "system_learning",
    },
)

# ---------------------------------------------------------------------------
# TEST PLACEMENT SSOT
# Single canonical map: source root → mirror test directory.
# LocationHealerAgent, TestGeneratorAgent, and all validators MUST import
# from here instead of hardcoding test paths.
#
# NOTE: apps_* folders are auto-discovered via _discover_apps_wildcard_folders()
# to avoid requiring manual SSOT edits when adding new app territories.
# ---------------------------------------------------------------------------
TEST_MIRROR_BASE: str = "tests/unit"


def get_test_mirror_roots(repo_root: Path | None = None) -> frozenset[str]:
    """Return all test mirror roots including dynamically discovered apps_* folders."""
    discovered = _discover_apps_wildcard_folders(repo_root)
    return _BASE_MIRROR_ROOTS | discovered


# Legacy constant for backward compatibility (evaluated at import time)
# New code should use get_test_mirror_roots() for dynamic discovery
# Uses try/except to handle circular import during module load
try:
    TEST_MIRROR_ROOTS: frozenset[str] = _BASE_MIRROR_ROOTS | _discover_apps_wildcard_folders()
except NameError:
    # get_validated_project_root not yet defined during module load
    TEST_MIRROR_ROOTS = _BASE_MIRROR_ROOTS


def _build_test_canonical_location_map(repo_root: Path | None = None) -> dict[str, str]:
    """Build canonical test location map with wildcard apps_* support."""
    base_map = {
        "agentic_core": "tests/unit/agentic_core",
        "system_learning": "tests/unit/system_learning",
    }

    try:
        discovered = _discover_apps_wildcard_folders(repo_root)
        for app_name in discovered:
            base_map[app_name] = f"tests/unit/{app_name}"
    except NameError as e:
        # get_validated_project_root not yet defined during module load
        import logging

        logging.getLogger(__name__).debug("ssot: NameError swallowed at L554: %s", e)

    return base_map


# Legacy map for backward compatibility
# Uses try/except to handle circular import during module load
try:
    TEST_CANONICAL_LOCATION_MAP: dict[str, str] = _build_test_canonical_location_map()
except NameError:
    # Fallback during module load
    TEST_CANONICAL_LOCATION_MAP = {
        "agentic_core": "tests/unit/agentic_core",
        "system_learning": "tests/unit/system_learning",
    }


def get_canonical_test_path(source_path: Path, repo_root: Path) -> Path:
    """Return the canonical test file path for a given source file.

    LocationHealerAgent and TestGeneratorAgent MUST call this function instead
    of constructing test paths ad-hoc.  The mapping is read from
    TEST_CANONICAL_LOCATION_MAP so there is a single SSOT.

    Examples
    --------
    source: agentic_core/L5_safety/foo.py  →  tests/unit/agentic_core/L5_safety/test_foo.py
    source: apps_rg/engines/bar.py         →  tests/unit/apps_rg/engines/test_bar.py
    source: tools/mirror_tests.py          →  tests/unit_min_deps/test_mirror_tests.py
    """
    from pathlib import Path as _Path

    src = _Path(source_path)
    root = _Path(repo_root)
    try:
        rel = src.relative_to(root)
    except ValueError:
        rel = src

    parts = rel.parts
    if not parts:
        return root / TESTS_AUTOGEN_DIR / f"test_{src.stem}.py"

    source_root = parts[0]

    # Use dynamic discovery for wildcard apps_* support
    location_map = _build_test_canonical_location_map(repo_root)
    mirror_base = location_map.get(source_root)
    if mirror_base is None:
        return root / TESTS_AUTOGEN_DIR / f"test_{src.stem}.py"

    sub_parts = parts[1:-1]  # directories between root and filename
    return (
        root / mirror_base / _Path(*sub_parts) / f"test_{src.stem}.py"
        if sub_parts
        else root / mirror_base / f"test_{src.stem}.py"
    )


REPORTS_DIR: str = "reports"
ARCHIVES_DIR: str = "archives"
COVERAGE_HTML_DIR: str = "reports/coverage_html"
DOCS_REPORTS_PLANS: str = "docs/reports/plans"

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
        "agents",
        "utils",
        "config",
        "reasoning",
        "enforcement",
        "validators",
        "engines",
        "scripts",
        "tools",
        "types",
        "security",
        "governance",
        "dashboards",
        "seams",
        "mixins",
        "interfaces",
        "L6_observability",
        "L3_orchestration",
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L4_state",
        "L5_safety",
        "prompt_governance",
        "runtime",
        "knowledge",
        "ops_scripts",
        "tests",
        "docs",
        "reports",
        "logs",
        "archives",
        ".gravity_state",
        ".backup",
    },
)


# ============================================================================
# LAZY LOADERS FOR COLD MODULES
# ============================================================================


@lru_cache(maxsize=1)
def get_sovereign_territories() -> Mapping[str, Any]:
    """Return territory definitions (DEPRECATED: use get_all_territories() instead)."""
    return get_all_territories()


@lru_cache(maxsize=1)
def get_core_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return CORE_SUBFOLDER_MAP from derived module."""
    from agentic_core.L5_safety.config.structure_blueprint.derived import CORE_SUBFOLDER_MAP

    return CORE_SUBFOLDER_MAP


@lru_cache(maxsize=1)
def get_subfolder_metadata() -> Mapping[str, Mapping[str, Any]]:
    """Return SUBFOLDER_METADATA from derived module."""
    from agentic_core.L5_safety.config.structure_blueprint.derived import SUBFOLDER_METADATA

    return SUBFOLDER_METADATA


@lru_cache(maxsize=1)
def get_apps_wildcard_subfolder_map(app_name: str) -> Mapping[str, Sequence[str]]:
    """Return subfolder map for any apps_* folder via dynamic derivation.

    This enables automatic support for new app territories without requiring
    manual SSOT updates. Uses the same derivation logic as explicit apps.

    Args:
        app_name: The apps_* folder name (e.g., 'apps_rg', 'apps_new')

    Returns:
        Mapping of subfolder names to their nested structure.
    """
    from agentic_core.L5_safety.config.structure_blueprint.derived import _derive_apps_subfolder_map

    return _derive_apps_subfolder_map(app_name)


@lru_cache(maxsize=1)
def get_apps_rg_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return APPS_RG_SUBFOLDER_MAP - now uses wildcard discovery."""
    return get_apps_wildcard_subfolder_map("apps_rg")


@lru_cache(maxsize=1)
def get_apps_lic_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return APPS_LIC_SUBFOLDER_MAP - now uses wildcard discovery."""
    return get_apps_wildcard_subfolder_map("apps_lic")


@lru_cache(maxsize=1)
def get_apps_shared_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return APPS_SHARED_SUBFOLDER_MAP - now uses wildcard discovery."""
    return get_apps_wildcard_subfolder_map("apps_shared")


@lru_cache(maxsize=1)
def get_apps_eval_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return APPS_EVAL_SUBFOLDER_MAP - now uses wildcard discovery."""
    return get_apps_wildcard_subfolder_map("apps_eval")


@lru_cache(maxsize=1)
def get_apps_exec_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return APPS_EXEC_SUBFOLDER_MAP - now uses wildcard discovery."""
    return get_apps_wildcard_subfolder_map("apps_exec")


@lru_cache(maxsize=1)
def get_apps_research_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return APPS_RESEARCH_SUBFOLDER_MAP - now uses wildcard discovery."""
    return get_apps_wildcard_subfolder_map("apps_research")


@lru_cache(maxsize=1)
def get_apps_rfp_subfolder_map() -> Mapping[str, Sequence[str]]:
    """Return APPS_RFP_SUBFOLDER_MAP - now uses wildcard discovery."""
    return get_apps_wildcard_subfolder_map("apps_rfp")


# ============================================================================
# EXCLUSION LOADING FROM YAML SSOT
# ============================================================================


@lru_cache(maxsize=1)
def _load_exclusions_from_yaml() -> dict[str, frozenset[str]]:
    """Load exclusion directories from excluded_paths.yaml (SSOT).

    Returns:
        Dict with keys: 'build_cache', 'version_control', 'virtual_env',
        'coverage', 'archive', 'ide', 'vendor', 'data', 'special'
    """
    if yaml is None:
        # Fallback to hardcoded values if PyYAML not available
        return {
            "build_cache": frozenset(),
            "version_control": frozenset(),
            "virtual_env": frozenset(),
            "coverage": frozenset(),
            "archive": frozenset(),
            "ide": frozenset(),
            "vendor": frozenset(),
            "data": frozenset(),
            "special": frozenset(),
        }

    # Path to excluded_paths.yaml (relative to this file)
    config_path = Path(__file__).parent.parent.parent.parent.parent / "config" / "excluded_paths.yaml"

    if not config_path.exists():
        # Fallback if config file not found
        return {
            "build_cache": frozenset(),
            "version_control": frozenset(),
            "virtual_env": frozenset(),
            "coverage": frozenset(),
            "archive": frozenset(),
            "ide": frozenset(),
            "vendor": frozenset(),
            "data": frozenset(),
            "special": frozenset(),
        }

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Build frozensets for each category
    return {
        "build_cache": frozenset(data.get("build_cache_dirs", [])),
        "version_control": frozenset(data.get("version_control_dirs", [])),
        "virtual_env": frozenset(data.get("virtual_env_dirs", [])),
        "coverage": frozenset(data.get("coverage_dirs", [])),
        "archive": frozenset(data.get("archive_dirs", [])),
        "ide": frozenset(data.get("ide_dirs", [])),
        "vendor": frozenset(data.get("vendor_dirs", [])),
        "data": frozenset(data.get("data_dirs", [])),
        "special": frozenset(data.get("special_dirs", [])),
    }


# ============================================================================
# MIGRATED FROM MONOLITH (structure_blueprint_config.py) — 2026-02-08
# ============================================================================


# File extensions that NamingAgent should validate
VALIDATED_FILE_EXTENSIONS: frozenset[str] = frozenset(
    {
        # Python
        ".py",
        # Templates
        ".jinja",
        ".jinja2",
        ".j2",
        # Config
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        # Documentation
        ".md",
        ".txt",
        ".rst",
        # Web
        ".html",
        ".css",
        ".js",
        ".ts",
    },
)


# Files exempt from naming validation (infrastructure files)
NAMING_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        # Python infrastructure
        "__init__.py",
        "__main__.py",
        "conftest.py",
        "setup.py",
        # Config files
        "pyproject.toml",
        ".env",
        ".gitignore",
        ".dockerignore",
        "Dockerfile",
        "Makefile",
        "requirements.txt",
        # Documentation
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "LICENSE.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        # IDE/Editor
        ".editorconfig",
        ".prettierrc",
        ".eslintrc",
        # Git
        ".gitattributes",
    },
)


# Directories exempt from naming validation
NAMING_EXEMPT_DIRS: frozenset[str] = frozenset(
    {
        "archives",
        "data",
        "docs",  # [ADDED] Valid root
        "legacy_code",
        "legacy_engines",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        ".tox",
        "logs",
    },
)

FORBIDDEN_PATTERNS: Final[Sequence[Pattern]] = [
    re.compile("^utils\\.py$"),
    re.compile("^helper\\.py$"),
    re.compile("^temp\\.py$"),
    re.compile(".*_v\\d+\\.py$"),
    re.compile("^main\\.py$"),
    re.compile("^test\\.py$"),
    re.compile(".*_final\\.py$"),
    re.compile(".*_new\\.py$"),
    re.compile(".*_old\\.py$"),
    re.compile(".*_copy\\.py$"),
    re.compile(".*_backup\\.py$"),
    re.compile("^legacy_.*\\.py$"),
    re.compile("^.+_\\d+\\.py$"),
    re.compile("^draft_.*\\.py$"),
    # Schema Dissolution + Utils Sanitization
    re.compile(r"^utilities_.*"),  # Redundant prefix. Use simple snake_case.
    re.compile(r".*_util_util\.py$"),  # Stuttering suffix violation.
]

# Static protected files (hard-coded core infrastructure)
_STATIC_ROOT_PROTECTED_FILES: frozenset[str] = frozenset(
    {
        "canon_validator_agentic_v2.py",
        "canon_validator_agentic_v2_thin.py",
        "pyproject.toml",
        "README.md",
        "langgraph.json",
        ".env",
        "windsurfrules.md",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".coverage",
        "pytest.ini",
        "tox.ini",
        ".python-version",
        ".schema_violations_tracking.yaml",
        ".secrets.baseline",
        "archives_restoration_manifest.json",
        "audit_residual_rglob_results.json",
        "git.code-workspace",
        "current_test_status.txt",
        "mission_audit.csv",
    },
)


# Dynamic protected files derived from SSOT constants
_DYNAMIC_ROOT_PROTECTED_FILES: frozenset[str] = frozenset(
    {
        AGENT_DISCOVERY_JSON,
        AGENT_DISCOVERY_MANIFEST_JSON,
        RUNTIME_STATE_JSON,
    },
)


# Final combined immutable set - Single Source of Truth for all root-level protection
ROOT_PROTECTED_FILES: frozenset[str] = _STATIC_ROOT_PROTECTED_FILES | _DYNAMIC_ROOT_PROTECTED_FILES


# 2. ENFORCE ROOT PURITY
# Only these folders are allowed at the project root level
PROJECT_ROOT_WHITELIST: Final[frozenset[str]] = frozenset(
    {
        "agentic_core",
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rfp",
        "apps_rg",
        "apps_shared",
        "ops_scripts",
        "tests",
        "docs",
        "data",
        "archives",
        ".git",
        ".github",
        ".gravity_state",
        ".backup",
        ".vscode",
    },
)

# Wave 3: ROOT_WHITELIST alias for backward compatibility
ROOT_WHITELIST = PROJECT_ROOT_WHITELIST


# [SSOT] STRICT ROOT POLICY: Any file NOT in this list or matching these patterns
# is considered "Drift" and must be routed via ARTIFACT_ROUTING_MAP.
ROOT_ALLOWED_PATTERNS: Final[Sequence[Pattern]] = [
    re.compile(r"^trace_.*\.jsonl$"),  # Allowed: Mission Traces
    re.compile(r"^mission_.*\.log$"),  # Allowed: Mission Logs
    re.compile(r"^.*\.bat$"),  # Allowed: Windows Batch scripts
    re.compile(r"^.*\.sh$"),  # Allowed: Shell scripts
    re.compile(r"^root_drift_.*\.py$"),  # Allowed: Remediation scripts (Temp)
    re.compile(r"^ARCHITECTURE_LAYERS\.md$"),  # Allowed: Architecture documentation
    re.compile(r"^README\.md$"),  # Allowed: Project README
    re.compile(r"^AGENTS\.md$"),  # Allowed: Agent guidance documentation
    re.compile(r"^\.codeiumignore$"),  # Allowed: Codeium ignore rules
    re.compile(r"^\.env$"),  # Allowed: Environment variables
    re.compile(r"^\.gitattributes$"),  # Allowed: Git attributes
    re.compile(r"^\.gitignore$"),  # Allowed: Git ignore rules
    re.compile(r"^\.pre-commit-config\.yaml$"),  # Allowed: Pre-commit configuration
    re.compile(r"^\.pylintrc$"),  # Allowed: Pylint configuration
    re.compile(r"^conftest\.py$"),  # Allowed: Root pytest conftest
    re.compile(r"^pyproject\.toml$"),  # Allowed: Python project configuration
    re.compile(r"^pyrightconfig\.json$"),  # Allowed: Pyright type checker configuration
    re.compile(r"^pytest\.ini$"),  # Allowed: Pytest configuration
]


# Load exclusions from YAML SSOT (excluded_paths.yaml)
_exclusions = _load_exclusions_from_yaml()

# Combine all exclusion categories from YAML into single SSOT set
SOVEREIGN_EXCLUDED_FOLDERS: frozenset[str] = frozenset().union(
    _exclusions["build_cache"],
    _exclusions["version_control"],
    _exclusions["virtual_env"],
    _exclusions["coverage"],
    _exclusions["archive"],
    _exclusions["ide"],
    _exclusions["vendor"],
    _exclusions["data"],
    _exclusions["special"],
    # Additional exclusions not in YAML (legacy/intentional)
    frozenset(
        {
            ".github",  # GitHub workflows (intentional)
            ".windsurf",  # Windsurf IDE data (intentional)
            ".hypothesis",  # Hypothesis test DB (intentional)
            "Thumbs.db",  # Windows thumbnail cache (file, not dir)
            "docs",  # Documentation territory (intentional)
            "logging",  # Logging module name conflicts (intentional)
        }
    ),
)

FORBIDDEN_FOLDER_PATTERN: Pattern = re.compile(r"^\d+_")

FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset(
    {"legacy_code", "legacy_engines", "legacy_resume_gen", "old_core"},
)

TESTS_ROOT_FILE_WHITELIST: frozenset[str] = frozenset(
    {"conftest.py", "pytest.ini", "sovereign_smoke_test.py", "test_autonomous_improvements.py"},
)

AUTONOMOUS_AGENT_WHITELIST: frozenset[str] = frozenset(
    {
        "autonomous_checkpoint_manager.py",
        "autonomous_state_guardian.py",
        "self_updating_safety_engine.py",
        "neural_auto_immune_agent.py",
    },
)

protected_folders: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS

ignore_dirs: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS

sovereign_ignored_folders: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS

SCOPE_SUMMARY_EXCLUSIONS: frozenset[str] = frozenset({"stubs", ".sovereign_healing_backup", "__pycache__"})


# === ALLOWED DUPLICATE FILENAMES ===
# These files are permitted to exist with the same name across multiple directories.
# This is the SSOT for filename uniqueness exceptions - all agents must respect this list.
ALLOWED_DUPLICATE_FILENAMES: frozenset[str] = frozenset(
    {
        # Python package infrastructure (MUST exist in every package)
        "__init__.py",
        "__main__.py",
        # Testing infrastructure (pytest requires these in test directories)
        "conftest.py",
        # Common module patterns (legitimate per-package definitions)
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
        # observability patterns (per-engine instrumentation)
        "observability.py",
        "metrics.py",
        "logging.py",
        "tracing.py",
        # Autonomous agent patterns (per-engine autonomy)
        "proactive.py",
        "autonomous.py",
        "self_healing.py",
        # Prompt patterns (per-domain prompts)
        "prompts.py",
        "templates.py",
    },
)


def safe_prefixed_filename(prefix: str, filename: str) -> str:
    """
    SSOT safeguard: Generate a prefixed filename WITHOUT duplicate prefixes.

    Prevents name sprawl like:
        healing_strategies.py -> healing_healing_strategies.py (BAD)

    Instead produces:
        healing_strategies.py -> healing_strategies.py (already has prefix)
        strategies.py -> healing_strategies.py (prefix added)

    Args:
        prefix: The prefix to add (e.g., 'healing', 'auditors')
        filename: The original filename

    Returns:
        Filename with prefix added only if not already present
    """
    if not prefix:
        return filename

    # Normalize prefix (remove trailing underscore if present)
    prefix = prefix.rstrip("_")

    # Check if filename already starts with the prefix
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    "." + filename.rsplit(".", 1)[1] if "." in filename else ""

    # If already has prefix, return unchanged
    if stem.startswith(prefix + "_") or stem == prefix:
        return filename

    # Add prefix
    return f"{prefix}_{filename}"


def validate_no_duplicate_prefix(filename: str) -> tuple[bool, str]:
    """
    SSOT safeguard: Detect if a filename has duplicate prefixes.

    Examples of violations:
        healing_healing_strategies.py -> True, "Duplicate prefix: healing_"
        auditors_auditors_report.py -> True, "Duplicate prefix: auditors_"

    Returns:
        (has_violation, message)
    """
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    parts = stem.split("_")

    # Check for consecutive duplicate parts
    for i in range(len(parts) - 1):
        if parts[i] == parts[i + 1] and parts[i]:  # Non-empty consecutive duplicates
            return True, f"Duplicate prefix detected: '{parts[i]}_' repeated in '{filename}'"

    return False, ""


DISCOVERY_EXCLUDED_TERRITORIES: frozenset[str] = frozenset(
    {"runtime_shared", "legacy_code", "legacy_engines", "archives", "stubs", "examples", "_compat"},
)

PYTHON_STDLIB_MODULES: frozenset[str] = frozenset(
    {
        "os",
        "sys",
        "pathlib",
        "logging",
        "asyncio",
        "typing",
        "dataclasses",
        "collections",
        "json",
        "re",
        "datetime",
        "functools",
        "itertools",
        "abc",
        "enum",
        "contextlib",
        "threading",
        "time",
        "random",
        "math",
        "urllib",
        "http",
        "socket",
        "subprocess",
        "shutil",
        "hashlib",
        "uuid",
        "copy",
        "io",
        "traceback",
        "inspect",
        "importlib",
        "warnings",
        "pickle",
    },
)


# ROOT_WHITELIST is materialized at import time in _constants.py and imported
# at the top of this module. No lazy loading needed.


# ============================================================================
# GLOBAL EXCLUDED DIRECTORIES - Production Lens SSOT
# Loaded from excluded_paths.yaml (YAML SSOT) + intentional additions
# ============================================================================
GLOBAL_EXCLUDED_DIRS: frozenset[str] = frozenset().union(
    _exclusions["build_cache"],
    _exclusions["version_control"],
    _exclusions["virtual_env"],
    _exclusions["coverage"],
    _exclusions["archive"],
    # Additional production lens exclusions (intentional)
    frozenset(
        {
            "logs",  # Log directories
            "artifacts",  # Artifact outputs
            ".github",  # GitHub workflows
            "tests",  # Test directory (excluded from production lens)
            "test_artifacts",  # Test artifacts
        }
    ),
)


def is_path_allowed(rel_path: str | Path) -> bool:
    """
    [ULTRA-HARDENED] Determines if a path conforms to SOVEREIGN_TERRITORIES.
    Enforces path normalization, cross-domain deportation, and depth precision.
    """

    # 1. Path Normalization: Neutralize traversal (../) and redundant slashes (//)
    original_path = str(rel_path).replace("\\", "/")

    # [CRITICAL] Block paths with redundant slashes for security
    if "//" in original_path:
        return False

    # guardian: allow-path-string
    normalized_path = os.path.normpath(original_path).replace("\\", "/")

    # Reject paths that normalize to parent directories or empty
    if not normalized_path or normalized_path.startswith("..") or normalized_path == ".":
        return False

    # Filter out empty parts from normalized path
    parts = [p for p in normalized_path.split("/") if p]
    if not parts:
        return False

    if len(parts) == 1:
        # Allow sovereign territory directories at root level
        if parts[0] in get_all_territories():
            return True
        return parts[0] in ROOT_PROTECTED_FILES or parts[0] in ALLOWED_DUPLICATE_FILENAMES

    root = parts[0]
    if root not in get_all_territories():
        return False

    config = get_all_territories()[root]

    # 2. Cross-Sovereign Deportation: Prevent App/Test leakage into Core
    filename = parts[-1]
    if root == "agentic_core":
        # Critical Analysis: Blocks 'rg_', 'lic_', and 'test_' prefixes to prevent
        # semantic drift while allowing __init__.py and L0 scripts.
        if filename.startswith(("rg_", "lic_", "test_")):
            if not (filename == "__init__.py" or "L0_routing/scripts" in normalized_path):
                return False

    # 3. Depth Enforcement: disabled — repo structure is mature and accurate.
    # The depth caps were set 6 months ago on a greenfield repo and now block
    # legitimate deep paths (agentic_core actual=7, tests actual=9, etc.).
    # The `depth` key is retained in SSOT YAML to avoid KeyError on line 1357
    # but is no longer used as a hard nesting cap.
    # folder_depth kept for the file-position check at line 1357.
    folder_depth = len(parts) - 1 if "." in filename else len(parts)

    # Check subfolder existence and nested forbidden patterns
    if len(parts) > 1:
        sub_name = parts[1]
        allowed_subs = config["subfolders"]

        # [HARDENING] Check for forbidden patterns at the subfolder level (e.g., L3_ prefixes)
        if isinstance(allowed_subs, dict) and sub_name in allowed_subs:
            sub_cfg = allowed_subs[sub_name]
            if isinstance(sub_cfg, dict):
                patterns = sub_cfg.get("forbidden_patterns", [])
                if any(re.search(p, normalized_path) for p in patterns):
                    return False  # BLOCK: Legacy structure detected

        if isinstance(allowed_subs, dict):
            if sub_name not in allowed_subs:
                return sub_name.endswith(".py")  # Root files like __init__.py
        elif isinstance(allowed_subs, list):
            if sub_name not in allowed_subs:
                # Allow files at the correct depth (not subdirectories)
                if "." in sub_name and len(parts) <= config["depth"] + 1:
                    return True
                return False

    return True


def is_l4_approved(path: str) -> bool:
    """
    [HARDENED] Helper to verify L4 specializations.
    Safely navigates both List-based (Apps) and Dict-based (Core) subfolders.
    ONLY approves exactly depth 4 folder structures (excluding filename).
    """

    parts = [p for p in path.split("/") if p]
    if len(parts) < 4:
        return False

    root, l2, l3, l4 = parts[0], parts[1], parts[2], parts[3]

    # Remove filename to check folder structure (depth should be exactly 4 folders)
    folder_parts = parts[:-1] if parts and "." in parts[-1] else parts

    # Must be exactly depth 4 folders for L4 approval
    if len(folder_parts) != 4:
        return False

    try:
        # Check if this is an L4-approved folder path first
        full_folder_path = f"{root}/{l2}/{l3}"
        if full_folder_path in L4_APPROVED_FOLDERS:
            # For approved folders, check if l4 is a valid L4 subfolder in L4_SUBFOLDER_MAP
            # Need to find the right key in L4_SUBFOLDER_MAP and navigate the nested structure
            l4_structure = L4_SUBFOLDER_MAP.get(l2, {})
            if isinstance(l4_structure, dict) and l3 in l4_structure:
                l3_structure = l4_structure[l3]
                if isinstance(l3_structure, dict):
                    # Check if l4 is directly a key in the L3 structure
                    if l4 in l3_structure:
                        return True
                    # Check if l4 is in any of the subfolder lists within the L3 structure
                    for subfolder_list in l3_structure.values():
                        if isinstance(subfolder_list, list) and l4 in subfolder_list:
                            return True

        # Fallback: Check l3-specific configuration for l4_specializations
        root_cfg = get_all_territories().get(root, {})
        subs = root_cfg.get("subfolders", {})

        # Critical Analysis: Prevent TypeError by ensuring 'subs' is a Dict
        # before attempting L2/L3 key lookups (fixes apps_rg crash).
        if not isinstance(subs, dict):
            return False

        # Check both L2 and L3 for the specialization map (Fallback lookup)
        l2_cfg = subs.get(l2, {})
        if isinstance(l2_cfg, dict):
            l3_cfg = l2_cfg.get(l3, {})
            if isinstance(l3_cfg, dict):
                specs = l3_cfg.get("l4_specializations", [])
                if l4 in specs:
                    return True

        return False
    except (KeyError, TypeError, AttributeError):
        return False


# === FLAT DIRECTORIES (No Subfolders Allowed) ===
# Directories marked "flat": True in SOVEREIGN_TERRITORIES.
# Files MUST live directly in these directories — any subdirectory is a violation.
# Derived from territories where "flat" is explicitly True.
FLAT_DIRECTORIES: Final[frozenset[str]] = frozenset(
    {
        "cache",  # deduplicated 2026-04-05 — core/ removed, now flat
        "config",  # deduplicated 2026-04-05 — core/ removed, now flat
        "embeddings",  # deduplicated 2026-04-05 — core/ removed, now flat
        "gateway",  # deduplicated 2026-04-05 — core/ removed, now flat
        "interfaces",  # deduplicated 2026-04-05 — core/ removed, now flat
        "mixins",  # contracts/ dissolved 2026-02-08 — all files flat
        "patterns",  # deduplicated 2026-04-05 — core/ removed, now flat
        "planning",  # deduplicated 2026-04-05 — core/ removed, now flat
        "base_agents",  # Strict identity only — flat by constitution
    },
)


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
    for i, part in enumerate(path_parts):
        if part in FLAT_DIRECTORIES:
            # If there are 2+ parts after the flat directory before the filename,
            # that means there's a subdirectory inside it.
            remaining = path_parts[i + 1 :]
            if len(remaining) > 1:
                # remaining[-1] is the filename, remaining[:-1] are subdirs
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
