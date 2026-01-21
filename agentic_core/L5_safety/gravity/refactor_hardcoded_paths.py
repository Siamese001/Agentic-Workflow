#!/usr/bin/env python3
"""
Bulk refactor hardcoded paths to use SSOT constants from structure_blueprint.py
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Files to exclude
EXCLUDED_DIRS = {
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "archives",
    "legacy",
    "deprecated",
}

EXCLUDED_FILES = {
    "structure_blueprint.py",  # SSOT definition
    "scan_hardcoded_paths.py",
    "refactor_hardcoded_paths.py",  # This file
}

# SSOT constant mappings (path_pattern -> SSOT_CONSTANT_NAME)
PATH_TO_SSOT_MAP = {
    # Agent discovery files
    r'["\']agent_discovery_full\.json["\']': "AGENT_DISCOVERY_JSON",
    r'["\']agent_discovery_full\.manifest\.json["\']': "AGENT_DISCOVERY_MANIFEST_JSON",
    # Layer directories
    r'["\']agentic_core/L0_maintenance["\']': "L0_MAINTENANCE_DIR",
    r'["\']agentic_core/L1_cognition["\']': "L1_COGNITION_DIR",
    r'["\']agentic_core/L2_execution["\']': "L2_EXECUTION_DIR",
    r'["\']agentic_core/L3_orchestration["\']': "L3_ORCHESTRATION_DIR",
    r'["\']agentic_core/L4_state["\']': "L4_STATE_DIR",
    r'["\']agentic_core/L5_safety["\']': "L5_SAFETY_DIR",
    r'["\']agentic_core/L6_observability["\']': "L6_OBSERVABILITY_DIR",
    # Critical subdirectories
    r'["\']agentic_core/L6_observability/dashboards["\']': "DASHBOARD_DIR",
    r'["\']agentic_core/config/blueprint_sovereign["\']': "BLUEPRINT_SOVEREIGN_DIR",
    r'["\']agentic_core/schemas["\']': "SCHEMAS_DIR",
    r'["\']agentic_core/prompt_governance["\']': "PROMPT_GOVERNANCE_DIR",
    r'["\']agentic_core/utils["\']': "UTILS_DIR",
    r'["\']agentic_core/runtime["\']': "RUNTIME_DIR",
    # Core directories
    r'["\']agentic_core["\']': "AGENTIC_CORE_DIR",
    r'["\']scripts["\']': "SCRIPTS_DIR",
    r'["\']tests/unit["\']': "TESTS_UNIT_DIR",
    r'["\']tests/integration["\']': "TESTS_INTEGRATION_DIR",
    r'["\']tests/e2e["\']': "TESTS_E2E_DIR",
    r'["\']tests["\']': "TESTS_DIR",
    r'["\']apps_rg["\']': "APPS_RG_DIR",
    r'["\']apps_lic["\']': "APPS_LIC_DIR",
    r'["\']apps_shared["\']': "APPS_SHARED_DIR",
    # Output directories
    r'["\']reports["\']': "REPORTS_DIR",
    r'["\']archives["\']': "ARCHIVES_DIR",
}

# Path() constructor patterns
PATH_CONSTRUCTOR_MAP = {
    r'Path\(["\']agent_discovery_full\.json["\']\)': "get_validated_project_root() / AGENT_DISCOVERY_JSON",
    r'Path\(["\']agentic_core/L0_maintenance["\']\)': "get_validated_project_root() / L0_MAINTENANCE_DIR",
    r'Path\(["\']agentic_core/L1_cognition["\']\)': "get_validated_project_root() / L1_COGNITION_DIR",
    r'Path\(["\']agentic_core/L2_execution["\']\)': "get_validated_project_root() / L2_EXECUTION_DIR",
    r'Path\(["\']agentic_core/L3_orchestration["\']\)': "get_validated_project_root() / L3_ORCHESTRATION_DIR",
    r'Path\(["\']agentic_core/L4_state["\']\)': "get_validated_project_root() / L4_STATE_DIR",
    r'Path\(["\']agentic_core/L5_safety["\']\)': "get_validated_project_root() / L5_SAFETY_DIR",
    r'Path\(["\']agentic_core/L6_observability/dashboards["\']\)': "get_validated_project_root() / DASHBOARD_DIR",
    r'Path\(["\']agentic_core["\']\)': "get_validated_project_root() / AGENTIC_CORE_DIR",
    r'Path\(["\']scripts["\']\)': "get_validated_project_root() / SCRIPTS_DIR",
    r'Path\(["\']tests/unit["\']\)': "get_validated_project_root() / TESTS_UNIT_DIR",
    r'Path\(["\']tests["\']\)': "get_validated_project_root() / TESTS_DIR",
}

# Required imports to add
SSOT_IMPORT = """from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)"""


def should_exclude_path(path: Path) -> bool:
    """Check if path should be excluded."""
    parts_lower = {p.lower() for p in path.parts}
    if parts_lower & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    if path.name in EXCLUDED_FILES:
        return True
    return False


def has_ssot_import(content: str) -> bool:
    """Check if file already imports from structure_blueprint."""
    return "from agentic_core.L5_safety.validators.structure_blueprint import" in content


def add_ssot_import(content: str) -> str:
    """Add SSOT import after last existing import."""
    if has_ssot_import(content):
        return content

    lines = content.split("\n")
    last_import_idx = -1

    # Find last import statement
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i

    if last_import_idx >= 0:
        # Insert SSOT import after last import
        lines.insert(last_import_idx + 1, "")
        lines.insert(last_import_idx + 2, SSOT_IMPORT)
        return "\n".join(lines)
    else:
        # No imports found, add at top after docstring/comments
        insert_idx = 0
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
                in_docstring = True
            if in_docstring and (stripped.endswith('"""') or stripped.endswith("'''")):
                insert_idx = i + 1
                break
            if not stripped or stripped.startswith("#"):
                continue
            insert_idx = i
            break

        lines.insert(insert_idx, SSOT_IMPORT)
        lines.insert(insert_idx + 1, "")
        return "\n".join(lines)


def refactor_file(file_path: Path, dry_run: bool = False) -> tuple[bool, int]:
    """Refactor a single file to use SSOT constants.

    Returns:
        (was_modified, num_replacements)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        replacements = 0

        # Skip if already importing from structure_blueprint
        if "structure_blueprint" in content and "import" in content:
            # Already using SSOT, skip
            return False, 0

        # Apply string replacements
        for pattern, constant in PATH_TO_SSOT_MAP.items():
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, constant, content)
                replacements += len(matches)

        # Apply Path() constructor replacements
        for pattern, replacement in PATH_CONSTRUCTOR_MAP.items():
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, replacement, content)
                replacements += len(matches)

        if replacements > 0:
            # Add SSOT import
            content = add_ssot_import(content)

            if not dry_run and content != original_content:
                file_path.write_text(content, encoding="utf-8")

            return True, replacements

        return False, 0

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0


def refactor_repository(dry_run: bool = False) -> dict[str, int]:
    """Refactor entire repository.

    Returns:
        Statistics dict
    """
    print("=" * 80)
    print("HARDCODED PATH REFACTORING" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 80)
    print(f"\n📂 Project: {PROJECT_ROOT}")
    print(
        f"🔄 Mode: {'DRY RUN - No files will be modified' if dry_run else 'LIVE - Files will be modified'}\n"
    )

    stats = {
        "files_scanned": 0,
        "files_modified": 0,
        "total_replacements": 0,
    }

    modified_files = []

    # Scan all Python files
    # Operation Zero: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files

    for py_file in get_python_files(PROJECT_ROOT):
        if should_exclude_path(py_file):
            continue

        stats["files_scanned"] += 1
        was_modified, num_replacements = refactor_file(py_file, dry_run)

        if was_modified:
            stats["files_modified"] += 1
            stats["total_replacements"] += num_replacements
            rel_path = py_file.relative_to(PROJECT_ROOT)
            modified_files.append((rel_path, num_replacements))

    # Print results
    print("\n" + "=" * 80)
    print("REFACTORING SUMMARY")
    print("=" * 80)
    print(f"Files scanned:      {stats['files_scanned']}")
    print(f"Files modified:     {stats['files_modified']}")
    print(f"Total replacements: {stats['total_replacements']}")
    print()

    if modified_files:
        print("Top 20 Modified Files:")
        print("-" * 80)
        for file_path, count in sorted(modified_files, key=lambda x: -x[1])[:20]:
            print(f"   {str(file_path):60} {count:4} replacements")

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Refactor hardcoded paths to SSOT")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--live", action="store_true", help="Actually modify files (requires explicit flag)"
    )
    args = parser.parse_args()

    if not args.dry_run and not args.live:
        print("❌ ERROR: Must specify either --dry-run or --live")
        print("   Use --dry-run to preview changes")
        print("   Use --live to actually modify files")
        return 1

    dry_run = args.dry_run
    stats = refactor_repository(dry_run=dry_run)

    print("\n" + "=" * 80)
    if dry_run:
        print("✅ DRY RUN COMPLETE - No files were modified")
        print("   Run with --live to apply changes")
    else:
        print("✅ REFACTORING COMPLETE")
        print(f"   Modified {stats['files_modified']} files")
        print(f"   Made {stats['total_replacements']} replacements")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
