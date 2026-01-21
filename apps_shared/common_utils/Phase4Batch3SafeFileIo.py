"""
Phase 4 Batch 3: Safe File I/O (The Encoding Fix) - Hardened AST Version

Add safe_read_file/safe_write_file imports to files using open() for file I/O.

This script:
1. Uses AST to find open() calls for reading/writing
2. Adds safe_read_file/safe_write_file import if needed
3. Self-verifies syntax before writing

EXCLUDED FILES:
- file_utils.py (the implementation itself)
"""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from typing import List, Tuple, Optional, Set

# Files to EXCLUDE from refactoring
EXCLUDED_FILES = {
    "file_utils.py",
    "conftest.py",
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

SAFE_FILE_IMPORT = "from agentic_core.utils.file_utils import safe_read_file, safe_write_file"

# Pattern to detect file open calls
OPEN_PATTERN = re.compile(r'\bopen\s*\(')


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


class FileIOVisitor(ast.NodeVisitor):
    """AST visitor to find file I/O patterns and imports."""

    def __init__(self):
        self.last_import_line = 0
        self.has_safe_file_import = False
        self.has_open_calls = False

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track import statements."""
        self.last_import_line = max(self.last_import_line, node.end_lineno or node.lineno)

        if node.module == "agentic_core.utils.file_utils":
            for alias in node.names:
                if alias.name in ("safe_read_file", "safe_write_file"):
                    self.has_safe_file_import = True

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """Track import statements."""
        self.last_import_line = max(self.last_import_line, node.end_lineno or node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Find open() calls."""
        if isinstance(node.func, ast.Name) and node.func.id == 'open':
            self.has_open_calls = True

        self.generic_visit(node)


def find_safe_insertion_line(tree: ast.AST, visitor: FileIOVisitor) -> int:
    """Determine the safest line number to add the import."""
    if visitor.last_import_line > 0:
        return visitor.last_import_line

    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, (ast.Constant, ast.Str)):
        return tree.body[0].end_lineno

    return 0


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file.

    Returns:
        dict with processing results
    """
    result = {
        "file": str(file_path),
        "import_added": False,
        "skipped": False,
        "reason": None,
    }

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result["skipped"] = True
        result["reason"] = f"Read error: {e}"
        return result

    # Quick check for open() calls
    if not OPEN_PATTERN.search(content):
        result["skipped"] = True
        result["reason"] = "No open() calls found"
        return result

    # Parse AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        result["skipped"] = True
        result["reason"] = f"Pre-existing syntax error: {e}"
        return result

    visitor = FileIOVisitor()
    visitor.visit(tree)

    # Skip if no open calls found by AST
    if not visitor.has_open_calls:
        result["skipped"] = True
        result["reason"] = "No open() calls in AST"
        return result

    # Skip if already has safe file import
    if visitor.has_safe_file_import:
        result["skipped"] = True
        result["reason"] = "Already has safe_file import"
        return result

    lines = content.splitlines()

    # Add import
    import_insertion_idx = find_safe_insertion_line(tree, visitor)
    lines.insert(import_insertion_idx, SAFE_FILE_IMPORT)
    result["import_added"] = True

    # Final Safety Check
    new_content = '\n'.join(lines) + '\n'

    try:
        ast.parse(new_content)
    except SyntaxError as e:
        result["skipped"] = True
        result["reason"] = f"SAFETY ABORT: Generated invalid syntax: {e}"
        return result

    # Write
    if not dry_run:
        try:
            file_path.write_text(new_content, encoding='utf-8')
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 3: Safe File I/O")
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

    print(f"{'[DRY RUN]' if args.dry_run else '[EXECUTE]'} Phase 4 Batch 3: Safe File I/O")
    print(f"Scanning: {root}")
    print("-" * 60)

    files = find_python_files(root)
    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "imports_added": 0,
        "files_skipped": 0,
    }

    for file_path in files:
        result = process_file(file_path, dry_run=args.dry_run)
        stats["files_processed"] += 1

        if result["skipped"]:
            stats["files_skipped"] += 1
            if "Already has" not in str(result["reason"]) and "No open" not in str(result["reason"]):
                print(f"  [SKIP] {file_path.name}: {result['reason']}")
            continue

        if result["import_added"]:
            stats["files_modified"] += 1
            stats["imports_added"] += 1

            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if args.dry_run else '[MODIFIED]'} {rel_path}")

    print("-" * 60)
    print("Summary:")
    print(f"  Files processed:   {stats['files_processed']}")
    print(f"  Files modified:    {stats['files_modified']}")
    print(f"  Imports added:     {stats['imports_added']}")
    print(f"  Files skipped:     {stats['files_skipped']}")
    print("\nNote: This batch adds safe_read_file/safe_write_file imports.")
    print("Manual review recommended for actual open() replacement.")

if __name__ == "__main__":
    main()
