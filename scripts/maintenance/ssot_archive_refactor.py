#!/usr/bin/env python3
"""
SSOT Archive Path Refactor

Replaces all hardcoded "archives" strings with imports from structure_blueprint.ARCHIVES_DIR
to ensure Single Source of Truth compliance.

USAGE:
    python scripts/maintenance/ssot_archive_refactor.py --dry-run
    python scripts/maintenance/ssot_archive_refactor.py --execute
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple


def find_hardcoded_archives(file_path: Path) -> List[Tuple[int, str]]:
    """Find lines with hardcoded 'archives' strings."""
    matches = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Skip comments and docstrings
            if line.strip().startswith('#'):
                continue
            if '"""' in line or "'''" in line:
                continue
            
            # Look for hardcoded "archives" or 'archives'
            if '"archives"' in line or "'archives'" in line:
                # Skip if it's already using ARCHIVES_DIR
                if 'ARCHIVES_DIR' in line:
                    continue
                # Skip if it's in a comment
                if '#' in line and line.index('#') < line.find('archives'):
                    continue
                matches.append((i, line))
    
    except Exception as e:
        print(f"  ⚠️  Error reading {file_path}: {e}")
    
    return matches


def needs_import(file_path: Path) -> bool:
    """Check if file needs ARCHIVES_DIR import."""
    try:
        content = file_path.read_text(encoding='utf-8')
        # Check if already imports ARCHIVES_DIR
        if 'from agentic_core.L5_safety.validators.structure_blueprint import ARCHIVES_DIR' in content:
            return False
        if 'ARCHIVES_DIR' in content and 'import' in content:
            return False
        return True
    except:
        return False


def add_import(file_path: Path, dry_run: bool = True) -> bool:
    """Add ARCHIVES_DIR import to file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Find the best place to insert import (after other imports)
        import_line = -1
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                import_line = i
        
        if import_line == -1:
            # No imports found, add after docstring
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    import_line = i + 1
                    break
        
        if import_line == -1:
            import_line = 0
        
        # Insert import
        new_import = 'from agentic_core.L5_safety.validators.structure_blueprint import ARCHIVES_DIR'
        lines.insert(import_line + 1, new_import)
        
        if not dry_run:
            file_path.write_text('\n'.join(lines), encoding='utf-8')
        
        return True
    except Exception as e:
        print(f"  ❌ Error adding import to {file_path}: {e}")
        return False


def replace_hardcoded_archives(file_path: Path, dry_run: bool = True) -> int:
    """Replace hardcoded 'archives' with ARCHIVES_DIR."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Replace "archives" with ARCHIVES_DIR (but not in comments)
        # Pattern: project_root / "archives" -> project_root / ARCHIVES_DIR
        content = re.sub(
            r'(["\'])archives\1',
            'ARCHIVES_DIR',
            content
        )
        
        replacements = content.count('ARCHIVES_DIR') - original_content.count('ARCHIVES_DIR')
        
        if content != original_content and not dry_run:
            file_path.write_text(content, encoding='utf-8')
        
        return replacements
    except Exception as e:
        print(f"  ❌ Error replacing in {file_path}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description='SSOT Archive Path Refactor')
    parser.add_argument('--execute', action='store_true', help='Execute changes (default is dry-run)')
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    print(f"\n{'='*70}")
    print("SSOT Archive Path Refactor")
    print(f"{'='*70}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"{'='*70}\n")
    
    # Scan agentic_core for hardcoded archives
    agentic_core = Path('agentic_core')
    files_to_fix = []
    
    for py_file in agentic_core.rglob('*.py'):
        # Skip archives directory itself
        if 'archives' in py_file.parts:
            continue
        if '__pycache__' in py_file.parts:
            continue
        
        matches = find_hardcoded_archives(py_file)
        if matches:
            files_to_fix.append((py_file, matches))
    
    print(f"Found {len(files_to_fix)} files with hardcoded 'archives' strings\n")
    
    if not files_to_fix:
        print("✅ No hardcoded 'archives' strings found!")
        return 0
    
    total_replacements = 0
    
    for file_path, matches in files_to_fix:
        print(f"\n📝 {file_path}")
        print(f"   Found {len(matches)} hardcoded references")
        
        if dry_run:
            print("   [DRY RUN] Would:")
            if needs_import(file_path):
                print("     1. Add ARCHIVES_DIR import")
            print(f"     2. Replace {len(matches)} hardcoded strings")
        else:
            # Add import if needed
            if needs_import(file_path):
                if add_import(file_path, dry_run=False):
                    print("   ✅ Added ARCHIVES_DIR import")
            
            # Replace hardcoded strings
            replacements = replace_hardcoded_archives(file_path, dry_run=False)
            if replacements > 0:
                print(f"   ✅ Replaced {replacements} occurrences")
                total_replacements += replacements
    
    print(f"\n{'='*70}")
    if dry_run:
        print("DRY RUN COMPLETE")
        print(f"Would modify {len(files_to_fix)} files")
    else:
        print("REFACTOR COMPLETE")
        print(f"Files modified: {len(files_to_fix)}")
        print(f"Total replacements: {total_replacements}")
        print("\nNext steps:")
        print("  1. Run: pytest tests/L5_safety/test_hygiene_consolidation.py")
        print("  2. Run: pytest tests/unit/test_archival_gatekeeper.py")
        print("  3. Verify: python scripts/maintenance/verify_ssot_compliance.py")
    print(f"{'='*70}\n")
    
    return 0


if __name__ == '__main__':
    exit(main())
