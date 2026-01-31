#!/usr/bin/env python3
"""
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

# =============================================================================
# SSOT CONSTANTS (Derived from structure_blueprint.py)
# =============================================================================

# Valid top-level directories (Sovereign Territories)
VALID_TERRITORIES: frozenset[str] = frozenset(
    {
        "agentic_core",
        "apps_rg",
        "apps_lic",
        "apps_shared",
        "tests",
        "ops_scripts",
        "archives",
        "data",
        "docs",
        "logs",
        "reports",
        "scripts",
        ".sovereign_healing_backup",
        ".github",
        ".windsurf",
        ".gravity_state",
        ".backup",
        ".git",
        "temp_quiet_test",
        "temp_verbose_test",
    }
)

# Valid subfolders for apps_* directories (depth 2)
APPS_VALID_SUBFOLDERS: frozenset[str] = frozenset(
    {
        # apps_rg
        "asset_library",
        "core",
        "domain",
        "engines",
        "logic_nodes",
        "shared",
        "system_flow",
        "validation",
        # apps_lic
        "reports",
        "scripts",
        "tools",
        # apps_shared
        "agents",
        "common_utils",
        "config",
        "core_components",
        "data",
        "utils",
    }
)

# Valid subfolders for agentic_core (depth 2)
AGENTIC_CORE_VALID_SUBFOLDERS: frozenset[str] = frozenset(
    {
        "base_agents",
        "domain",
        "L0_maintenance",
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
    }
)

# Valid test type directories (tests/TYPE/...)
TESTS_VALID_TYPES: frozenset[str] = frozenset(
    {
        "unit",
        "integration",
        "e2e",
        "fixtures",
        "guardian",
        "autogen",
    }
)

# =============================================================================
# CONSTITUTIONAL RULES (NEVER VIOLATE)
# =============================================================================

# [CONSTITUTIONAL] Base agents MUST reside in agentic_core/base_agents/
BASE_AGENT_PATTERN = re.compile(r".*BaseAgent\.py$")
BASE_AGENT_CANONICAL_DIR = "agentic_core/base_agents"

# Forbidden patterns that indicate "Path Rot"
FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    # No test files in app roots
    ("apps_shared/test_", "Test files must be in tests/unit/apps_shared/"),
    ("apps_rg/test_", "Test files must be in tests/unit/apps_rg/"),
    ("apps_lic/test_", "Test files must be in tests/unit/apps_lic/"),
    # No logic in forbidden locations
    ("agentic_core/common/", "Use agentic_core/utils/ instead"),
    ("agentic_core/utils/core_extensions/", "Evicted per CANON_VALIDATION_REGISTRY"),
    # No agents in apps_shared (they belong in apps_shared/agents/)
    ("apps_shared/[A-Z]*Agent.py", "Agents must be in apps_shared/agents/"),
]

# Files that should NEVER exist at project root (except allowed ones)
ROOT_FORBIDDEN_PATTERNS: list[str] = [
    r"^[A-Z].*Agent\.py$",  # No agents at root (except specific allowed ones)
]

# Allowed root-level Python files (exceptions)
ROOT_ALLOWED_FILES: frozenset[str] = frozenset(
    {
        "conftest.py",
        "setup.py",
        "AgentTechnicalStatus.py",  # Legacy - to be migrated
        "NuclearAuditAgent.py",  # Legacy - to be migrated
    }
)


def validate_base_agent_location(file_path: str) -> tuple[bool, str]:
    """
    [CONSTITUTIONAL] Validate that base agents are in the correct location.

    This rule has two parts:
    1. Core framework base agents (SovereignBaseAgent, layer base agents)
       MUST be in agentic_core/base_agents/
    2. App-specific base agents (prefixed with app name)
       MUST be in their respective apps_* directories
    """
    path = Path(file_path)

    if not BASE_AGENT_PATTERN.match(path.name):
        return True, ""

    posix_path = path.as_posix()

    # Core framework base agents - MUST be in agentic_core/base_agents/
    core_base_agents = {
        "SovereignBaseAgent.py",
        # Layer base agents would go here if they exist
        # "L0BaseAgent.py", "L1BaseAgent.py", etc.
    }

    if path.name in core_base_agents:
        if posix_path.startswith(BASE_AGENT_CANONICAL_DIR + "/"):
            return True, ""
        else:
            return False, (
                f"[CONSTITUTIONAL VIOLATION] Core base agent '{path.name}' must reside in "
                f"{BASE_AGENT_CANONICAL_DIR}/, found in: {file_path}"
            )

    # App-specific base agents - MUST be in their respective apps_* directories
    app_prefixes = ["RG", "LIC", "SHARED"]
    for prefix in app_prefixes:
        if path.name.startswith(prefix) and path.name.endswith("BaseAgent.py"):
            # Find the expected app directory
            expected_app_dir = f"apps_{prefix.lower()}" if prefix != "SHARED" else "apps_shared"
            if posix_path.startswith(expected_app_dir + "/"):
                return True, ""
            else:
                return False, (
                    f"[CONSTITUTIONAL VIOLATION] App-specific base agent "
                    f"'{path.name}' must reside in {expected_app_dir}/, "
                    f"found in: {file_path}"
                )

    # For any other base agents, default to agentic_core/base_agents/
    if posix_path.startswith(BASE_AGENT_CANONICAL_DIR + "/"):
        return True, ""

    return False, (
        f"[CONSTITUTIONAL VIOLATION] Base agent '{path.name}' must reside in "
        f"{BASE_AGENT_CANONICAL_DIR}/ or appropriate apps_* directory, found in: {file_path}"
    )


def validate_territory(file_path: str) -> tuple[bool, str]:
    """Validate that file is in a valid top-level territory."""
    path = Path(file_path)
    parts = path.parts

    if len(parts) < 1:
        return True, ""

    territory = parts[0]

    # Hidden directories starting with . are generally allowed
    if territory.startswith("."):
        return True, ""

    # Root-level files are allowed (pyproject.toml, README.md, etc.)
    if len(parts) == 1:
        # Check for forbidden root patterns
        for pattern in ROOT_FORBIDDEN_PATTERNS:
            if re.match(pattern, territory) and territory not in ROOT_ALLOWED_FILES:
                return False, f"Forbidden file at root: {file_path}"
        return True, ""

    if territory not in VALID_TERRITORIES:
        return False, f"Unknown territory '{territory}' in: {file_path}"

    return True, ""


def validate_subfolder_structure(file_path: str) -> tuple[bool, str]:
    """Validate subfolder structure for apps_* and agentic_core."""
    path = Path(file_path)
    parts = path.parts

    if len(parts) < 2:
        return True, ""

    territory = parts[0]

    # Validate apps_* subfolder structure
    if territory.startswith("apps_"):
        subfolder = parts[1]
        # Allow __init__.py and similar at depth 1
        if not subfolder.endswith(".py"):
            if subfolder not in APPS_VALID_SUBFOLDERS:
                return False, (
                    f"Invalid subfolder '{subfolder}' in {territory}: {file_path}. "
                    f"Valid subfolders: {sorted(APPS_VALID_SUBFOLDERS)}"
                )

    # Validate agentic_core subfolder structure
    if territory == "agentic_core":
        subfolder = parts[1]
        if not subfolder.endswith(".py"):
            if subfolder not in AGENTIC_CORE_VALID_SUBFOLDERS:
                return False, (
                    f"Invalid subfolder '{subfolder}' in agentic_core: {file_path}. "
                    f"Valid subfolders: {sorted(AGENTIC_CORE_VALID_SUBFOLDERS)}"
                )

    # Validate tests structure
    if territory == "tests":
        if len(parts) >= 2:
            test_type = parts[1]
            if not test_type.endswith(".py") and test_type not in TESTS_VALID_TYPES:
                # Allow __pycache__ and similar
                if not test_type.startswith("__"):
                    return False, (
                        f"Invalid test type '{test_type}' in tests/: {file_path}. "
                        f"Valid types: {sorted(TESTS_VALID_TYPES)}"
                    )

    return True, ""


def validate_forbidden_patterns(file_path: str) -> tuple[bool, str]:
    """Check for forbidden patterns that indicate structural violations."""
    posix_path = Path(file_path).as_posix()

    for pattern, message in FORBIDDEN_PATTERNS:
        if re.search(pattern, posix_path):
            return False, f"Forbidden pattern detected in {file_path}: {message}"

    return True, ""


def validate_path(file_path: str) -> list[str]:
    """
    Validate a single file path against all SSOT rules.

    Returns:
        List of error messages (empty if valid)
    """
    errors: list[str] = []

    # Run all validators
    validators = [
        validate_base_agent_location,  # Constitutional - runs first
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

    # Parse arguments
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

    for file_path in files:
        if constitutional_only:
            # Only check constitutional rule
            is_valid, error = validate_base_agent_location(Path(file_path))
            if not is_valid:
                constitutional_violations.append(error)
        else:
            # Check all validators
            errors = validate_path(Path(file_path))
            for error in errors:
                if "[CONSTITUTIONAL" in error:
                    constitutional_violations.append(error)
                else:
                    all_violations.append(error)

    # Constitutional violations are CRITICAL
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

    # Regular violations (only if not constitutional-only)
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
