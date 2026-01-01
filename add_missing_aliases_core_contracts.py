#!/usr/bin/env python3
"""
Comprehensive Alias Addition Script for core_contracts.py
Phase 12 Completion - Dec 31, 2025

Systematically adds missing PascalCase backward-compatibility aliases
for all snake_case class/enum/dataclass definitions.

Safety:
- Creates .bak backup file
- Dry-run mode for preview
- No modifications to definitions — only adds aliases
- Handles dataclasses, Pydantic BaseModel, Enum
"""

import os
import re
import shutil
from typing import Set, List, Tuple, Dict


def snake_to_pascal(snake: str) -> str:
    """Convert snake_case to PascalCase (e.g., sovereign_severity → SovereignSeverity)"""
    parts = snake.split('_')
    return ''.join(part.capitalize() for part in parts if part)


def extract_definitions_and_aliases(lines: List[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Extract snake_case definitions and existing PascalCase aliases.
    
    Returns:
        - snake_classes: Set of snake_case class/enum names
        - existing_aliases: Set of snake_case names that already have aliases
        - pascal_definitions: Set of PascalCase names defined directly (not aliases)
    """
    # Pattern for class definitions (including @dataclass decorated)
    # Matches: class name(...): or class name:
    class_pattern = re.compile(r'^(?:@dataclass(?:\(.*?\))?\s*\n)?class\s+([a-z_][a-z0-9_]*)\s*[\(:]', re.MULTILINE)
    
    # Simpler line-by-line pattern for snake_case class
    line_class_pattern = re.compile(r'^\s*class\s+([a-z_][a-z0-9_]*)\s*[\(:]')
    
    # Pattern for existing aliases: PascalCase = snake_case
    alias_pattern = re.compile(r'^([A-Z][A-Za-z0-9_]*)\s*=\s*([a-z_][a-z0-9_]*)\s*$')
    
    # Pattern for direct PascalCase class definitions
    pascal_class_pattern = re.compile(r'^\s*class\s+([A-Z][A-Za-z0-9_]*)\s*[\(:]')
    
    snake_classes: Set[str] = set()
    existing_aliases: Set[str] = set()
    pascal_definitions: Set[str] = set()
    
    full_content = ''.join(lines)
    
    for line in lines:
        # Check for snake_case class definition
        match = line_class_pattern.match(line)
        if match:
            name = match.group(1)
            # Ensure it's actually snake_case (has underscore or starts lowercase)
            if '_' in name or name[0].islower():
                snake_classes.add(name)
        
        # Check for PascalCase class definition
        pascal_match = pascal_class_pattern.match(line)
        if pascal_match:
            pascal_definitions.add(pascal_match.group(1))
        
        # Check for existing alias: PascalCase = snake_case
        alias_match = alias_pattern.match(line.strip())
        if alias_match:
            pascal_name = alias_match.group(1)
            snake_name = alias_match.group(2)
            existing_aliases.add(snake_name)
    
    return snake_classes, existing_aliases, pascal_definitions


def find_insertion_point(lines: List[str], missing_aliases: List[Tuple[str, str]]) -> int:
    """
    Find the safe insertion point for aliases:
    - Before the first usage of any PascalCase name that needs an alias in actual code
    - This ensures aliases are defined before they're referenced
    """
    # Build set of PascalCase names we need to define
    pascal_names_needed = {pascal for pascal, _ in missing_aliases}
    
    # Standard library / pydantic names to ignore
    ignore_names = {'BaseModel', 'Field', 'Enum', 'Optional', 'List', 'Dict', 'Any', 
                    'Literal', 'Set', 'Path', 'ConfigDict', 'True', 'False', 'None'}
    
    # Pattern to find PascalCase usage in type annotations
    # e.g., "primary_tone: ToneType" or "List[Hypothesis]"
    type_annotation_pattern = re.compile(r':\s*([A-Z][A-Za-z0-9_]*)\s*[=\[\)]')
    list_pattern = re.compile(r'List\[([A-Z][A-Za-z0-9_]*)\]')
    optional_pattern = re.compile(r'Optional\[([A-Z][A-Za-z0-9_]*)\]')
    
    # Direct reference like ThermalProfile.BALANCED
    direct_usage = re.compile(r'\b([A-Z][A-Za-z0-9_]*)\.(?!py)')  # Exclude .py file refs
    
    # Track if we're inside a class definition
    in_class = False
    class_start_line = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip comments and docstrings
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        # Track class definitions
        if stripped.startswith('class ') or stripped.startswith('@dataclass'):
            in_class = True
            class_start_line = i
            continue
        
        # Skip import lines
        if stripped.startswith('from ') or stripped.startswith('import '):
            continue
        
        # Only check inside class bodies for field definitions
        if not in_class:
            continue
        
        # Check for type annotation usage in field definitions
        for pattern in [type_annotation_pattern, list_pattern, optional_pattern]:
            matches = pattern.findall(line)
            for name in matches:
                if name and name in pascal_names_needed and name not in ignore_names:
                    # Found first usage - need to insert aliases before this class
                    # Go back to find class start or @dataclass decorator
                    for j in range(class_start_line, -1, -1):
                        if lines[j].strip().startswith('@dataclass') or lines[j].strip().startswith('# NAMING'):
                            return j
                        if lines[j].strip().startswith('class '):
                            return j
                    return class_start_line
        
        # Check for direct usage like ThermalProfile.BALANCED (enum access)
        direct_matches = direct_usage.findall(line)
        for name in direct_matches:
            if name in pascal_names_needed and name not in ignore_names:
                for j in range(class_start_line, -1, -1):
                    if lines[j].strip().startswith('@dataclass') or lines[j].strip().startswith('# NAMING'):
                        return j
                    if lines[j].strip().startswith('class '):
                        return j
                return class_start_line
    
    # Fallback: insert before first registry update
    for i, line in enumerate(lines):
        if 'CORE_CONTRACTS_REGISTRY.update(' in line:
            return i
    
    raise ValueError("Could not find safe insertion point")


def find_class_definition_lines(lines: List[str]) -> Dict[str, int]:
    """
    Find the line number where each snake_case class is DEFINED.
    Returns dict mapping class name to its definition line number.
    """
    class_pattern = re.compile(r'^class\s+([a-z_][a-z0-9_]*)\s*[\(:]')
    
    class_lines: Dict[str, int] = {}
    
    for i, line in enumerate(lines):
        match = class_pattern.match(line)
        if match:
            class_lines[match.group(1)] = i
    
    return class_lines


def find_safe_insertion_point(lines: List[str], class_lines: Dict[str, int], 
                               aliases_needed: List[Tuple[str, str]]) -> int:
    """
    Find the safest single insertion point for all aliases.
    Strategy: Insert right after the LAST class that is referenced by ANY subsequent class.
    """
    # Build mapping of pascal -> snake
    alias_map = {pascal: snake for pascal, snake in aliases_needed}
    pascal_names = set(alias_map.keys())
    
    # Find where each PascalCase name is first USED (not defined)
    first_usage: Dict[str, int] = {}
    
    # Patterns to detect PascalCase usage
    type_patterns = [
        re.compile(r':\s*([A-Z][A-Za-z0-9_]*)\s*[=\[\)]'),  # Type annotation
        re.compile(r'List\[([A-Z][A-Za-z0-9_]*)\]'),
        re.compile(r'Optional\[([A-Z][A-Za-z0-9_]*)\]'),
        re.compile(r'\b([A-Z][A-Za-z0-9_]*)\.'),  # Enum access like ThermalProfile.BALANCED
    ]
    
    ignore_names = {'BaseModel', 'Field', 'Enum', 'Optional', 'List', 'Dict', 'Any', 
                    'Literal', 'Set', 'Path', 'ConfigDict', 'True', 'False', 'None',
                    'Config', 'Builder'}
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip comments, imports, class definitions
        if stripped.startswith('#') or stripped.startswith('from ') or stripped.startswith('import '):
            continue
        if stripped.startswith('class ') or stripped.startswith('@'):
            continue
            
        for pattern in type_patterns:
            for match in pattern.finditer(line):
                name = match.group(1)
                if name in pascal_names and name not in ignore_names:
                    if name not in first_usage:
                        first_usage[name] = i
    
    if not first_usage:
        # No usage found, insert before first registry update
        for i, line in enumerate(lines):
            if 'core_contracts_registry' in line and '=' in line and 'update' not in line.lower():
                return i
        return len(lines) - 1
    
    # Find the earliest usage
    earliest_usage_line = min(first_usage.values())
    earliest_usage_name = [k for k, v in first_usage.items() if v == earliest_usage_line][0]
    
    # The snake_case class for this PascalCase name
    snake_name = alias_map.get(earliest_usage_name)
    if snake_name and snake_name in class_lines:
        # Insert right after this class's definition line
        # Find the next class or comment marker after this class
        class_def_line = class_lines[snake_name]
        
        # Scan forward to find end of this class (next class def or # NAMING marker)
        for i in range(class_def_line + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith('# NAMING') or stripped.startswith('class ') or stripped.startswith('@dataclass'):
                return i
            if stripped.startswith('# ===') and i > class_def_line + 3:  # Section marker
                return i
    
    return earliest_usage_line


def add_missing_aliases(file_path: str, dry_run: bool = True) -> None:
    """
    Systematically add missing PascalCase backward-compatibility aliases.
    Uses consolidated insertion - all aliases in one block at a safe location.
    
    Args:
        file_path: Path to core_contracts.py
        dry_run: If True, only preview changes without applying
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Create backup
    backup_path = file_path + '.bak'
    shutil.copy(file_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract definitions and existing aliases
    snake_classes, existing_aliases, pascal_definitions = extract_definitions_and_aliases(lines)
    
    print(f"\n📊 Analysis Results:")
    print(f"   - Snake_case classes found: {len(snake_classes)}")
    print(f"   - Already have aliases: {len(existing_aliases)}")
    print(f"   - Direct PascalCase definitions: {len(pascal_definitions)}")
    
    # Generate missing aliases
    missing_aliases: List[Tuple[str, str]] = []
    for snake in sorted(snake_classes):
        if snake not in existing_aliases:
            pascal = snake_to_pascal(snake)
            # Skip if PascalCase is already defined directly as a class
            if pascal not in pascal_definitions:
                missing_aliases.append((pascal, snake))
    
    if not missing_aliases:
        print("\n✓ No missing aliases found — backward compatibility already complete!")
        return
    
    print(f"\n🔧 Found {len(missing_aliases)} missing aliases to add:")
    for pascal, snake in missing_aliases[:10]:
        print(f"   {pascal} = {snake}")
    if len(missing_aliases) > 10:
        print(f"   ... and {len(missing_aliases) - 10} more")
    
    # Find class definition lines
    class_lines = find_class_definition_lines(lines)
    
    # Group aliases by their snake_case class definition order
    # We need to insert aliases in multiple strategic locations
    
    # Strategy: For each class that uses a PascalCase reference,
    # ensure all referenced aliases are defined before that class
    
    # Find all usage points and group aliases accordingly
    alias_map = {pascal: snake for pascal, snake in missing_aliases}
    
    # Build insertion groups: determine which aliases need to exist before which lines
    insertion_groups: Dict[int, List[str]] = {}
    
    # Strategy: Add "from __future__ import annotations" at top (if not present)
    # This defers annotation evaluation so PascalCase names don't need to exist at parse time
    # Then add all aliases before the first registry definition
    
    # Check if future annotations import exists
    has_future_annotations = any('from __future__ import annotations' in line for line in lines)
    
    # Find insertion points
    registry_line = None
    first_import_line = None
    
    last_registry_update = None
    final_assertion_line = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Find first regular import (not from __future__)
        if first_import_line is None and (stripped.startswith('import ') or 
            (stripped.startswith('from ') and '__future__' not in stripped)):
            first_import_line = i
        # Track the LAST registry update call
        if 'CORE_CONTRACTS_REGISTRY.update(' in line:
            last_registry_update = i
        # Find the final assertion block
        if 'Final Registry Integrity Assertion' in line:
            final_assertion_line = i
            break
    
    # Insert point for aliases: AFTER all registry updates, before final assertions
    # This ensures all classes are defined before aliases reference them
    if final_assertion_line:
        alias_insertion_line = final_assertion_line
    elif last_registry_update:
        # Find end of last registry update block (closing brace + blank line)
        alias_insertion_line = last_registry_update + 5
    else:
        alias_insertion_line = len(lines) - 10
    
    # Build alias block
    alias_block = [
        "\n",
        "# === BACKWARD COMPATIBILITY ALIASES (Phase 12 Completion - Dec 31, 2025) ===\n",
        "# Consolidated missing PascalCase aliases for legacy references\n", 
        "# These enable full module import without NameError\n",
        "# Future: Deprecate and remove after migration to snake_case SSOT\n",
    ]
    
    for pascal, snake in missing_aliases:
        alias_block.append(f"{pascal} = {snake}\n")
    
    alias_block.append("\n")
    
    # Build future import line if needed
    future_import = "from __future__ import annotations\n" if not has_future_annotations else None
    
    print(f"\n📍 Strategy:")
    if future_import:
        print(f"   1. Add 'from __future__ import annotations' before first import (line {first_import_line + 1})")
    print(f"   2. Add alias block before registry (line {alias_insertion_line + 1})")
    
    if dry_run:
        print("\n" + "="*60)
        print("=== PROPOSED CHANGES (DRY RUN) ===")
        print("="*60)
        if future_import:
            print(f"+ {future_import.strip()}")
        print("\nAlias block preview:")
        print(''.join(alias_block[:10]))
        if len(alias_block) > 15:
            print(f"... ({len(alias_block) - 10} more lines)")
        print("="*60)
        print(f"\nTotal aliases to add: {len(missing_aliases)}")
        print("\n⚠️  DRY RUN MODE - No changes applied")
        print("    To apply changes, use --apply flag")
        return
    
    # Apply changes
    new_lines = lines.copy()
    
    # First: Insert future import if needed (before first regular import)
    if future_import and first_import_line is not None:
        new_lines.insert(first_import_line, future_import)
        # Adjust alias insertion line since we added a line
        alias_insertion_line += 1
    
    # Second: Insert alias block before registry
    new_lines = new_lines[:alias_insertion_line] + alias_block + new_lines[alias_insertion_line:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✓ Changes applied:")
    if future_import:
        print(f"   - Added 'from __future__ import annotations'")
    print(f"   - Added {len(missing_aliases)} aliases")
    print(f"✓ Backup available at: {backup_path}")


def validate_import(file_path: str) -> bool:
    """Validate that the module can be imported without errors."""
    import subprocess
    import sys
    
    # Get the module path relative to the project
    result = subprocess.run(
        [sys.executable, "-c", 
         f"import sys; sys.path.insert(0, r'{os.path.dirname(os.path.dirname(file_path))}'); "
         f"from agentic_core.schemas.models.core_contracts import *; "
         f"print('Full SSOT import OK:', len(CORE_CONTRACTS_REGISTRY))"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
    )
    
    if result.returncode == 0:
        print(f"\n✓ Validation passed: {result.stdout.strip()}")
        return True
    else:
        print(f"\n✗ Validation failed:")
        print(f"   {result.stderr}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Add missing PascalCase aliases to core_contracts.py"
    )
    parser.add_argument(
        "--apply", 
        action="store_true",
        help="Apply changes (default is dry-run mode)"
    )
    parser.add_argument(
        "--validate",
        action="store_true", 
        help="Run import validation after applying changes"
    )
    parser.add_argument(
        "--file",
        default="agentic_core/schemas/models/core_contracts.py",
        help="Path to core_contracts.py (default: agentic_core/schemas/models/core_contracts.py)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("  Backward Compatibility Alias Generator")
    print("  Phase 12 Completion - Dec 31, 2025")
    print("="*60)
    
    dry_run = not args.apply
    
    if dry_run:
        print("\n🔍 Running in DRY-RUN mode (use --apply to make changes)")
    else:
        print("\n⚡ Running in APPLY mode - changes will be written!")
    
    add_missing_aliases(args.file, dry_run=dry_run)
    
    if args.validate and not dry_run:
        print("\n" + "-"*60)
        print("Running post-modification validation...")
        validate_import(args.file)
