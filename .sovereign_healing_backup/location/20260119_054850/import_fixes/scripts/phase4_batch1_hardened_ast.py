"""
Phase 4 Batch 1: Result Normalization (The Decorator Sweep) - Hardened AST Version
"""
from __future__ import annotations

import argparse
import ast
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

STANDARD_HEAL_IMPORT = "from agentic_core.utils.core_extensions.decorators import standard_heal"


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
        self.last_import_line = 0
        self.has_standard_heal_import = False
        self.has_future_import = False
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track import statements."""
        if node.module == '__future__':
            self.has_future_import = True
            
        self.last_import_line = max(self.last_import_line, node.end_lineno or node.lineno)
        
        # Check if this is the standard_heal import
        if node.module == "agentic_core.utils.core_extensions.decorators":
            for alias in node.names:
                if alias.name == "standard_heal":
                    self.has_standard_heal_import = True
        
        self.generic_visit(node)
        
    def visit_Import(self, node: ast.Import):
        """Track import statements."""
        self.last_import_line = max(self.last_import_line, node.end_lineno or node.lineno)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Find heal_repository method definitions."""
        if node.name == "heal_repository":
            has_decorator = False
            for decorator in node.decorator_list:
                # Check for @standard_heal
                if isinstance(decorator, ast.Name) and decorator.id == "standard_heal":
                    has_decorator = True
                    break
                # Check for @decorators.standard_heal
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


def find_safe_insertion_line(tree: ast.AST, visitor: HealRepositoryVisitor) -> int:
    """
    Determine the safest line number (0-based index for list insertion) to add the import.
    Uses AST data to ensure we insert AFTER the last import block.
    """
    # 1. If imports exist, insert after the last one
    if visitor.last_import_line > 0:
        return visitor.last_import_line
    
    # 2. If no imports, check for module docstring
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, (ast.Constant, ast.Str)):
        return tree.body[0].end_lineno
        
    # 3. Default to top of file
    return 0


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
        result["reason"] = f"Pre-existing syntax error: {e}"
        return result
    
    # Visit AST
    visitor = HealRepositoryVisitor()
    visitor.visit(tree)
    
    # Skip if no heal_repository methods
    if not visitor.heal_methods:
        result["skipped"] = True
        result["reason"] = "No heal_repository method"
        return result
    
    # Filter methods needing decoration
    methods_to_decorate = [(line, col) for line, col, has_dec in visitor.heal_methods if not has_dec]
    
    if not methods_to_decorate and visitor.has_standard_heal_import:
        result["skipped"] = True
        result["reason"] = "Already compliant"
        return result
    
    lines = content.splitlines() # splitlines keeps things cleaner than split('\n')
    
    # Determine import insertion point
    import_insertion_idx = 0
    if not visitor.has_standard_heal_import and methods_to_decorate:
        import_insertion_idx = find_safe_insertion_line(tree, visitor)
        
        # Insert import
        lines.insert(import_insertion_idx, STANDARD_HEAL_IMPORT)
        result["import_added"] = True
    
    # Add decorators
    # We must process in reverse order so line insertions don't shift subsequent targets
    # Note: method_line from AST is 1-based.
    
    # If we inserted an import, all lines AFTER that point have shifted down by 1.
    # However, since we process decorators in reverse (bottom-up), and the import is usually 
    # at the top, we just need to account for the shift if the method is below the import.
    
    sorted_methods = sorted(methods_to_decorate, reverse=True)
    
    for method_line, col_offset in sorted_methods:
        # Adjust target line if it was below the inserted import
        target_idx = method_line - 1 # Convert 1-based AST line to 0-based list index
        if result["import_added"] and target_idx >= import_insertion_idx:
            target_idx += 1
            
        indent = ' ' * col_offset
        lines.insert(target_idx, f"{indent}@standard_heal")
        result["decorators_added"] += 1
    
    # Final Safety Check: Verify syntax of new content
    new_content = '\n'.join(lines) + '\n' # Ensure trailing newline
    
    try:
        ast.parse(new_content)
    except SyntaxError as e:
        result["skipped"] = True
        result["reason"] = f"SAFETY ABORT: Generated invalid syntax: {e}"
        return result

    # Write
    if not dry_run and (result["import_added"] or result["decorators_added"] > 0):
        try:
            file_path.write_text(new_content, encoding='utf-8')
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 1: Hardened AST Decorator Sweep")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--execute", action="store_true", help="Actually modify files")
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Please specify --dry-run or --execute")
        return
    
    root = Path(__file__).parent.parent / "agentic_core"
    if not root.exists():
        print(f"Error: agentic_core directory not found at {root}")
        return
    
    print(f"{'[DRY RUN]' if args.dry_run else '[EXECUTE]'} Phase 4 Batch 1: Hardened AST Sweep")
    print(f"Scanning: {root}")
    print("-" * 60)
    
    files = find_python_files(root)
    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "imports_added": 0,
        "decorators_added": 0,
        "files_skipped": 0,
    }
    
    for file_path in files:
        result = process_file(file_path, dry_run=args.dry_run)
        stats["files_processed"] += 1
        
        if result["skipped"]:
            stats["files_skipped"] += 1
            # Only print error reasons, not simple skips
            if "Already compliant" not in str(result["reason"]):
                 print(f"  [SKIP] {file_path.name}: {result['reason']}")
            continue
        
        if result["import_added"] or result["decorators_added"] > 0:
            stats["files_modified"] += 1
            stats["imports_added"] += 1 if result["import_added"] else 0
            stats["decorators_added"] += result["decorators_added"]
            
            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if args.dry_run else '[MODIFIED]'} {rel_path}")
    
    print("-" * 60)
    print("Summary:")
    print(f"  Files processed:   {stats['files_processed']}")
    print(f"  Files modified:    {stats['files_modified']}")
    print(f"  Imports added:     {stats['imports_added']}")
    print(f"  Decorators added:  {stats['decorators_added']}")
    print(f"  Files skipped:     {stats['files_skipped']}")

if __name__ == "__main__":
    main()
