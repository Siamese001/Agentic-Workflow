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
from typing import Optional, TypedDict


class ImportNode(TypedDict):
    lineno: int
    module: Optional[str]
    all_symbols: list[str]
    dead_symbols: list[str]
    end_lineno: int


def get_dead_imports(report_path: str, file_path: str) -> set[str]:
    """Get dead imports for a specific file from the ADG report."""
    p = pathlib.Path(report_path)
    if not p.exists():
        print(f"  WARNING: Report file not found: {report_path} — SKIPPING", file=sys.stderr)
        return set()
    
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  ERROR: Failed to parse JSON in {report_path}: {e} — SKIPPING", file=sys.stderr)
        return set()
    except OSError as e:
        print(f"  ERROR: Failed to read {report_path}: {e} — SKIPPING", file=sys.stderr)
        return set()
    
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
    """Remove dead re-exports from an __init__.py file using AST-based parsing."""
    if not dead_imports:
        return False
    
    try:
        src = pathlib.Path(init_path).read_text(encoding="utf-8")
    except OSError as e:
        print(f"  ERROR: Failed to read {init_path}: {e} — SKIPPING", file=sys.stderr)
        return False
    
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"  SYNTAX ERROR in {init_path}: {e} — SKIPPING", file=sys.stderr)
        return False
    
    # Find all ImportFrom nodes with their line numbers and symbols
    import_nodes: list[ImportNode] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            symbols = [alias.name for alias in node.names]
            # Check if any of these symbols are dead
            dead_symbols_in_import = [s for s in symbols if s in dead_imports]
            if dead_symbols_in_import:
                end_lineno = getattr(node, 'end_lineno', None) or node.lineno
                import_nodes.append({
                    'lineno': node.lineno,
                    'module': node.module,
                    'all_symbols': symbols,
                    'dead_symbols': dead_symbols_in_import,
                    'end_lineno': end_lineno
                })
    
    if not import_nodes:
        return False
    
    # Process the file to remove dead symbols
    lines = src.splitlines(keepends=True)
    skip_indices = set[int]()
    removed_any = False
    
    # Process each import node
    for imp in import_nodes:
        start_line = imp['lineno'] - 1  # 0-indexed
        end_line = imp['end_lineno'] - 1
        
        # Extract the import block
        import_block = lines[start_line:end_line + 1]
        import_text = ''.join(import_block)
        
        # For multi-line imports, we need to rebuild the block
        if '(' in import_text and ')' in import_text:
            # Parse the block to extract individual symbol lines
            kept_symbols = []
            removed_symbols = []
            
            for symbol in imp['all_symbols']:
                if symbol in imp['dead_symbols']:
                    removed_symbols.append(symbol)
                else:
                    kept_symbols.append(symbol)
            
            if not kept_symbols:
                # All symbols removed - delete entire block
                for i in range(start_line, end_line + 1):
                    skip_indices.add(i)
                removed_any = True
            else:
                # Rebuild the import with only kept symbols
                # This is complex - for now, remove the entire block and let user handle
                # TODO: Implement proper multi-line import rebuilding
                for i in range(start_line, end_line + 1):
                    skip_indices.add(i)
                removed_any = True
        else:
            # Single-line import
            if len(imp['dead_symbols']) == len(imp['all_symbols']):
                # All symbols removed - delete the line
                skip_indices.add(start_line)
                removed_any = True
            else:
                # Some symbols remain - rebuild the import
                kept_symbols = [s for s in imp['all_symbols'] if s not in imp['dead_symbols']]
                module = imp['module']
                if module:
                    new_import = f"from {module} import {', '.join(kept_symbols)}\n"
                else:
                    new_import = f"import {', '.join(kept_symbols)}\n"
                lines[start_line] = new_import
                removed_any = True
    
    if not removed_any:
        return False
    
    # Build final lines, skipping deleted indices
    final_lines = [l for i, l in enumerate(lines) if i not in skip_indices]
    
    # Remove __all__ if we removed imports
    final_output = []
    skip_all = False
    for line in final_lines:
        if removed_any and '__all__' in line:
            skip_all = True
            continue
        if skip_all and line.strip() and not line.strip().startswith('#'):
            skip_all = False
        if not skip_all:
            final_output.append(line)
    
    # Validate syntax
    new_src = "".join(final_lines)
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        print(f"  SYNTAX ERROR after modification in {init_path}: {e} — SKIPPING", file=sys.stderr)
        return False
    
    if not dry_run:
        try:
            pathlib.Path(init_path).write_text(new_src, encoding="utf-8")
        except OSError as e:
            print(f"  ERROR: Failed to write {init_path}: {e} — SKIPPING", file=sys.stderr)
            return False
    
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
        if not p.exists():
            print(f"  WARNING: Report file not found: {rp} — SKIPPING", file=sys.stderr)
            continue
        
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ERROR: Failed to parse JSON in {rp}: {e} — SKIPPING", file=sys.stderr)
            continue
        except OSError as e:
            print(f"  ERROR: Failed to read {rp}: {e} — SKIPPING", file=sys.stderr)
            continue
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
