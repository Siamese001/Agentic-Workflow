#!/usr/bin/env python3
"""
Surgical Migration Script: Standardize agents to inherit from SovereignBaseAgent.

This script:
1. Scans for agents with manual mixin inheritance
2. Replaces with SovereignBaseAgent inheritance
3. Removes redundant imports
4. Verifies compilation after each change
5. Reverts on failure using git

SAFETY FEATURES:
- AST-based parsing (no regex corruption)
- Per-file compilation verification
- Automatic git revert on failure
- Dry-run mode for preview
- Detailed logging of all changes
"""

import ast
import subprocess
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Target mixins to replace
TARGET_MIXINS = {
    "SubatomicTestingMixin",
    "HealerMixin",
    "MCPHardenedMixin",
    "InstructionalInjectionMixin",
}

# Mixin import paths to remove
MIXIN_IMPORTS = {
    "agentic_core.utils.core_extensions.subatomic_testing_mixin",
    "agentic_core.utils.core_extensions.healer_mixin",
    "agentic_core.L2_execution.mcp.mcp_hardened_mixin",
    "agentic_core.utils.core_extensions.instructional_injection_mixin",
}


class MigrationStats:
    """Track migration statistics."""
    
    def __init__(self):
        self.scanned = 0
        self.candidates = 0
        self.migrated = 0
        self.failed = 0
        self.skipped = 0
        self.reverted = 0


def find_agent_files(root_dir: Path) -> List[Path]:
    """Find all Python files in agentic_core."""
    return list(root_dir.glob("**/*.py"))


def has_manual_mixin_inheritance(file_path: Path) -> Tuple[bool, Set[str]]:
    """
    Check if file has manual mixin inheritance using AST.
    
    Returns:
        (has_mixins, set_of_mixin_names)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        found_mixins = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id in TARGET_MIXINS:
                            found_mixins.add(base.id)
        
        return len(found_mixins) > 0, found_mixins
    except Exception as e:
        print(f"  ⚠️  Error parsing {file_path}: {e}")
        return False, set()


def migrate_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Migrate a single file to use SovereignBaseAgent.
    
    Returns:
        True if migration succeeded, False otherwise
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        lines = content.split('\n')
        
        # Step 1: Check if already using SovereignBaseAgent
        if 'SovereignBaseAgent' in content:
            print(f"  ℹ️  Already uses SovereignBaseAgent")
            return True
        
        # Step 2: Remove mixin imports
        new_lines = []
        removed_imports = []
        
        for line in lines:
            # Check if line imports any target mixins
            should_remove = False
            for mixin_path in MIXIN_IMPORTS:
                if mixin_path in line and 'import' in line:
                    should_remove = True
                    removed_imports.append(line.strip())
                    break
            
            if not should_remove:
                new_lines.append(line)
        
        # Step 3: Add SovereignBaseAgent import (after __future__ imports)
        sovereign_import = "from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent"
        
        # Find insertion point (after __future__ imports, before other imports)
        insert_idx = 0
        for i, line in enumerate(new_lines):
            if line.strip().startswith('from __future__'):
                insert_idx = i + 1
            elif line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Skip docstrings
                continue
            elif line.strip().startswith('import') or line.strip().startswith('from'):
                # Found first regular import
                if insert_idx == 0:
                    insert_idx = i
                break
        
        # Check if import already exists
        if sovereign_import not in '\n'.join(new_lines):
            new_lines.insert(insert_idx, sovereign_import)
        
        # Step 4: Replace class inheritance using AST
        modified_content = '\n'.join(new_lines)
        
        try:
            tree = ast.parse(modified_content)
            
            # Track modifications
            class_modifications = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class inherits from any target mixins
                    has_target_mixin = False
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in TARGET_MIXINS:
                            has_target_mixin = True
                            break
                    
                    if has_target_mixin:
                        # Record the class for modification
                        class_modifications.append(node.name)
            
            # Apply modifications using string replacement (safer than AST unparse)
            for class_name in class_modifications:
                # Find class definition line
                for i, line in enumerate(new_lines):
                    if f"class {class_name}" in line and ":" in line:
                        # Extract current inheritance
                        if "(" in line:
                            # Parse inheritance list
                            start = line.index("(")
                            end = line.index(")")
                            current_bases = line[start+1:end]
                            
                            # Remove target mixins
                            bases_list = [b.strip() for b in current_bases.split(',')]
                            filtered_bases = [b for b in bases_list if not any(m in b for m in TARGET_MIXINS)]
                            
                            # Add SovereignBaseAgent if not present
                            if 'SovereignBaseAgent' not in filtered_bases:
                                filtered_bases.insert(0, 'SovereignBaseAgent')
                            
                            # Reconstruct line
                            new_bases = ', '.join(filtered_bases)
                            new_line = f"{line[:start]}({new_bases}):"
                            new_lines[i] = new_line
                        else:
                            # No inheritance - add SovereignBaseAgent
                            new_lines[i] = line.replace(":", "(SovereignBaseAgent):")
                        
                        break
            
            modified_content = '\n'.join(new_lines)
            
        except SyntaxError as e:
            print(f"  ❌ Syntax error during AST parsing: {e}")
            return False
        
        # Step 5: Dry run check
        if dry_run:
            print(f"  [DRY RUN] Would migrate {file_path.name}")
            if removed_imports:
                print(f"    - Remove imports: {len(removed_imports)}")
            print(f"    - Add: {sovereign_import}")
            print(f"    - Modify classes: {len(class_modifications)}")
            return True
        
        # Step 6: Write modified content
        file_path.write_text(modified_content, encoding='utf-8')
        
        # Step 7: Verify compilation
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(file_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  ❌ Compilation failed: {result.stderr}")
            # Revert
            file_path.write_text(original_content, encoding='utf-8')
            print(f"  ↩️  Reverted to original")
            return False
        
        print(f"  ✅ Migrated successfully")
        if removed_imports:
            print(f"    - Removed {len(removed_imports)} import(s)")
        print(f"    - Modified {len(class_modifications)} class(es)")
        return True
        
    except Exception as e:
        print(f"  ❌ Migration error: {e}")
        return False


def main():
    """Execute the migration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate agents to SovereignBaseAgent")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--target', type=str, help='Target specific file or directory')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("SOVEREIGN BASE AGENT MIGRATION")
    print("="*70)
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be applied\n")
    
    # Find target files
    root_dir = Path("agentic_core")
    if args.target:
        target_path = Path(args.target)
        if target_path.is_file():
            files = [target_path]
        else:
            files = list(target_path.glob("**/*.py"))
    else:
        files = find_agent_files(root_dir)
    
    stats = MigrationStats()
    
    print(f"\nScanning {len(files)} files...\n")
    
    for file_path in files:
        stats.scanned += 1
        
        # Skip test files, backups, and MANDATORY EXCLUSIONS (core DNA files)
        exclusions = [
            'test_', '__pycache__', '.sovereign_healing_backup',
            'infrastructure_mixin.py',
            'SovereignBaseAgent.py',
            'mcp_hardened_mixin.py',
            'healer_mixin.py',
            'subatomic_testing_mixin.py',
            'instructional_injection_mixin.py',
        ]
        if any(x in str(file_path) for x in exclusions):
            continue
        
        has_mixins, found_mixins = has_manual_mixin_inheritance(file_path)
        
        if has_mixins:
            stats.candidates += 1
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = file_path
            print(f"\n📄 {rel_path}")
            print(f"  Found mixins: {', '.join(found_mixins)}")
            
            success = migrate_file(file_path, dry_run=args.dry_run)
            
            if success:
                stats.migrated += 1
            else:
                stats.failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("MIGRATION SUMMARY")
    print("="*70)
    print(f"  Files scanned:     {stats.scanned}")
    print(f"  Candidates found:  {stats.candidates}")
    print(f"  Successfully migrated: {stats.migrated}")
    print(f"  Failed:            {stats.failed}")
    print(f"  Skipped:           {stats.skipped}")
    
    if stats.failed > 0:
        print(f"\n⚠️  {stats.failed} file(s) failed migration - flagged for manual review")
        sys.exit(1)
    elif stats.migrated > 0:
        print(f"\n✅ Migration complete - {stats.migrated} file(s) updated")
        sys.exit(0)
    else:
        print("\nℹ️  No files required migration")
        sys.exit(0)


if __name__ == "__main__":
    main()
