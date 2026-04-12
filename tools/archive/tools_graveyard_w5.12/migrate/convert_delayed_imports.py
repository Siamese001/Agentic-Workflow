#!/usr/bin/env python3
"""
Delayed Import Converter - AST-based tool to convert test files to delayed imports.

Moves problematic imports from module level into test functions to prevent
collection-time crashes. This implements PATH B from PyTest Lifecycle document.

Usage:
    # Validate mode (dry run)
    python tools/convert_delayed_imports.py --validate tests/unit/agentic_core/L0_routing/

    # Convert mode (in-place)
    python tools/convert_delayed_imports.py tests/unit/agentic_core/L0_routing/

    # Convert specific file
    python tools/convert_delayed_imports.py tests/unit/agentic_core/L0_routing/enforcement/test_execution_gateway.py
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys
from typing import Any, Dict, List, Set, Tuple

# Imports that should stay at module level (safe for collection)
SAFE_IMPORTS = {
    # Standard library
    "pytest",
    "unittest",
    "mock",
    "unittest.mock",
    "os",
    "sys",
    "pathlib",
    "datetime",
    "time",
    "uuid",
    "re",
    "json",
    "yaml",
    "csv",
    "io",
    "tempfile",
    "math",
    "random",
    "itertools",
    "functools",
    "operator",
    "dataclasses",
    "typing",
    "collections",
    "contextlib",
    "warnings",
    "logging",
    # Testing utilities
    "pytest_asyncio",
    "pytest_mock",
    "factory_boy",
    "faker",
    "freezegun",
    # Future statements
    "__future__",
}

# Imports that should be delayed (problematic for collection)
DELAYED_PATTERNS = {
    "agentic_core.",
    "apps_",
    "system_learning.",
    "tools.",
}

# Import types that should always be delayed
DELAYED_IMPORT_TYPES = {
    ast.Import,
    ast.ImportFrom,
}


class DelayedImportVisitor(ast.NodeVisitor):
    """AST visitor to identify imports that should be delayed."""

    def __init__(self) -> None:
        self.imports_to_delay: List[Tuple[ast.stmt, int]] = []
        self.safe_imports: List[Tuple[ast.stmt, int]] = []
        self.test_functions: List[ast.FunctionDef] = []
        self.has_test_functions = False

    def visit_Import(self, node: ast.Import) -> None:
        """Handle regular import statements."""
        for alias in node.names:
            if self._should_delay_import(alias.name):
                self.imports_to_delay.append((node, node.lineno))
            else:
                self.safe_imports.append((node, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle from-import statements."""
        if node.module is None:
            # from . import X (relative import)
            self.imports_to_delay.append((node, node.lineno))
        elif self._should_delay_import(node.module):
            self.imports_to_delay.append((node, node.lineno))
        else:
            self.safe_imports.append((node, node.lineno))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track test functions."""
        if node.name.startswith("test_"):
            self.has_test_functions = True
            self.test_functions.append(node)
        self.generic_visit(node)

    def _should_delay_import(self, module_name: str) -> bool:
        """Check if an import should be delayed."""
        # Check for __future__ imports (always safe)
        if module_name == "__future__":
            return False

        # Check for safe imports
        if module_name in SAFE_IMPORTS:
            return False

        # Check for delayed patterns
        for pattern in DELAYED_PATTERNS:
            if module_name.startswith(pattern):
                return True

        # Check for relative imports
        if module_name.startswith("."):
            return True

        return False


class DelayedImportTransformer(ast.NodeTransformer):
    """AST transformer to move imports into test functions."""

    def __init__(self, imports_to_delay: List[ast.stmt]) -> None:
        self.imports_to_delay = imports_to_delay
        self.delayed_imports_added: Set[str] = set()

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Remove delayed imports from module level."""
        # Keep only safe imports
        new_body = []
        for stmt in node.body:
            if stmt not in self.imports_to_delay:
                new_body.append(stmt)

        # Process remaining nodes
        node.body = new_body
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Add delayed imports at the start of test functions."""
        if node.name.startswith("test_") and self.imports_to_delay:
            # Create a key to avoid duplicate imports in the same function
            func_key = f"{node.name}_delayed"
            if func_key not in self.delayed_imports_added:
                # Add delayed imports at the beginning of the function
                new_body = []

                # Add delayed imports first
                for import_stmt in self.imports_to_delay:
                    # Clone the import statement to avoid modifying the original
                    if isinstance(import_stmt, ast.Import):
                        new_import = ast.Import(
                            names=[
                                ast.alias(name=alias.name, asname=alias.asname) for alias in import_stmt.names
                            ]
                        )
                    elif isinstance(import_stmt, ast.ImportFrom):
                        new_import = ast.ImportFrom(
                            module=import_stmt.module,
                            level=import_stmt.level,
                            names=[
                                ast.alias(name=alias.name, asname=alias.asname) for alias in import_stmt.names
                            ],
                        )
                    else:
                        continue

                    # Add the import with proper location info
                    ast.copy_location(new_import, import_stmt)
                    new_body.append(new_import)

                # Add original function body
                new_body.extend(node.body)

                # Update function body
                node.body = new_body
                self.delayed_imports_added.add(func_key)

        return self.generic_visit(node)


def analyze_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """Analyze a Python file for delayed import conversion."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        visitor = DelayedImportVisitor()
        visitor.visit(tree)

        return {
            "file": str(file_path),
            "has_test_functions": visitor.has_test_functions,
            "total_imports": len(visitor.imports_to_delay) + len(visitor.safe_imports),
            "imports_to_delay": len(visitor.imports_to_delay),
            "safe_imports": len(visitor.safe_imports),
            "test_functions": len(visitor.test_functions),
            "needs_conversion": len(visitor.imports_to_delay) > 0 and visitor.has_test_functions,
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "needs_conversion": False,
        }


def convert_file(file_path: pathlib.Path, validate: bool = False) -> Dict[str, Any]:
    """Convert a Python file to use delayed imports."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        tree = ast.parse(original_content)
        visitor = DelayedImportVisitor()
        visitor.visit(tree)

        if not visitor.imports_to_delay:
            return {
                "file": str(file_path),
                "status": "no_changes_needed",
                "imports_delayed": 0,
            }

        if validate:
            return {
                "file": str(file_path),
                "status": "would_convert",
                "imports_delayed": len(visitor.imports_to_delay),
                "safe_imports": len(visitor.safe_imports),
            }

        # Apply transformation
        transformer = DelayedImportTransformer(visitor.imports_to_delay)
        new_tree = transformer.visit(tree)

        # Fix AST locations
        ast.fix_missing_locations(new_tree)

        # Generate new code
        new_content = ast.unparse(new_tree)

        # Write back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "file": str(file_path),
            "status": "converted",
            "imports_delayed": len(visitor.imports_to_delay),
            "safe_imports": len(visitor.safe_imports),
        }

    except Exception as e:
        return {
            "file": str(file_path),
            "status": "error",
            "error": str(e),
            "imports_delayed": 0,
        }


def find_python_files(paths: List[pathlib.Path]) -> List[pathlib.Path]:
    """Find all Python files in the given paths."""
    python_files = []

    for path in paths:
        if path.is_file() and path.suffix == ".py":
            python_files.append(path)
        elif path.is_dir():
            python_files.extend(path.rglob("*.py"))

    return sorted(python_files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert test files to use delayed imports for collection safety",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=pathlib.Path,
        help="Files or directories to convert",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate mode (dry run, don't modify files)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary statistics only",
    )

    args = parser.parse_args()

    # Find all Python files
    python_files = find_python_files(args.paths)

    if not python_files:
        print("No Python files found.", file=sys.stderr)
        sys.exit(1)

    # Process files
    results = []
    summary = {
        "total_files": len(python_files),
        "processed": 0,
        "converted": 0,
        "no_changes_needed": 0,
        "errors": 0,
        "total_imports_delayed": 0,
        "total_safe_imports": 0,
    }

    for file_path in python_files:
        if args.summary:
            # Just analyze for summary
            analysis = analyze_file(file_path)
            if analysis.get("needs_conversion"):
                summary["total_imports_delayed"] += analysis["imports_to_delay"]
                summary["total_safe_imports"] += analysis["safe_imports"]
                summary["processed"] += 1
        else:
            # Full conversion
            result = convert_file(file_path, validate=args.validate)
            results.append(result)

            # Update summary
            summary["processed"] += 1
            if result["status"] == "converted":
                summary["converted"] += 1
                summary["total_imports_delayed"] += result["imports_delayed"]
                summary["total_safe_imports"] += result.get("safe_imports", 0)
            elif result["status"] == "no_changes_needed":
                summary["no_changes_needed"] += 1
            elif result["status"] == "would_convert":
                summary["converted"] += 1  # Count as would convert
                summary["total_imports_delayed"] += result["imports_delayed"]
                summary["total_safe_imports"] += result.get("safe_imports", 0)
            elif result["status"] == "error":
                summary["errors"] += 1

    # Output results
    if args.json:
        output = {
            "summary": summary,
            "results": results if not args.summary else [],
        }
        print(json.dumps(output, indent=2))
    else:
        if args.summary:
            print("Delayed Import Conversion Summary")
            print("=================================")
            print(f"Total files: {summary['total_files']}")
            print(f"Files needing conversion: {summary['processed']}")
            print(f"Imports to delay: {summary['total_imports_delayed']}")
            print(f"Safe imports (unchanged): {summary['total_safe_imports']}")
        else:
            print(f"Processed {summary['processed']} files:")
            print(f"  Converted: {summary['converted']}")
            print(f"  No changes needed: {summary['no_changes_needed']}")
            print(f"  Errors: {summary['errors']}")
            print(f"Total imports delayed: {summary['total_imports_delayed']}")

            # Show errors if any
            if summary["errors"] > 0:
                print("\nErrors:")
                for result in results:
                    if result["status"] == "error":
                        print(f"  {result['file']}: {result['error']}")


if __name__ == "__main__":
    main()
