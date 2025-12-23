#!/usr/bin/env python3
"""
Namespace Medic - Standalone Utility for Fast Import Healing
Scans all Python files and injects missing standard library imports.
Run this BEFORE canon_validator to fix import starvation issues.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

# Import patterns: (usage_pattern, import_statement, import_type)
IMPORT_PATTERNS = [
    ("logging.", "import logging", "simple"),
    ("logger.", "import logging", "simple"),
    ("Any", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("Optional", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("Protocol", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("Dict[", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("List[", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("@dataclass", "from dataclasses import dataclass, field", "dataclass"),
    ("dataclass(", "from dataclasses import dataclass, field", "dataclass"),
    ("Enum", "from enum import Enum, auto", "enum"),
    ("Path(", "from pathlib import Path", "simple"),
    ("json.", "import json", "simple"),
    ("os.path", "import os", "simple"),
    ("sys.", "import sys", "simple"),
    ("re.", "import re", "simple"),
    ("datetime.", "import datetime", "simple"),
    ("time.", "import time", "simple"),
    ("asyncio.", "import asyncio", "simple"),
]


def find_missing_imports(content: str) -> List[str]:
    """Detect which standard library imports are missing from the file."""
    missing = []
    seen_import_types = set()
    
    for usage_pattern, import_stmt, import_type in IMPORT_PATTERNS:
        # Skip if usage pattern not found
        if usage_pattern not in content:
            continue
        
        # Check if import already exists
        if import_stmt in content:
            continue
        
        # For typing imports, only add once
        if import_type == "typing" and "typing" in seen_import_types:
            continue
        
        # Avoid duplicates
        if import_stmt not in missing:
            missing.append(import_stmt)
            seen_import_types.add(import_type)
    
    return missing


def inject_imports(content: str, imports: List[str]) -> str:
    """Inject missing imports at the top of the file (after docstring)."""
    lines = content.split('\n')
    
    # Find insertion point (after module docstring if present)
    insert_idx = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip shebang and encoding declarations
        if stripped.startswith('#'):
            insert_idx = i + 1
            continue
        
        # Detect docstring start
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            docstring_char = stripped[:3]
            in_docstring = True
            # Check if docstring ends on same line
            if stripped.count(docstring_char) >= 2:
                in_docstring = False
                insert_idx = i + 1
            continue
        
        # Detect docstring end
        if in_docstring and docstring_char in stripped:
            in_docstring = False
            insert_idx = i + 1
            continue
        
        # If we hit a non-comment, non-docstring line, stop
        if not in_docstring and stripped and not stripped.startswith('#'):
            break
    
    # Insert imports at the determined position
    import_lines = imports + ['']  # Add blank line after imports
    lines[insert_idx:insert_idx] = import_lines
    
    return '\n'.join(lines)


def heal_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Heal a single file by injecting missing imports.
    Returns (was_healed, num_imports_added)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Find missing imports
        missing = find_missing_imports(content)
        
        if not missing:
            return False, 0
        
        # Inject imports
        healed_content = inject_imports(content, missing)
        
        # Validate syntax
        try:
            ast.parse(healed_content)
        except SyntaxError as e:
            print(f"   [!] Syntax error after healing {file_path.name}: {e}")
            return False, 0
        
        # Write back if not dry run
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(healed_content)
        
        return True, len(missing)
    
    except Exception as e:
        print(f"   [!] Failed to heal {file_path.name}: {e}")
        return False, 0


def main():
    """Main entry point for namespace healing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Namespace Medic - Fix missing standard library imports')
    parser.add_argument('--target', default='agentic_core', help='Target directory to scan')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without modifying files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    # Resolve target path
    project_root = Path(__file__).parent
    target_path = (project_root / args.target).resolve()
    
    if not target_path.exists():
        print(f"[!] Target path does not exist: {target_path}")
        sys.exit(1)
    
    print(f"{'='*70}")
    print(f"NAMESPACE MEDIC - Standard Library Import Healer")
    print(f"{'='*70}")
    print(f"Target: {target_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE HEALING'}")
    print(f"{'='*70}\n")
    
    # Discover Python files
    python_files = [p for p in target_path.rglob("*.py") if p.is_file() and '__pycache__' not in str(p)]
    print(f"[SCAN] Found {len(python_files)} Python files\n")
    
    # Heal files
    healed_count = 0
    total_imports = 0
    
    for file_path in python_files:
        was_healed, num_imports = heal_file(file_path, dry_run=args.dry_run)
        
        if was_healed:
            healed_count += 1
            total_imports += num_imports
            status = "[DRY-RUN]" if args.dry_run else "[HEALED]"
            print(f"{status} {file_path.name} (+{num_imports} imports)")
            
            if args.verbose:
                # Show which imports were added
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                missing = find_missing_imports(content) if args.dry_run else []
                for imp in missing:
                    print(f"         + {imp}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Files scanned: {len(python_files)}")
    print(f"Files healed: {healed_count}")
    print(f"Total imports added: {total_imports}")
    
    if args.dry_run:
        print(f"\n[INFO] This was a dry run. Run without --dry-run to apply changes.")
    else:
        print(f"\n[SUCCESS] Namespace healing complete!")
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()