#!/usr/bin/env python3
"""
Standardize base agent naming with L# prefix throughout codebase.

Current -> New:
- L0RoutingBaseAgent -> L0RoutingBaseAgent
- L1CognitionBase -> L1CognitionBase
- L2ExecutionBase -> (already has L# prefix, keep as is)
- L3OrchestrationBase -> L3L3OrchestrationBase
- L4StateBase -> L4L4StateBase
- L5SafetyBase -> L5L5SafetyBase
- L6ObservabilityBase -> (already has L# prefix, keep as is)

This script:
1. Renames class definitions
2. Updates all imports
3. Updates all references in code and docs
4. Regenerates agent discovery
"""

from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

PROJECT_ROOT = Path(__file__).parent.parent

# Mapping of old names to new names
RENAME_MAP = {
    # Class name changes - Phase 2: L0 and L1 only
    "L0RoutingBaseAgent": "L0RoutingBaseAgent",
    "L1CognitionBase": "L1CognitionBase",
}

# File renames (old path -> new path, relative to PROJECT_ROOT)
FILE_RENAMES = {
    "agentic_core/L0_routing/scripts/L0RoutingBaseAgent.py": "agentic_core/L0_routing/scripts/L0RoutingBaseAgent.py",
    "agentic_core/L1_cognition/thought_engine/L1CognitionBase.py": "agentic_core/L1_cognition/thought_engine/L1CognitionBase.py",
}

# Extensions to process
CODE_EXTENSIONS = {".py", ".md", ".json", ".html", ".txt"}

# Directories to skip
SKIP_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def find_files_to_update(root: Path) -> list[Path]:
    """Find all files that may need updating."""
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files

    files = list(get_python_files(root)) + list(
        get_data_files(root, extensions=[".json", ".md", ".yaml", ".yml"]),
    )

    # Filter by CODE_EXTENSIONS and skip directories
    filtered_files = []
    for path in files:
        if path.is_file() and path.suffix in CODE_EXTENSIONS:
            if not any(skip in path.parts for skip in SKIP_DIRS):
                filtered_files.append(path)
    return filtered_files


def update_file_content(
    file_path: Path,
    rename_map: dict[str, str],
    dry_run: bool = True,
) -> tuple[bool, int]:
    """Update file content with new names. Returns (changed, count)."""
    try:
        content = file_path.read_text(encoding="utf-8")
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"  ⚠️  Could not read {file_path}: {e}")
        return False, 0

    original = content
    changes = 0

    for old_name, new_name in rename_map.items():
        if old_name in content:
            count = content.count(old_name)
            content = content.replace(old_name, new_name)
            changes += count

    if content != original:
        if not dry_run:
            file_path.write_text(content, encoding="utf-8")
        return True, changes

    return False, 0


def rename_files(file_renames: dict[str, str], dry_run: bool = True) -> list[str]:
    """Rename files. Returns list of renamed files."""
    renamed = []
    for old_path, new_path in file_renames.items():
        old_full = PROJECT_ROOT / old_path
        new_full = PROJECT_ROOT / new_path

        if old_full.exists():
            if dry_run:
                print(f"  Would rename: {old_path} -> {new_path}")
            else:
                old_full.rename(new_full)
                print(f"  Renamed: {old_path} -> {new_path}")
            renamed.append(old_path)
        else:
            print(f"  ⚠️  File not found: {old_path}")

    return renamed


def main(dry_run: bool = True):
    """Main execution."""
    mode = "DRY RUN" if dry_run else "LIVE"
    print("=" * 70)
    print(f"Base Agent Name Standardization ({mode})")
    print("=" * 70)

    print("\nRename Map:")
    for old, new in RENAME_MAP.items():
        print(f"  {old} -> {new}")

    # Step 1: Find files to update
    print("\nScanning files...")
    files = find_files_to_update(PROJECT_ROOT)
    print(f"  Found {len(files)} files to scan")

    # Step 2: Update file contents
    print("\nUpdating file contents...")
    updated_files = []
    total_changes = 0

    for file_path in files:
        changed, count = update_file_content(file_path, RENAME_MAP, dry_run)
        if changed:
            updated_files.append((file_path, count))
            total_changes += count
            if count > 0:
                rel_path = file_path.relative_to(PROJECT_ROOT)
                print(f"  {'Would update' if dry_run else 'Updated'}: {rel_path} ({count} changes)")

    # Step 3: Rename files
    print("\nRenaming files...")
    renamed = rename_files(FILE_RENAMES, dry_run)

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Files updated: {len(updated_files)}")
    print(f"  Total replacements: {total_changes}")
    print(f"  Files renamed: {len(renamed)}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No changes were made.")
        print("   Run with --live to apply changes.")
    else:
        print("\n✅ Changes applied successfully!")
        print("   Run agent discovery and tests to verify.")

    print("=" * 70)

    return len(updated_files), total_changes, len(renamed)


if __name__ == "__main__":
    import sys

    dry_run = "--live" not in sys.argv
    main(dry_run)
