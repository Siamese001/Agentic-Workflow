#!/usr/bin/env python3
"""
Strip dead re-exports from __init__.py files.

Usage:
    python tools/fix/strip_dead_reexports.py --reports <json_reports> [--dry-run]
"""

import argparse
import ast
import json
import pathlib
import sys


def get_dead_imports(report_path: str, file_path: str) -> set[str]:
    """Get dead imports for a specific file from the ADG report."""
    p = pathlib.Path(report_path)
    data = json.loads(p.read_text(encoding="utf-8"))
    
    for fdata in data["files"]:
        if fdata["path"].replace("\\", "/") == file_path.replace("\\", "/"):
            dead = set()
            for item in fdata.get("adg_dead_imports", []):
                # Extract the imported name (last part of dotted path)
                sym = item["symbol"].split(".")[-1]
                dead.add(sym)
            return dead
    return set()


def strip_dead_reexports_from_init(init_path: str, dead_imports: set[str], dry_run: bool) -> bool:
    """Remove dead re-exports from an __init__.py file."""
    if not dead_imports:
        return False
    
    src = pathlib.Path(init_path).read_text(encoding="utf-8")
    lines = src.splitlines(keepends=True)
    
    # Find and remove import lines containing dead symbols
    new_lines = []
    removed_any = False
    in_import_block = False
    
    for line in lines:
        # Check if this is an import line
        if "from " in line and "import " in line:
            # Check if any dead symbol is in this line
            has_dead = any(dead in line for dead in dead_imports)
            if has_dead:
                # For single-line imports, remove the line
                if "(" not in line:
                    removed_any = True
                    continue
                # For multi-line imports, mark for processing
                in_import_block = True
                new_lines.append(line)
                continue
        
        # Handle continuation of multi-line imports
        if in_import_block:
            if ")" in line:
                in_import_block = False
                # Filter out dead symbols from this block
                # Simplified: just remove the entire block for now
                removed_any = True
                continue
            # Check if this line contains a dead symbol
            has_dead = any(dead in line for dead in dead_imports)
            if has_dead:
                removed_any = True
                continue
            new_lines.append(line)
            continue
        
        # Remove __all__ lines if we removed imports
        if removed_any and "__all__" in line:
            continue
        
        new_lines.append(line)
    
    if not removed_any:
        return False
    
    # Validate syntax
    new_src = "".join(new_lines)
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        print(f"  SYNTAX ERROR in {init_path}: {e} — SKIPPING", file=sys.stderr)
        return False
    
    if not dry_run:
        pathlib.Path(init_path).write_text(new_src, encoding="utf-8")
    
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Strip dead re-exports from __init__.py files")
    parser.add_argument("--reports", nargs="+", required=True, help="ADG analysis JSON reports")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without modifying files")
    args = parser.parse_args()
    
    # Collect all __init__.py files with dead imports
    targets = []
    for rp in args.reports:
        p = pathlib.Path(rp)
        data = json.loads(p.read_text(encoding="utf-8"))
        for fdata in data["files"]:
            if "__init__.py" in fdata["path"] and fdata.get("adg_dead_imports"):
                targets.append((fdata["path"], rp))
    
    print(f"Found {len(targets)} __init__.py files with dead re-exports")
    
    changed = 0
    for filepath, report_path in sorted(targets):
        dead_imports = get_dead_imports(report_path, filepath)
        if strip_dead_reexports_from_init(filepath, dead_imports, args.dry_run):
            action = "DRY-RUN" if args.dry_run else "CHANGED"
            print(f"[{action}] {filepath}")
            changed += 1
    
    print(f"\nSummary: {changed} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
