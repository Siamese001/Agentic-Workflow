"""
Operational configuration for Runtime Agents
Centralized settings for file scanning, deduplication, and operational tasks.

This is separate from structure_blueprint.py which defines compliance rules.
This config is for OPERATIONAL agents that need to know what to scan/exclude.
Aligned with apps_* pattern with full lifecycle trace contract integration.
"""

import sys
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_environ,
    _emit_reads_policy_state,
    _emit_snapshots_state,
    _emit_validates_capability,
    emit_determinism_digest,
    emit_replay_key,
)

# P0: Foundation Governance
_emit_applies_guardrail("p0", "operational_config", "p0_governance")
_emit_reads_policy_state("p0", "operational_config", "policy_binding")
_emit_snapshots_state("p0", "operational_config", "state_snapshot")

# P2: Execution Capability
_emit_reads_environ("p2", "operational_config", "env_read")
_emit_validates_capability("p2", "operational_config", "capability_check")

# P0: Determinism
emit_replay_key("p0", "operational_config")
emit_determinism_digest("p0", "operational_config")

from apps_shared.config.pipeline_constants_config import MAX_RETRIES  # noqa: F401

DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # guardian: allow-global-mutation

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# ============================================================================
# DIRECTORY EXCLUSIONS - What operational agents should NEVER touch
# ============================================================================

OPERATIONAL_EXCLUDED_DIRS: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)


# ============================================================================
# SCAN TARGETS - Directories that operational agents SHOULD scan
# ============================================================================

OPERATIONAL_SCAN_TARGETS: list[str] = [
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,  # Include tests for deduplication
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
    },
)


# ============================================================================
# FILE EXTENSIONS - What file types to scan
# ============================================================================

OPERATIONAL_PYTHON_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".py",
    },
)

OPERATIONAL_CONFIG_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".json",
        ".yaml",
        ".yml",
        ".toml",
    },
)

OPERATIONAL_ALL_EXTENSIONS: frozenset[str] = OPERATIONAL_PYTHON_EXTENSIONS | OPERATIONAL_CONFIG_EXTENSIONS


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
