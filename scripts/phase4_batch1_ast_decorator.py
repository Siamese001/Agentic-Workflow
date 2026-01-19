#!/usr/bin/env python3
"""
Phase 4 Batch 1: Result Normalization (The Decorator Sweep) - AST Version

Apply @standard_heal decorator to heal_repository methods using AST analysis.

This version uses AST to:
1. Find heal_repository method definitions
2. Check if they already have @standard_heal decorator
3. Insert decorator at the correct line position
4. Insert import at a safe location (after all existing imports)

Usage:
    python scripts/phase4_batch1_ast_decorator.py --dry-run
    python scripts/phase4_batch1_ast_decorator.py --execute
"""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from typing import List, Tuple, Optional, Set

# Files to EXCLUDE from refactoring
EXCLUDED_FILES = {
    "decorators.py",
    "conftest.py",
    "healer_mixin.py",
    "infrastructure_mixin.py",
    "SovereignBaseAgent.py",
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

STANDARD_HEAL_IMPORT = "from agentic_core.L5_safety.validators.decorators import standard_heal"


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files, excluding specified directories."""
    files = []
    for path in root.rglob("*.py"):
        if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
            continue
        if path.name in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


class HealRepositoryVisitor(ast.NodeVisitor):
    """AST visitor to find heal_repository methods and their decorators."""
    
    def __init__(self):
        self.heal_methods: List[Tuple[int, int, bool]] = []  # (line, col, has_standard_heal)
        self.imports_end_line = 0
        self.has_standard_heal_import = False
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track import statements."""
        self.imports_end_line = max(self.imports_end_line, node.end_lineno or node.lineno)
        
        # Check if this is the standard_heal import
        if node.module == "agentic_core.utils.core_extensions.decorators":
            for alias in node.names:
                if alias.name == "standard_heal":
                    self.has_standard_heal_import = True
        
        self.generic_visit(node)
        
    def visit_Import(self, node: ast.Import):
        """Track import statements."""
        self.imports_end_line = max(self.imports_end_line, node.end_lineno or node.lineno)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Find heal_repository method definitions."""
        if node.name == "heal_repository":
            # Check if it already has @standard_heal decorator
            has_decorator = False
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "standard_heal":
                    has_decorator = True
                    break
                elif isinstance(decorator, ast.Attribute) and decorator.attr == "standard_heal":
                    has_decorator = True
                    break
            
            self.heal_methods.append((node.lineno, node.col_offset, has_decorator))
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Find async heal_repository method definitions."""
        if node.name == "heal_repository":
            has_decorator = False
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "standard_heal":
                    has_decorator = True
                    break
            
            self.heal_methods.append((node.lineno, node.col_offset, has_decorator))
        
        self.generic_visit(node)


def find_last_import_line(content: str) -> int:
    """Find the last import line, handling multi-line imports correctly."""
    lines = content.split('\n')
    last_import_line = 0
    in_multiline_import = False
    paren_depth = 0
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Track parentheses depth
        paren_depth += line.count('(') - line.count(')')
        
        if stripped.startswith('import ') or stripped.startswith('from '):
            in_multiline_import = paren_depth > 0
            if paren_depth == 0:
                last_import_line = i
        elif in_multiline_import:
            if paren_depth == 0:
                last_import_line = i
                in_multiline_import = False
        elif stripped == ')' and paren_depth == 0:
            # Closing paren of multi-line import
            last_import_line = i
    
    return last_import_line


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file using AST analysis.
    
    Returns:
        dict with processing results
    """
    result = {
        "file": str(file_path),
        "import_added": False,
        "decorators_added": 0,
        "skipped": False,
        "reason": None,
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result["skipped"] = True
        result["reason"] = f"Read error: {e}"
        return result
    
    # Parse AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        result["skipped"] = True
        result["reason"] = f"Syntax error: {e}"
        return result
    
    # Visit AST to find heal_repository methods
    visitor = HealRepositoryVisitor()
    visitor.visit(tree)
    
    # Skip if no heal_repository methods
    if not visitor.heal_methods:
        result["skipped"] = True
        result["reason"] = "No heal_repository method"
        return result
    
    # Filter out methods that already have the decorator
    methods_to_decorate = [(line, col) for line, col, has_dec in visitor.heal_methods if not has_dec]
    
    if not methods_to_decorate and visitor.has_standard_heal_import:
        result["skipped"] = True
        result["reason"] = "Already has @standard_heal decorator"
        return result
    
    lines = content.split('\n')
    
    # Add import if needed
    if not visitor.has_standard_heal_import and methods_to_decorate:
        import_line = find_last_import_line(content)
        if import_line == 0:
            # No imports found, add after module docstring or at top
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        # Find end of docstring
                        quote = stripped[:3]
                        if stripped.count(quote) >= 2 and len(stripped) > 6:
                            import_line = i + 1
                            break
                        for j in range(i + 1, len(lines)):
                            if quote in lines[j]:
                                import_line = j + 1
                                break
                        break
                    elif stripped.startswith('from __future__'):
                        import_line = i + 1
                    else:
                        import_line = i
                        break
        
        # Insert import
        lines.insert(import_line, STANDARD_HEAL_IMPORT)
        result["import_added"] = True
        
        # Adjust line numbers for decorator insertion
        methods_to_decorate = [(line + 1 if line > import_line else line, col) 
                               for line, col in methods_to_decorate]
    
    # Add decorators (process in reverse order to maintain line numbers)
    for method_line, col_offset in sorted(methods_to_decorate, reverse=True):
        # Calculate indentation
        indent = ' ' * col_offset
        decorator_line = f"{indent}@standard_heal"
        
        # Insert decorator before the method definition
        lines.insert(method_line - 1, decorator_line)
        result["decorators_added"] += 1
    
    # Write if not dry run and changes were made
    if not dry_run and (result["import_added"] or result["decorators_added"] > 0):
        try:
            new_content = '\n'.join(lines)
            file_path.write_text(new_content, encoding='utf-8')
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 1: AST Decorator Sweep")
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
    
    print(f"{'[DRY RUN]' if dry_run else '[EXECUTE]'} Phase 4 Batch 1: AST Decorator Sweep")
    print(f"Scanning: {root}")
    print("-" * 60)
    
    files = find_python_files(root)
    print(f"Found {len(files)} Python files to analyze")
    
    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "imports_added": 0,
        "decorators_added": 0,
        "files_skipped": 0,
    }
    
    for file_path in files:
        result = process_file(file_path, dry_run=dry_run)
        stats["files_processed"] += 1
        
        if result["skipped"]:
            stats["files_skipped"] += 1
            continue
        
        if result["import_added"] or result["decorators_added"] > 0:
            stats["files_modified"] += 1
            stats["imports_added"] += 1 if result["import_added"] else 0
            stats["decorators_added"] += result["decorators_added"]
            
            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if dry_run else '[MODIFIED]'} {rel_path}")
            if result["import_added"]:
                print(f"    + Added standard_heal import")
            if result["decorators_added"]:
                print(f"    + Added {result['decorators_added']} @standard_heal decorator(s)")
    
    print("-" * 60)
    print("Summary:")
    print(f"  Files processed:   {stats['files_processed']}")
    print(f"  Files modified:    {stats['files_modified']}")
    print(f"  Imports added:     {stats['imports_added']}")
    print(f"  Decorators added:  {stats['decorators_added']}")
    print(f"  Files skipped:     {stats['files_skipped']}")
    
    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --execute to apply changes.")


if __name__ == "__main__":
    main()
