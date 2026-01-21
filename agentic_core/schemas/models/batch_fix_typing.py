#!/usr/bin/env python3
"""
Batch fix typing issues in agent files.
Adds missing type hints to function parameters and return types.
"""
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

PROJECT_ROOT = Path(__file__).parent.parent


def get_agents_needing_fixes() -> List[Dict]:
    """Get agents with low typed_pct."""
    data = json.load(open(PROJECT_ROOT / 'agent_discovery_full.json'))
    # Filter to agents with typed_pct < 100 and in agentic_core (not test files)
    low_typed = [
        a for a in data
        if a.get('typed_pct', 100) < 100
        and 'agentic_core' in a.get('path', '')
        and 'test' not in a.get('path', '').lower()
    ]
    return sorted(low_typed, key=lambda x: x.get('typed_pct', 0))


def fix_missing_return_types(source: str) -> Tuple[str, int]:
    """Add missing return types to functions."""
    fixes = 0
    lines = source.split('\n')

    for i, line in enumerate(lines):
        # Match function definitions without return type
        # Pattern: def func_name(...): or async def func_name(...):
        match = re.match(r'^(\s*)(async\s+)?def\s+(\w+)\s*\([^)]*\)\s*:\s*$', line)
        if match:
            indent = match.group(1)
            is_async = match.group(2) is not None
            func_name = match.group(3)

            # Skip if already has return type (->)
            if '->' in line:
                continue

            # Determine return type based on function name
            if func_name in ('__init__', '__post_init__', '__del__'):
                return_type = 'None'
            elif func_name.startswith('_') and not func_name.startswith('__'):
                return_type = 'Any'
            elif 'execute' in func_name.lower():
                return_type = 'Dict[str, Any]'
            elif 'heal' in func_name.lower():
                return_type = 'Dict[str, int]'
            elif 'validate' in func_name.lower() or 'check' in func_name.lower() or 'is_' in func_name.lower():
                return_type = 'bool'
            elif 'get_' in func_name.lower() or 'find_' in func_name.lower():
                return_type = 'Any'
            elif 'list_' in func_name.lower():
                return_type = 'List[Any]'
            else:
                return_type = 'Any'

            # Insert return type before the colon
            new_line = line.rstrip(':') + f' -> {return_type}:'
            lines[i] = new_line
            fixes += 1

    return '\n'.join(lines), fixes


def fix_missing_param_types(source: str) -> Tuple[str, int]:
    """Add missing parameter types to functions."""
    fixes = 0
    lines = source.split('\n')

    # Common parameter type mappings
    param_types = {
        'ctx': 'Any',
        'context': 'Any',
        'dry_run': 'bool',
        'execute': 'bool',
        'depth': 'int',
        'max_depth': 'int',
        'path': 'Path',
        'file_path': 'str',
        'name': 'str',
        'text': 'str',
        'data': 'Dict[str, Any]',
        'config': 'Dict[str, Any]',
        'options': 'Dict[str, Any]',
        'result': 'Dict[str, Any]',
        'results': 'List[Any]',
        'items': 'List[Any]',
        'callback': 'Any',
        'func': 'Any',
        'args': 'Any',
        'kwargs': 'Any',
        'timeout': 'int',
        'limit': 'int',
        'count': 'int',
        'index': 'int',
        'enabled': 'bool',
        'force': 'bool',
        'verbose': 'bool',
        'daemon': 'bool',
        'event': 'Any',
        'orchestrator': 'Any',
        'retriever': 'Any',
        'engine': 'Any',
        'client': 'Any',
        'genai_client': 'Any',
        'genai_available': 'bool',
    }

    for i, line in enumerate(lines):
        # Match function definition lines
        if re.match(r'^\s*(async\s+)?def\s+\w+\s*\(', line):
            # Find parameters without types
            for param, ptype in param_types.items():
                # Match parameter without type annotation
                # e.g., ", ctx)" or "(ctx," or "(ctx)"
                patterns = [
                    (rf'(\({param})\)', rf'({param}: {ptype})'),  # (param)
                    (rf'(\({param}),', rf'({param}: {ptype},'),   # (param,
                    (rf',\s*({param})\)', rf', {param}: {ptype})'),  # , param)
                    (rf',\s*({param}),', rf', {param}: {ptype},'),   # , param,
                ]
                for pattern, replacement in patterns:
                    if re.search(pattern, line) and f'{param}:' not in line:
                        line = re.sub(pattern, replacement, line)
                        fixes += 1

            lines[i] = line

    return '\n'.join(lines), fixes


def ensure_typing_imports(source: str) -> str:
    """Ensure typing imports are present."""
    needed_types = set()

    if 'Dict[' in source:
        needed_types.add('Dict')
    if 'List[' in source:
        needed_types.add('List')
    if 'Optional[' in source:
        needed_types.add('Optional')
    if 'Any' in source:
        needed_types.add('Any')
    if 'Tuple[' in source:
        needed_types.add('Tuple')
    if 'Set[' in source:
        needed_types.add('Set')

    if not needed_types:
        return source

    # Check if typing import exists
    typing_import_match = re.search(r'^from typing import (.+)$', source, re.MULTILINE)

    if typing_import_match:
        existing = set(t.strip() for t in typing_import_match.group(1).split(','))
        missing = needed_types - existing
        if missing:
            all_types = sorted(existing | needed_types)
            new_import = f"from typing import {', '.join(all_types)}"
            source = source.replace(typing_import_match.group(0), new_import)
    else:
        # Add typing import after __future__ import or at top
        if 'from __future__' in source:
            source = re.sub(
                r'(from __future__ import [^\n]+\n)',
                rf'\1from typing import {", ".join(sorted(needed_types))}\n',
                source
            )
        else:
            source = f'from typing import {", ".join(sorted(needed_types))}\n' + source

    return source


def fix_file(file_path: Path, dry_run: bool = True) -> Dict:
    """Fix typing issues in a single file."""
    try:
        source = file_path.read_text(encoding='utf-8')
        original = source
    except Exception as e:
        return {"error": str(e), "file": str(file_path)}

    # Apply fixes
    source, return_fixes = fix_missing_return_types(source)
    source, param_fixes = fix_missing_param_types(source)
    source = ensure_typing_imports(source)

    total_fixes = return_fixes + param_fixes

    if source != original:
        if not dry_run:
            file_path.write_text(source, encoding='utf-8')
        return {
            "file": str(file_path),
            "return_type_fixes": return_fixes,
            "param_type_fixes": param_fixes,
            "total_fixes": total_fixes,
            "applied": not dry_run
        }

    return {
        "file": str(file_path),
        "total_fixes": 0,
        "applied": False
    }


def main(dry_run: bool = True):
    """Main entry point."""
    agents = get_agents_needing_fixes()

    print("=" * 70)
    print(f"BATCH TYPING FIX {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print("=" * 70)
    print(f"Found {len(agents)} agents with typed_pct < 100%")

    total_fixes = 0
    files_fixed = 0

    for agent in agents:
        file_path = PROJECT_ROOT / agent['path']
        if not file_path.exists():
            continue

        result = fix_file(file_path, dry_run)

        if result.get('total_fixes', 0) > 0:
            files_fixed += 1
            total_fixes += result['total_fixes']
            print(f"\n{agent['class_name']} ({agent.get('typed_pct', 0):.0f}%)")
            print(f"  File: {agent['path']}")
            print(f"  Return type fixes: {result.get('return_type_fixes', 0)}")
            print(f"  Param type fixes: {result.get('param_type_fixes', 0)}")

    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  Files with fixes: {files_fixed}")
    print(f"  Total fixes: {total_fixes}")
    if dry_run:
        print("\nThis was a DRY RUN. Run with --live to apply changes.")
    else:
        print("\nChanges applied!")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    dry_run = "--live" not in sys.argv
    main(dry_run)
