#!/usr/bin/env python3
"""Pascal Sovereignty Fixer - Comprehensive snake_case to PascalCase converter.

Converts all snake_case class definitions to PascalCase and updates references.
"""
import ast
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

from agentic_core.L5_safety.validators.structure_blueprint import (
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
)
from agentic_core.utils.sovereign_index import SovereignIndex


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('_'))


def find_snake_case_classes(repo_root: Path, target_prefixes: List[str]) -> Dict[str, str]:
    """Find all snake_case class definitions and build rename mapping."""
    mapping = {}

    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for path in get_python_files(repo_root):
        if not any(prefix in str(path) for prefix in target_prefixes):
            continue
        try:
            content = path.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name[0].islower():
                pascal = snake_to_pascal(node.name)
                mapping[node.name] = pascal

    return mapping


def fix_file(path: Path, mapping: Dict[str, str], dry_run: bool = False) -> Tuple[bool, List[str]]:
    """Fix a single file by renaming classes and references."""
    try:
        content = path.read_text(encoding='utf-8')
        original = content
    except (UnicodeDecodeError, FileNotFoundError):
        return False, []

    changes = []

    # Sort by length (longest first) to avoid partial replacements
    sorted_mapping = sorted(mapping.items(), key=lambda x: -len(x[0]))

    for snake, pascal in sorted_mapping:
        # Replace class definitions
        pattern_class = rf'\bclass\s+{re.escape(snake)}\s*(\(|:)'
        if re.search(pattern_class, content):
            content = re.sub(pattern_class, f'class {pascal}\\1', content)
            changes.append(f'class {snake} -> {pascal}')

        # Replace references (whole word only)
        pattern_ref = rf'\b{re.escape(snake)}\b'
        if re.search(pattern_ref, content):
            new_content = re.sub(pattern_ref, pascal, content)
            if new_content != content:
                content = new_content
                if f'class {snake}' not in str(changes):
                    changes.append(f'ref {snake} -> {pascal}')

    if content != original:
        if not dry_run:
            path.write_text(content, encoding='utf-8')
        return True, changes

    return False, []


def main():
    repo_root = Path('.')
    target_prefixes = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
    dry_run = '--dry-run' in sys.argv

    print(f"{'[DRY RUN] ' if dry_run else ''}Pascal Sovereignty Fixer")
    print("=" * 60)

    # Build mapping
    print("\n[1/3] Building snake_case -> PascalCase mapping...")
    mapping = find_snake_case_classes(repo_root, target_prefixes)
    print(f"  Found {len(mapping)} unique snake_case class names")

    # Fix all files
    print(f"\n[2/3] {'Auditing' if dry_run else 'Fixing'} files...")
    fixed_count = 0
    total_changes = 0

    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for path in get_python_files(repo_root):
        if not any(prefix in str(path) for prefix in target_prefixes):
            continue

        changed, changes = fix_file(path, mapping, dry_run)
        if changed:
            fixed_count += 1
            total_changes += len(changes)
            print(f"  {'Would fix' if dry_run else 'Fixed'}: {path.name} ({len(changes)} changes)")

    # Summary
    print(f"\n[3/3] Summary")
    print("=" * 60)
    print(f"  Files {'to fix' if dry_run else 'fixed'}: {fixed_count}")
    print(f"  Total changes: {total_changes}")
    print(f"  Unique class renames: {len(mapping)}")

    if dry_run:
        print("\n[!] Run without --dry-run to apply changes")
    else:
        print("\n[✓] Pascal Sovereignty achieved!")

    return 0 if fixed_count == 0 or not dry_run else 1


if __name__ == '__main__':
    sys.exit(main())
