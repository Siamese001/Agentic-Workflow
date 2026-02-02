from __future__ import annotations

"""
Utility to automate the migration from deep imports to clean SSOT paths.

Phase 5: Repository-Wide Import Migration

This script updates imports across the codebase to use the new SSOT patterns:
- agentic_core.config for constants/registry
- agentic_core.unified for unified agents
- agentic_core.utils.core_extensions.healer_mixin for HealerMixin

Usage:
    python -m agentic_core.L0_maintenance.scripts.migrate_imports --dry-run
    python -m agentic_core.L0_maintenance.scripts.migrate_imports --apply
"""


import argparse
import re
from pathlib import Path

from agentic_core.utils.file_utils_validator import safe_read_file, safe_write_file
from agentic_core.utils.project_root import get_project_root
from agentic_core.utils.ssot_discovery_validator import get_python_files

# Migration patterns: (regex_pattern, replacement)
MIGRATION_MAP: dict[str, str] = {
    # Structure blueprint -> config
    r"from agentic_core\.L5_safety\.validators\.structure_blueprint_config import": "from agentic_core.config import",
    # Unified agents -> unified API
    r"from agentic_core\.L5_safety\.unified\.code_validator_agent_types import CodeValidatorAgent": "from agentic_core.unified import CodeValidatorAgent",
    r"from agentic_core\.L5_safety\.unified\.StructureValidatorAgent import StructureValidatorAgent": "from agentic_core.unified import StructureValidatorAgent",
    r"from agentic_core\.L5_safety\.unified\.code_enforcer_agent_types import CodeEnforcerAgent": "from agentic_core.unified import CodeEnforcerAgent",
    r"from agentic_core\.L5_safety\.unified\.structure_enforcer_agent_types import StructureEnforcerAgent": "from agentic_core.unified import StructureEnforcerAgent",
    r"from agentic_core\.L5_safety\.unified\.resource_manager_agent_types import ResourceManagerAgent": "from agentic_core.unified import ResourceManagerAgent",
    # HealerMixin -> SSOT location
    r"from agentic_core\.L5_safety\.validators\.healer_mixin import": "from agentic_core.base_agents.healer_mixin import",
    r"from agentic_core\.L5_safety\.guardrails\.healer_mixin import": "from agentic_core.base_agents.healer_mixin import",
    r"from agentic_core\.common\.healing\.healer_mixin import": "from agentic_core.base_agents.healer_mixin import",
}

# Files to skip during migration
SKIP_FILES = {
    "migrate_imports.py",
    "test_phase5_migration.py",
    "__init__.py",  # Package inits may have intentional re-exports
}


def migrate_file(file_path: Path, dry_run: bool = True) -> tuple[bool, list[str]]:
    """
    Migrate imports in a single file.

    Args:
        file_path: Path to the Python file
        dry_run: If True, don't write changes

    Returns:
        Tuple of (was_modified, list_of_changes)
    """
    content = safe_read_file(file_path)
    if content is None:
        return False, []

    original_content = content
    changes = []

    for pattern, replacement in MIGRATION_MAP.items():
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append(f"  {pattern} -> {replacement}")

    if content != original_content:
        if not dry_run:
            safe_write_file(file_path, content)
        return True, changes

    return False, []


def migrate_repo(dry_run: bool = True) -> dict[str, list[str]]:
    """
    Migrate all Python files in the repository.

    Args:
        dry_run: If True, only report changes without applying

    Returns:
        Dict mapping file paths to their changes
    """
    root = get_project_root()
    files = get_python_files(root)

    results = {}

    for file_path in files:
        # Skip certain files
        if file_path.name in SKIP_FILES:
            continue

        was_modified, changes = migrate_file(file_path, dry_run=dry_run)

        if was_modified:
            results[str(file_path)] = changes

    return results


def main():
    parser = argparse.ArgumentParser(description="Migrate imports to SSOT patterns")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show changes without applying (default)",
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes to files")
    args = parser.parse_args()

    dry_run = not args.apply

    print(f"{'DRY RUN' if dry_run else 'APPLYING CHANGES'}: Migrating imports...")

    results = migrate_repo(dry_run=dry_run)

    if results:
        print(f"\n{'Would modify' if dry_run else 'Modified'} {len(results)} files:\n")
        for file_path, changes in results.items():
            print(f"  {file_path}")
            for change in changes:
                print(f"    {change}")
    else:
        print("\nNo files need migration.")

    if dry_run and results:
        print("\nRun with --apply to apply changes.")


if __name__ == "__main__":
    main()
