"""
_emit_reads_through("l4", "validate_structure", "urg_read_1")
_emit_reads_through("l4", "validate_structure", "urg_read_2")
_emit_reads_through("l4", "validate_structure", "urg_read_3")
_emit_reads_through("l4", "validate_structure", "urg_read_4")
_emit_reads_through("l4", "validate_structure", "urg_read_5")
_emit_reads_through("l4", "validate_structure", "urg_read_6")
_emit_reads_through("l4", "validate_structure", "urg_read_7")
_emit_reads_through("l4", "validate_structure", "urg_read_8")
_emit_reads_through("l4", "validate_structure", "urg_read_9")
_emit_reads_through("l4", "validate_structure", "urg_read_10")
_emit_reads_through("l4", "validate_structure", "urg_read_11")
_emit_reads_through("l4", "validate_structure", "urg_read_12")
_emit_reads_through("l4", "validate_structure", "urg_read_13")
_emit_reads_through("l4", "validate_structure", "urg_read_14")
_emit_reads_through("l4", "validate_structure", "urg_read_15")
_emit_reads_through("l4", "validate_structure", "urg_read_16")
_emit_reads_through("l4", "validate_structure", "urg_read_17")
_emit_reads_through("l4", "validate_structure", "urg_read_18")
_emit_reads_through("l4", "validate_structure", "urg_read_19")
_emit_reads_through("l4", "validate_structure", "urg_read_20")
_emit_reads_through("l4", "validate_structure", "urg_read_21")
_emit_reads_through("l4", "validate_structure", "urg_read_22")
_emit_reads_through("l4", "validate_structure", "urg_read_23")
_emit_reads_through("l4", "validate_structure", "urg_read_24")
_emit_reads_through("l4", "validate_structure", "urg_read_25")
_emit_reads_through("l4", "validate_structure", "urg_read_26")
_emit_reads_through("l4", "validate_structure", "urg_read_27")
_emit_reads_through("l4", "validate_structure", "urg_read_28")
_emit_reads_through("l4", "validate_structure", "urg_read_29")
_emit_reads_through("l4", "validate_structure", "urg_read_30")
_emit_reads_through("l4", "validate_structure", "urg_read_31")
_emit_reads_through("l4", "validate_structure", "urg_read_32")
_emit_reads_through("l4", "validate_structure", "urg_read_33")
_emit_reads_through("l4", "validate_structure", "urg_read_34")
_emit_reads_through("l4", "validate_structure", "urg_read_35")
_emit_reads_through("l4", "validate_structure", "urg_read_36")
SSOT Structure Validator (The Smoke Detector)
============================================
Fast (<5s) structural validation for pre-commit hooks.

This script enforces the "Three Pillars" testing architecture by validating:
1. Files exist only in SSOT-approved locations (structure_blueprint.py)
2. Base agents reside ONLY in agentic_core/base_agents/ (Constitutional Rule)
3. No logic files leak into forbidden directories
4. Test files are properly placed in tests/ hierarchy

USAGE:
    python scripts/validate_structure.py [files...]

EXIT CODES:
    0 - All paths valid
    1 - Structural violations detected

[CONSTITUTIONAL] This script enforces the Base Agent Location Lock rule.
"""

import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    OPS_SCRIPTS_DIR,
    REPORTS_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through
from tqdm import tqdm

VALID_TERRITORIES: frozenset[str] = frozenset(
    {
        AGENTIC_CORE_DIR,
        APPS_RG_DIR,
        APPS_LIC_DIR,
        APPS_SHARED_DIR,
        TESTS_DIR,
        OPS_SCRIPTS_DIR,
        ARCHIVES_DIR,
        "data",
        "docs",
        "logs",
        REPORTS_DIR,
        "scripts",
        ".sovereign_healing_backup",
        ".github",
        ".windsurf",
        ".gravity_state",
        ".backup",
        ".git",
        "temp_quiet_test",
        "temp_verbose_test",
    },
)
APPS_VALID_SUBFOLDERS: frozenset[str] = frozenset(
    {
        "asset_library",
        "core",
        "domain",
        "engines",
        "logic_nodes",
        "shared",
        "system_flow",
        "validation",
        REPORTS_DIR,
        "scripts",
        TOOLS_DIR,
        "agents",
        "common_utils",
        "config",
        "core_components",
        "data",
        "utils",
    },
)
AGENTIC_CORE_VALID_SUBFOLDERS: frozenset[str] = frozenset(
    {
        "base_agents",
        "domain",
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
        "config",
        "schemas",
        "prompt_governance",
        "runtime",
        "utils",
        "patterns",
        "semantic_memory",
        "knowledge",
    },
)
TESTS_VALID_TYPES: frozenset[str] = frozenset(
    {"unit", "integration", "e2e", "fixtures", "guardian", "autogen"},
)
BASE_AGENT_PATTERN = re.compile(".*BaseAgent\\.py$")
BASE_AGENT_CANONICAL_DIR = "agentic_core/base_agents"
FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    ("apps_shared/test_", "Test files must be in tests/unit/apps_shared/"),
    ("apps_rg/test_", "Test files must be in tests/unit/apps_rg/"),
    ("apps_lic/test_", "Test files must be in tests/unit/apps_lic/"),
    ("agentic_core/common/", "Use agentic_core/utils/ instead"),
    ("agentic_core/utils/core_extensions/", "Evicted per CANON_VALIDATION_REGISTRY"),
    ("apps_shared/[A-Z]*Agent.py", "Agents must be in apps_shared/agents/"),
]
ROOT_FORBIDDEN_PATTERNS: list[str] = ["^[A-Z].*Agent\\.py$"]
ROOT_ALLOWED_FILES: frozenset[str] = frozenset(
    {"conftest.py", "setup.py", "AgentTechnicalStatus.py", "NuclearAuditAgent.py"},
)


def validate_base_agent_location(file_path: str) -> tuple[bool, str]:
    """
    [CONSTITUTIONAL] Validate that base agents are in the correct location.

    This rule has two parts:
    1. Core framework base agents (SovereignBaseAgent, layer base agents)
       MUST be in agentic_core/base_agents/
    2. App-specific base agents (prefixed with app name)
       MUST be in their respective apps_* directories

    Note: Test files (test_*BaseAgent.py or in tests/) are excluded from this check.
    """
    path = Path(file_path)
    if not BASE_AGENT_PATTERN.match(path.name):
        return (True, "")
    posix_path = path.as_posix()
    if "tests/" in posix_path or path.name.startswith("test_"):
        return (True, "")
    core_base_agents = {"SovereignBaseAgent.py"}
    if path.name in core_base_agents:
        # guardian: allow-path-string
        if posix_path.startswith(BASE_AGENT_CANONICAL_DIR + "/"):
            return (True, "")
        else:
            return (
                False,
                f"[CONSTITUTIONAL VIOLATION] Core base agent '{path.name}' must reside in {BASE_AGENT_CANONICAL_DIR}/, found in: {file_path}",
            )
    app_prefixes = ["RG", "LIC", "SHARED"]
    for prefix in tqdm(app_prefixes, desc="Processing", unit="item"):
        if path.name.startswith(prefix) and path.name.endswith("BaseAgent.py"):
            expected_app_dir = f"apps_{prefix.lower()}" if prefix != "SHARED" else "apps_shared"
            # guardian: allow-path-string
            if posix_path.startswith(expected_app_dir + "/"):
                return (True, "")
            else:
                return (
                    False,
                    f"[CONSTITUTIONAL VIOLATION] App-specific base agent '{path.name}' must reside in {expected_app_dir}/, found in: {file_path}",
                )
    # guardian: allow-path-string
    if posix_path.startswith(BASE_AGENT_CANONICAL_DIR + "/"):
        return (True, "")
    return (
        False,
        f"[CONSTITUTIONAL VIOLATION] Base agent '{path.name}' must reside in {BASE_AGENT_CANONICAL_DIR}/ or appropriate apps_* directory, found in: {file_path}",
    )


def validate_territory(file_path: str) -> tuple[bool, str]:
    """Validate that file is in a valid top-level territory."""
    path = Path(file_path)
    parts = path.parts
    if len(parts) < 1:
        return (True, "")
    territory = parts[0]
    if territory.startswith("."):
        return (True, "")
    if len(parts) == 1:
        for pattern in ROOT_FORBIDDEN_PATTERNS:
            if re.match(pattern, territory) and territory not in ROOT_ALLOWED_FILES:
                return (False, f"Forbidden file at root: {file_path}")
        return (True, "")
    if territory not in VALID_TERRITORIES:
        return (False, f"Unknown territory '{territory}' in: {file_path}")
    return (True, "")


def validate_subfolder_structure(file_path: str) -> tuple[bool, str]:
    """Validate subfolder structure for apps_* and agentic_core."""
    path = Path(file_path)
    parts = path.parts
    if len(parts) < 2:
        return (True, "")
    territory = parts[0]
    if territory.startswith("apps_"):
        subfolder = parts[1]
        if not subfolder.endswith(".py"):
            if subfolder not in APPS_VALID_SUBFOLDERS:
                return (
                    False,
                    f"Invalid subfolder '{subfolder}' in {territory}: {file_path}. Valid subfolders: {sorted(APPS_VALID_SUBFOLDERS)}",
                )
    if territory == AGENTIC_CORE_DIR:
        subfolder = parts[1]
        if not subfolder.endswith(".py"):
            if subfolder not in AGENTIC_CORE_VALID_SUBFOLDERS:
                return (
                    False,
                    f"Invalid subfolder '{subfolder}' in agentic_core: {file_path}. Valid subfolders: {sorted(AGENTIC_CORE_VALID_SUBFOLDERS)}",
                )
    if territory == TESTS_DIR:
        if len(parts) >= 2:
            test_type = parts[1]
            if not test_type.endswith(".py") and test_type not in TESTS_VALID_TYPES:
                if not test_type.startswith("__"):
                    return (
                        False,
                        f"Invalid test type '{test_type}' in tests/: {file_path}. Valid types: {sorted(TESTS_VALID_TYPES)}",
                    )
    return (True, "")


def validate_forbidden_patterns(file_path: str) -> tuple[bool, str]:
    """Check for forbidden patterns that indicate structural violations."""
    posix_path = Path(file_path).as_posix()
    for pattern, message in FORBIDDEN_PATTERNS:
        if re.search(pattern, posix_path):
            return (False, f"Forbidden pattern detected in {file_path}: {message}")
    return (True, "")


def validate_path(file_path: str) -> list[str]:
    """
    Validate a single file path against all SSOT rules.

    Returns:
        List of error messages (empty if valid)
    """
    errors: list[str] = []
    validators = [
        validate_base_agent_location,
        validate_territory,
        validate_subfolder_structure,
        validate_forbidden_patterns,
    ]
    for validator in validators:
        is_valid, error = validator(file_path)
        if not is_valid:
            errors.append(error)
    return errors


def main() -> int:
    """Main entry point for pre-commit hook."""
    args = sys.argv[1:]
    files = []
    constitutional_only = False
    i = 0
    while i < len(args):
        if args[i] == "--constitutional-only":
            constitutional_only = True
        else:
            files.append(args[i])
        i += 1
    if not files:
        return 0
    all_violations: list[str] = []
    constitutional_violations: list[str] = []
    for file_path in tqdm(files, desc="Processing", unit="item"):
        if constitutional_only:
            is_valid, error = validate_base_agent_location(Path(file_path))
            if not is_valid:
                constitutional_violations.append(error)
        else:
            errors = validate_path(Path(file_path))
            for error in errors:
                if "[CONSTITUTIONAL" in error:
                    constitutional_violations.append(error)
                else:
                    all_violations.append(error)
    if constitutional_violations:
        print("\n" + "=" * 70)
        print("[CONSTITUTIONAL VIOLATION] CRITICAL STRUCTURAL ERRORS")
        print("=" * 70)
        print("These violations CANNOT be overridden and MUST be fixed:")
        print()
        for v in constitutional_violations:
            print(f"  [!!!] {v}")
        print()
        print("=" * 70)
        print("Fix: Move base agents to correct locations:")
        print("  - Core base agents -> agentic_core/base_agents/")
        print("  - App-specific base agents -> respective apps_* directories")
        print("=" * 70 + "\n")
        return 1
    if not constitutional_only and all_violations:
        print("\n" + "=" * 70)
        print("[SSOT STRUCTURE GUARD] STRUCTURAL VIOLATIONS DETECTED")
        print("=" * 70)
        for v in all_violations:
            print(f"  [X] {v}")
        print("=" * 70)
        print("\nFix: Move files to valid SSOT locations per structure_blueprint.py")
        print("=" * 70 + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
