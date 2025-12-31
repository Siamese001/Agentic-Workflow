"""
Namespace Medic - Standalone Utility for Fast Import Healing
Scans all Python files and injects missing standard library imports.
Run this BEFORE canon_validator to fix import starvation issues.
"""
import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import_patterns: Any = [('logging.', 'import logging', 'simple'), ('logger.', 'import logging', 'simple'), ('Any', 'from typing import Any, Optional, Protocol, Dict, List', 'typing'), ('Optional', 'from typing import Any, Optional, Protocol, Dict, List', 'typing'), ('Protocol', 'from typing import Any, Optional, Protocol, Dict, List', 'typing'), ('Dict[', 'from typing import Any, Optional, Protocol, Dict, List', 'typing'), ('List[', 'from typing import Any, Optional, Protocol, Dict, List', 'typing'), ('@dataclass', 'from dataclasses import dataclass, field', 'dataclass'), ('dataclass(', 'from dataclasses import dataclass, field', 'dataclass'), ('Enum', 'from enum import Enum, auto', 'enum'), ('Path(', 'from pathlib import Path', 'simple'), ('json.', 'import json', 'simple'), ('os.path', 'import os', 'simple'), ('sys.', 'import sys', 'simple'), ('re.', 'import re', 'simple'), ('datetime.', 'import datetime', 'simple'), ('time.', 'import time', 'simple'), ('asyncio.', 'import asyncio', 'simple')]

def find_missing_imports(content: str) -> List[str]:
    """Detect which standard library imports are missing from the file."""
    missing: Any = []
    seen_import_types: Any = set()
    for usage_pattern, import_stmt, import_type in IMPORT_PATTERNS:
        if usage_pattern not in content:
            continue
        if import_stmt in content:
            continue
        if import_type == 'typing' and 'typing' in seen_import_types:
            continue
        if import_stmt not in missing:
            missing.append(import_stmt)
            seen_import_types.add(import_type)
    return missing

def inject_imports(content: str, imports: List[str]) -> str:
    """Inject missing imports at the top of the file (after docstring)."""
    lines: Any = content.split('\n')
    insert_idx: Any = 0
    in_docstring: Any = False
    docstring_char: Any = None
    for i, line in enumerate(lines):
        stripped: Any = line.strip()
        if stripped.startswith('#'):
            insert_idx: Any = i + 1
            continue
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            docstring_char: Any = stripped[:3]
            in_docstring: Any = True
            if stripped.count(docstring_char) >= 2:
                in_docstring: Any = False
                insert_idx: Any = i + 1
            continue
        if in_docstring and docstring_char in stripped:
            in_docstring: Any = False
            insert_idx: Any = i + 1
            continue
        if not in_docstring and stripped and (not stripped.startswith('#')):
            break
    import_lines: Any = imports + ['']
    lines[insert_idx:insert_idx] = import_lines
    return '\n'.join(lines)

def heal_file(file_path: Path, dry_run: bool=False) -> Tuple[bool, int]:
    """
    Heal a single file by injecting missing imports.
    Returns (was_healed, num_imports_added)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content: Any = f.read()
        missing: Any = find_missing_imports(content)
        if not missing:
            return (False, 0)
        healed_content: Any = inject_imports(content, missing)
        try:
            ast.parse(healed_content)
        except SyntaxError as e:
            print(f'   [!] Syntax error after healing {file_path.name}: {e}')
            return (False, 0)
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(healed_content)
        return (True, len(missing))
    except Exception as e:
        print(f'   [!] Failed to heal {file_path.name}: {e}')
        return (False, 0)

def main() -> Any:
    """Main entry point for namespace healing."""
    import argparse
    parser: Any = argparse.ArgumentParser(description='Namespace Medic - Fix missing standard library imports')
    parser.add_argument('--target', default='agentic_core', help='Target directory to scan')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without modifying files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    args: Any = parser.parse_args()
    project_root: Any = Path(__file__).parent
    target_path: Any = (project_root / args.target).resolve()
    if not target_path.exists():
        print(f'[!] Target path does not exist: {target_path}')
        sys.exit(1)
    print(f"{'=' * 70}")
    print(f'NAMESPACE MEDIC - Standard Library Import Healer')
    print(f"{'=' * 70}")
    print(f'Target: {target_path}')
    print(f"Mode: {('DRY RUN' if args.dry_run else 'LIVE HEALING')}")
    print(f"{'=' * 70}\n")
    python_files: Any = [p for p in target_path.rglob('*.py') if p.is_file() and '__pycache__' not in str(p)]
    print(f'[SCAN] Found {len(python_files)} Python files\n')
    healed_count: Any = 0
    total_imports: Any = 0
    for file_path in python_files:
        was_healed, num_imports = heal_file(file_path, dry_run=args.dry_run)
        if was_healed:
            healed_count += 1
            total_imports += num_imports
            status: Any = '[DRY-RUN]' if args.dry_run else '[HEALED]'
            print(f'{status} {file_path.name} (+{num_imports} imports)')
            if args.verbose:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content: Any = f.read()
                missing: Any = find_missing_imports(content) if args.dry_run else []
                for imp in missing:
                    print(f'         + {imp}')
    print(f"\n{'=' * 70}")
    print(f'SUMMARY')
    print(f"{'=' * 70}")
    print(f'Files scanned: {len(python_files)}')
    print(f'Files healed: {healed_count}')
    print(f'Total imports added: {total_imports}')
    if args.dry_run:
        print(f'\n[INFO] This was a dry run. Run without --dry-run to apply changes.')
    else:
        print(f'\n[SUCCESS] Namespace healing complete!')
    print(f"{'=' * 70}\n")
if __name__ == '__main__':
    main()
