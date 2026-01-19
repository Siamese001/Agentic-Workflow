#!/usr/bin/env python3
"""
Phase 4 Batch 2: Discovery Optimization (The Index Switch)

Replace expensive rglob("*.py") calls with SovereignIndex.get_python_files().

CONSTRAINTS:
- Do NOT modify sovereign_index.py itself
- Do NOT modify full_agent_discovery.py (source of truth)
- Only replace simple patterns: .rglob("*.py") or .rglob('*.py')

Usage:
    python scripts/phase4_batch2_index_switch.py --dry-run
    python scripts/phase4_batch2_index_switch.py --execute
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple

# Files to EXCLUDE from refactoring (sources of truth)
EXCLUDED_FILES = {
    "sovereign_index.py",
    "full_agent_discovery.py",
    "conftest.py",
    "phase4_batch1_decorator_sweep.py",
    "phase4_batch2_index_switch.py",
}

# Directories to exclude
EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    "archives",
    "void_violations",
    "node_modules",
    ".venv",
    "venv",
}

# Pattern to match rglob("*.py") or rglob('*.py')
RGLOB_PATTERN = re.compile(
    r'(\w+)\.rglob\(["\'](\*\.py)["\']\)',
    re.MULTILINE
)

SOVEREIGN_INDEX_IMPORT = "from agentic_core.utils.sovereign_index import SovereignIndex"


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files in agentic_core, excluding specified directories."""
    files = []
    for path in root.rglob("*.py"):
        if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
            continue
        if path.name in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


def has_rglob_py_pattern(content: str) -> bool:
    """Check if file contains rglob("*.py") pattern."""
    return bool(RGLOB_PATTERN.search(content))


def already_has_sovereign_import(content: str) -> bool:
    """Check if file already imports SovereignIndex."""
    return "from agentic_core.utils.sovereign_index import SovereignIndex" in content


def find_import_insertion_point(content: str) -> int:
    """Find the best line to insert the import statement."""
    lines = content.split('\n')
    last_import_line = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2:
                    continue
                in_docstring = True
                continue
        else:
            if docstring_char in stripped:
                in_docstring = False
            continue
        
        # Track imports
        if stripped.startswith('import ') or stripped.startswith('from '):
            last_import_line = i
    
    return last_import_line


def replace_rglob_patterns(content: str) -> Tuple[str, int]:
    """Replace rglob("*.py") with SovereignIndex.get_instance().get_python_files().
    
    Returns:
        Tuple of (modified_content, number_of_replacements)
    """
    replacements = 0
    
    def replacer(match):
        nonlocal replacements
        var_name = match.group(1)
        replacements += 1
        # Replace with SovereignIndex call
        return f"SovereignIndex.get_instance({var_name}).get_python_files()"
    
    modified = RGLOB_PATTERN.sub(replacer, content)
    return modified, replacements


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file.
    
    Returns:
        dict with processing results
    """
    result = {
        "file": str(file_path),
        "import_added": False,
        "replacements": 0,
        "skipped": False,
        "reason": None,
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result["skipped"] = True
        result["reason"] = f"Read error: {e}"
        return result
    
    # Skip if no rglob pattern
    if not has_rglob_py_pattern(content):
        result["skipped"] = True
        result["reason"] = "No rglob('*.py') pattern"
        return result
    
    modified_content = content
    
    # Add import if missing
    if not already_has_sovereign_import(content):
        insert_line = find_import_insertion_point(content)
        lines = modified_content.split('\n')
        lines.insert(insert_line + 1, SOVEREIGN_INDEX_IMPORT)
        modified_content = '\n'.join(lines)
        result["import_added"] = True
    
    # Replace rglob patterns
    modified_content, replacements = replace_rglob_patterns(modified_content)
    result["replacements"] = replacements
    
    # Write if not dry run and changes were made
    if not dry_run and (result["import_added"] or replacements > 0):
        try:
            file_path.write_text(modified_content, encoding='utf-8')
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 2: Replace rglob with SovereignIndex")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--execute", action="store_true", help="Actually modify files")
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Please specify --dry-run or --execute")
        return
    
    dry_run = args.dry_run
    
    root = Path(__file__).parent.parent / "agentic_core"
    if not root.exists():
        print(f"Error: agentic_core directory not found at {root}")
        return
    
    print(f"{'[DRY RUN]' if dry_run else '[EXECUTE]'} Phase 4 Batch 2: Index Switch")
    print(f"Scanning: {root}")
    print("-" * 60)
    
    files = find_python_files(root)
    print(f"Found {len(files)} Python files to analyze")
    
    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "imports_added": 0,
        "replacements": 0,
        "files_skipped": 0,
    }
    
    for file_path in files:
        result = process_file(file_path, dry_run=dry_run)
        stats["files_processed"] += 1
        
        if result["skipped"]:
            stats["files_skipped"] += 1
            continue
        
        if result["import_added"] or result["replacements"] > 0:
            stats["files_modified"] += 1
            stats["imports_added"] += 1 if result["import_added"] else 0
            stats["replacements"] += result["replacements"]
            
            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if dry_run else '[MODIFIED]'} {rel_path}")
            if result["import_added"]:
                print(f"    + Added SovereignIndex import")
            if result["replacements"]:
                print(f"    + Replaced {result['replacements']} rglob call(s)")
    
    print("-" * 60)
    print("Summary:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Files modified:  {stats['files_modified']}")
    print(f"  Imports added:   {stats['imports_added']}")
    print(f"  Replacements:    {stats['replacements']}")
    print(f"  Files skipped:   {stats['files_skipped']}")
    
    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --execute to apply changes.")


if __name__ == "__main__":
    main()
