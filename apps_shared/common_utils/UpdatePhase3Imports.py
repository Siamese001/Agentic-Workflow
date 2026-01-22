#!/usr/bin/env python3
"""
update_phase3_imports.py - Phase 3 Global Search & Replace

Updates all imports of archived legacy managers and enforcers to use unified agents.

Usage:
    python scripts/update_phase3_imports.py --dry-run
    python scripts/update_phase3_imports.py
"""


import argparse
import re
import sys

PROJECT_ROOT = Path(__file__).parent.parent

# Import replacement mapping
IMPORT_REPLACEMENTS: dict[str, tuple[str, str]] = {
    # Resource Managers -> UnifiedResourceManagerAgent
    "BudgetManagerAgent": (
        "agentic_core.L5_safety.unified.UnifiedResourceManagerAgent",
        "UnifiedResourceManagerAgent",
    ),
    "ProactiveResourceManagerAgent": (
        "agentic_core.L5_safety.unified.UnifiedResourceManagerAgent",
        "UnifiedResourceManagerAgent",
    ),
    "FallbackManagerAgent": (
        "agentic_core.L5_safety.unified.UnifiedResourceManagerAgent",
        "UnifiedResourceManagerAgent",
    ),
    # Security Managers -> UnifiedSecurityManagerAgent
    "AgentPermissionManagerAgent": (
        "agentic_core.L5_safety.unified.UnifiedSecurityManagerAgent",
        "UnifiedSecurityManagerAgent",
    ),
    "SecureCheckpointManagerAgent": (
        "agentic_core.L5_safety.unified.UnifiedSecurityManagerAgent",
        "UnifiedSecurityManagerAgent",
    ),
    "SecureConfigManagerAgent": (
        "agentic_core.L5_safety.unified.UnifiedSecurityManagerAgent",
        "UnifiedSecurityManagerAgent",
    ),
    # Code Enforcers -> UnifiedCodeEnforcerAgent
    "CodeSSOTEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent",
        "UnifiedCodeEnforcerAgent",
    ),
    "CodeStandardsEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent",
        "UnifiedCodeEnforcerAgent",
    ),
    "PatternEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent",
        "UnifiedCodeEnforcerAgent",
    ),
    "TypeEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent",
        "UnifiedCodeEnforcerAgent",
    ),
    "PythonFileSovereigntyEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent",
        "UnifiedCodeEnforcerAgent",
    ),
    # Structure Enforcers -> UnifiedStructureEnforcerAgent
    "GravityEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent",
        "UnifiedStructureEnforcerAgent",
    ),
    "HierarchyEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent",
        "UnifiedStructureEnforcerAgent",
    ),
    "NamingEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent",
        "UnifiedStructureEnforcerAgent",
    ),
    "DocEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent",
        "UnifiedStructureEnforcerAgent",
    ),
    "ASCIIEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent",
        "UnifiedStructureEnforcerAgent",
    ),
    "StrictDocEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent",
        "UnifiedStructureEnforcerAgent",
    ),
    "PascalSovereigntyEnforcerAgent": (
        "agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent",
        "UnifiedStructureEnforcerAgent",
    ),
}


def find_files_with_imports(root: Path) -> list[Path]:
    """Find all Python files that might have legacy imports."""
    files = []
    for path in root.rglob("*.py"):
        path_str = str(path).lower()
        if "archive" in path_str:
            continue
        if "__pycache__" in path_str:
            continue
        files.append(path)
    return files


def update_imports_in_file(file_path: Path, dry_run: bool = False) -> list[str]:
    """Update legacy imports in a single file."""
    changes = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return changes

    original_content = content

    for legacy_name, (unified_module, unified_class) in IMPORT_REPLACEMENTS.items():
        # Pattern: from ... import LegacyAgent
        pattern = rf"from\s+[\w.]+\s+import\s+{legacy_name}\b"
        if re.search(pattern, content):
            new_import = f"from {unified_module} import {unified_class}"
            content = re.sub(pattern, new_import, content)
            changes.append(f"Updated import: {legacy_name} -> {unified_class}")

        # Replace usage if import was updated
        if any(legacy_name in c for c in changes):
            usage_pattern = rf"\b{legacy_name}\b"
            if re.search(usage_pattern, content):
                content = re.sub(usage_pattern, unified_class, content)
                changes.append(f"Updated usage: {legacy_name} -> {unified_class}")

    if content != original_content and not dry_run:
        file_path.write_text(content, encoding="utf-8")

    return changes


def main():
    parser = argparse.ArgumentParser(description="Update Phase 3 legacy imports")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    print("=" * 70)
    print("Phase 3 Global Search & Replace - Manager/Enforcer Import Updates")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN MODE]\n")

    files = find_files_with_imports(PROJECT_ROOT)
    total_changes = 0
    files_modified = 0

    for file_path in files:
        changes = update_imports_in_file(file_path, args.dry_run)
        if changes:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            print(f"\n{rel_path}:")
            for change in changes:
                print(f"  - {change}")
            total_changes += len(changes)
            files_modified += 1

    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Files scanned:  {len(files)}")
    print(f"  Files modified: {files_modified}")
    print(f"  Total changes:  {total_changes}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n✓ PHASE 3 IMPORT UPDATES COMPLETE")

    return 0


if __name__ == "__main__":
    sys.exit(main())