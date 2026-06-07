#!/usr/bin/env python3
"""Validate repository paths against basic SSOT territory and structural rules.

This is a fast path validator suitable for pre-commit style checks. It accepts a
list of file paths and reports constitutional violations separately from general
territory violations.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

try:
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR as _AGENTIC_CORE_DIR,
        APPS_LIC_DIR as _APPS_LIC_DIR,
        APPS_RG_DIR as _APPS_RG_DIR,
        APPS_SHARED_DIR as _APPS_SHARED_DIR,
        ARCHIVES_DIR as _ARCHIVES_DIR,
        OPS_SCRIPTS_DIR as _OPS_SCRIPTS_DIR,
        REPORTS_DIR as _REPORTS_DIR,
        TESTS_DIR as _TESTS_DIR,
        TOOLS_DIR as _TOOLS_DIR,
    )
except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
    _AGENTIC_CORE_DIR = "agentic_core"
    _APPS_LIC_DIR = "apps_lic"
    _APPS_RG_DIR = "apps_rg"
    _APPS_SHARED_DIR = "apps_shared"
    _ARCHIVES_DIR = "archives"
    _OPS_SCRIPTS_DIR = "ops_scripts"
    _REPORTS_DIR = "reports"
    _TESTS_DIR = "tests"
    _TOOLS_DIR = "tools"

VALID_TERRITORIES = frozenset(
    {
        _AGENTIC_CORE_DIR,
        _APPS_RG_DIR,
        _APPS_LIC_DIR,
        _APPS_SHARED_DIR,
        _TESTS_DIR,
        _OPS_SCRIPTS_DIR,
        _ARCHIVES_DIR,
        _REPORTS_DIR,
        _TOOLS_DIR,
        "data",
        "docs",
        "logs",
        "scripts",
        ".github",
        "docs/archive/windsurf/legacy-tree",
        ".backup",
        ".git",
        ".sovereign_healing_backup",
        ".gravity_state",
    }
)
APPS_VALID_SUBFOLDERS = frozenset(
    {
        "agents",
        "asset_library",
        "common_utils",
        "config",
        "core",
        "core_components",
        "data",
        "domain",
        "engines",
        "logic_nodes",
        _REPORTS_DIR,
        "scripts",
        "shared",
        "system_flow",
        _TOOLS_DIR,
        "utils",
        "validation",
    }
)
AGENTIC_CORE_VALID_SUBFOLDERS = frozenset(
    {
        "base_agents",
        "config",
        "domain",
        "knowledge",
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
        "patterns",
        "prompt_governance",
        "runtime",
        "schemas",
        "semantic_memory",
        "utils",
    }
)
TESTS_VALID_TYPES = frozenset({"unit", "integration", "e2e", "fixtures", "guardian", "autogen"})
BASE_AGENT_PATTERN = re.compile(r".*BaseAgent\.py$")
BASE_AGENT_CANONICAL_DIR = f"{_AGENTIC_CORE_DIR}/base_agents"
FORBIDDEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(rf"^{re.escape(_APPS_SHARED_DIR)}/test_"),
        f"Test files must be in {_TESTS_DIR}/unit/{_APPS_SHARED_DIR}/",
    ),
    (
        re.compile(rf"^{re.escape(_APPS_RG_DIR)}/test_"),
        f"Test files must be in {_TESTS_DIR}/unit/{_APPS_RG_DIR}/",
    ),
    (
        re.compile(rf"^{re.escape(_APPS_LIC_DIR)}/test_"),
        f"Test files must be in {_TESTS_DIR}/unit/{_APPS_LIC_DIR}/",
    ),
    (re.compile(rf"^{re.escape(_AGENTIC_CORE_DIR)}/common/"), f"Use {_AGENTIC_CORE_DIR}/utils/ instead"),
    (
        re.compile(rf"^{re.escape(_AGENTIC_CORE_DIR)}/utils/core_extensions/"),
        "Evicted per validation registry",
    ),
    (
        re.compile(rf"^{re.escape(_APPS_SHARED_DIR)}/[A-Z].*Agent\.py$"),
        f"Agents must be in {_APPS_SHARED_DIR}/agents/",
    ),
]
ROOT_FORBIDDEN_PATTERNS = [re.compile(r"^[A-Z].*Agent\.py$")]
ROOT_ALLOWED_FILES = frozenset({"conftest.py", "setup.py", "AgentTechnicalStatus.py", "NuclearAuditAgent.py"})


def _normalize_path(file_path: str | Path) -> str:
    path = Path(file_path)
    try:
        root = _resolve_project_root()
        if path.is_absolute():
            path = path.resolve().relative_to(root)
    except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
        pass
    return path.as_posix()


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / _AGENTIC_CORE_DIR).exists():
            return candidate

    return Path.cwd().resolve()


def validate_base_agent_location(file_path: str | Path) -> tuple[bool, str]:
    path = Path(_normalize_path(file_path))
    if not BASE_AGENT_PATTERN.match(path.name):
        return True, ""
    if f"{_TESTS_DIR}/" in path.as_posix() or path.name.startswith("test_"):
        return True, ""

    if path.name == "SovereignBaseAgent.py":
        if path.as_posix().startswith(BASE_AGENT_CANONICAL_DIR + "/"):
            return True, ""
        return (
            False,
            f"[CONSTITUTIONAL VIOLATION] Core base agent must be under {BASE_AGENT_CANONICAL_DIR}/: {path}",
        )

    if path.name.startswith("RG") and path.name.endswith("BaseAgent.py"):
        return (
            path.as_posix().startswith(f"{_APPS_RG_DIR}/"),
            f"[CONSTITUTIONAL VIOLATION] RG base agent must be under {_APPS_RG_DIR}/: {path}",
        )
    if path.name.startswith("LIC") and path.name.endswith("BaseAgent.py"):
        return (
            path.as_posix().startswith(f"{_APPS_LIC_DIR}/"),
            f"[CONSTITUTIONAL VIOLATION] LIC base agent must be under {_APPS_LIC_DIR}/: {path}",
        )
    if path.name.startswith("SHARED") and path.name.endswith("BaseAgent.py"):
        return (
            path.as_posix().startswith(f"{_APPS_SHARED_DIR}/"),
            f"[CONSTITUTIONAL VIOLATION] SHARED base agent must be under {_APPS_SHARED_DIR}/: {path}",
        )

    if path.as_posix().startswith(BASE_AGENT_CANONICAL_DIR + "/"):
        return True, ""
    return (
        False,
        f"[CONSTITUTIONAL VIOLATION] Base agent must reside in {BASE_AGENT_CANONICAL_DIR}/ or appropriate apps_* directory: {path}",
    )


def validate_territory(file_path: str | Path) -> tuple[bool, str]:
    path = Path(_normalize_path(file_path))
    parts = path.parts
    if not parts:
        return True, ""
    territory = parts[0]
    if territory.startswith("."):
        return True, ""
    if len(parts) == 1:
        for pattern in ROOT_FORBIDDEN_PATTERNS:
            if pattern.match(territory) and territory not in ROOT_ALLOWED_FILES:
                return False, f"Forbidden file at repository root: {territory}"
        return True, ""
    if territory not in VALID_TERRITORIES:
        return False, f"Unknown territory '{territory}' in {path}"
    return True, ""


def validate_subfolder_structure(file_path: str | Path) -> tuple[bool, str]:
    path = Path(_normalize_path(file_path))
    parts = path.parts
    if len(parts) < 2:
        return True, ""

    territory, subfolder = parts[0], parts[1]
    if (
        territory.startswith("apps_")
        and not subfolder.endswith(".py")
        and subfolder not in APPS_VALID_SUBFOLDERS
    ):
        return False, f"Invalid subfolder '{subfolder}' in {territory}: {path}"
    if (
        territory == _AGENTIC_CORE_DIR
        and not subfolder.endswith(".py")
        and subfolder not in AGENTIC_CORE_VALID_SUBFOLDERS
    ):
        return False, f"Invalid subfolder '{subfolder}' in {_AGENTIC_CORE_DIR}: {path}"
    if (
        territory == _TESTS_DIR
        and not subfolder.endswith(".py")
        and not subfolder.startswith("__")
        and subfolder not in TESTS_VALID_TYPES
    ):
        return False, f"Invalid test type '{subfolder}' in {_TESTS_DIR}: {path}"
    return True, ""


def validate_forbidden_patterns(file_path: str | Path) -> tuple[bool, str]:
    posix_path = _normalize_path(file_path)
    for pattern, message in FORBIDDEN_PATTERNS:
        if pattern.search(posix_path):
            return False, f"Forbidden pattern in {posix_path}: {message}"
    return True, ""


def validate_path(file_path: str | Path) -> list[str]:
    errors: list[str] = []
    for validator in (
        validate_base_agent_location,
        validate_territory,
        validate_subfolder_structure,
        validate_forbidden_patterns,
    ):
        is_valid, message = validator(file_path)
        if not is_valid:
            errors.append(message)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Files to validate.")
    parser.add_argument(
        "--constitutional-only", action="store_true", help="Only enforce base-agent location rules."
    )
    args = parser.parse_args(argv)

    if not args.files:
        return 0

    constitutional_violations: list[str] = []
    general_violations: list[str] = []

    for file_path in args.files:
        if args.constitutional_only:
            is_valid, message = validate_base_agent_location(file_path)
            if not is_valid:
                constitutional_violations.append(message)
            continue

        for message in validate_path(file_path):
            if "[CONSTITUTIONAL VIOLATION]" in message:
                constitutional_violations.append(message)
            else:
                general_violations.append(message)

    if constitutional_violations:
        print("\n" + "=" * 70)
        print("[CONSTITUTIONAL VIOLATION] CRITICAL STRUCTURAL ERRORS")
        print("=" * 70)
        for violation in constitutional_violations:
            print(f"  [!!!] {violation}")
        print("=" * 70 + "\n")
        return 1

    if general_violations and not args.constitutional_only:
        print("\n" + "=" * 70)
        print("[SSOT STRUCTURE GUARD] STRUCTURAL VIOLATIONS DETECTED")
        print("=" * 70)
        for violation in general_violations:
            print(f"  [X] {violation}")
        print("=" * 70 + "\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
