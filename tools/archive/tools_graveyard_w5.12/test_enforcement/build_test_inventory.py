#!/usr/bin/env python3
"""
Build complete test surface inventory for ImportError-based skip analysis.

Scans entire repository for:
- test files (tests/, *_test.py, test_*.py)
- skip patterns (pytest.skip, importorskip, try/except ImportError)
- conditional imports
- dependency references
"""

import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class TestInventory:
    file_path: str
    test_name: str
    skip_type: str  # import_error, marker, runtime_condition, none
    dependency: str  # what's being imported/skipped
    current_behavior: str  # skip/fail/pass
    inferred_category: str  # initial guess
    line_number: int = 0
    skip_reason: str = ""


class TestVisitor(ast.NodeVisitor):
    """AST visitor to extract test patterns."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tests: list[TestInventory] = []
        self.current_function = None
        self.imports: set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name.startswith("test_"):
            self.current_function = node.name
            # Check for decorators first
            self.check_decorators(node)
            # Then visit function body
            self.generic_visit(node)
            # If no skip found, record as normal test
            if not any(t.test_name == node.name for t in self.tests):
                self.tests.append(
                    TestInventory(
                        file_path=self.file_path,
                        test_name=node.name,
                        skip_type="none",
                        dependency="",
                        current_behavior="pass",
                        inferred_category="core",  # Default assumption
                        line_number=node.lineno,
                    )
                )
        self.current_function = None
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name.startswith("test_"):
            self.current_function = node.name
            self.check_decorators(node)
            self.generic_visit(node)
            if not any(t.test_name == node.name for t in self.tests):
                self.tests.append(
                    TestInventory(
                        file_path=self.file_path,
                        test_name=node.name,
                        skip_type="none",
                        dependency="",
                        current_behavior="pass",
                        inferred_category="core",
                        line_number=node.lineno,
                    )
                )
        self.current_function = None
        self.generic_visit(node)

    def check_decorators(self, node):
        """Check for pytest markers and skip decorators."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # Check pytest.skip
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "skip":
                    self.extract_skip_info(decorator, "marker")
                # Check pytest.importorskip
                elif isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "importorskip":
                    self.extract_importorskip_info(decorator)

    def visit_Call(self, node: ast.Call):
        """Check for pytest.skip calls in function body."""
        if isinstance(node.func, ast.Attribute) and node.func.attr == "skip":
            self.extract_skip_info(node, "runtime_condition")
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        """Check for try/except ImportError patterns."""
        if self.current_function:
            for handler in node.handlers:
                if isinstance(handler.type, ast.Name) and handler.type.id == "ImportError":
                    # Found ImportError handling
                    self.extract_importerror_info(node, handler)
        self.generic_visit(node)

    def extract_skip_info(self, node: ast.Call, skip_type: str):
        """Extract information from pytest.skip calls."""
        if not self.current_function:
            return

        dependency = ""
        reason = ""

        if node.args:
            # Try to extract reason from first argument
            if isinstance(node.args[0], ast.Constant):
                reason = node.args[0].value or ""
            elif isinstance(node.args[0], ast.Str):
                reason = node.args[0].s

        # Try to infer dependency from reason
        if reason:
            deps = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)", reason)
            dependency = deps[0] if deps else reason

        self.tests.append(
            TestInventory(
                file_path=self.file_path,
                test_name=self.current_function,
                skip_type=skip_type,
                dependency=dependency,
                current_behavior="skip",
                inferred_category="optional",  # Skip suggests optional
                line_number=node.lineno,
                skip_reason=reason,
            )
        )

    def extract_importorskip_info(self, node: ast.Call):
        """Extract information from pytest.importorskip calls."""
        if not self.current_function:
            return

        dependency = ""
        if node.args:
            if isinstance(node.args[0], ast.Constant):
                dependency = node.args[0].value or ""
            elif isinstance(node.args[0], ast.Str):
                dependency = node.args[0].s

        self.tests.append(
            TestInventory(
                file_path=self.file_path,
                test_name=self.current_function,
                skip_type="import_error",
                dependency=dependency,
                current_behavior="skip",
                inferred_category="optional",
                line_number=node.lineno,
                skip_reason=f"Missing dependency: {dependency}",
            )
        )

    def extract_importerror_info(self, try_node: ast.Try):
        """Extract information from try/except ImportError patterns."""
        if not self.current_function:
            return

        # Look for import statements in try block
        imported_deps = []
        for stmt in try_node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    imported_deps.append(alias.name)
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module:
                    imported_deps.append(stmt.module)

        dependency = imported_deps[0] if imported_deps else "unknown"

        self.tests.append(
            TestInventory(
                file_path=self.file_path,
                test_name=self.current_function,
                skip_type="import_error",
                dependency=dependency,
                current_behavior="skip",
                inferred_category="optional",
                line_number=try_node.lineno,
                skip_reason=f"ImportError for {dependency}",
            )
        )


def find_test_files(root_dir: Path) -> list[Path]:
    """Find all test files in the repository."""
    test_files = []

    # Pattern 1: tests/ directory
    tests_dir = root_dir / "tests"
    if tests_dir.exists():
        test_files.extend(tests_dir.rglob("*.py"))

    # Pattern 2: *_test.py files
    test_files.extend(root_dir.rglob("*_test.py"))

    # Pattern 3: test_*.py files
    test_files.extend(root_dir.rglob("test_*.py"))

    # Remove duplicates and filter out non-test files
    unique_files = set()
    for file_path in test_files:
        if file_path.is_file() and file_path.name != "__init__.py":
            unique_files.add(file_path)

    return sorted(list(unique_files))


def scan_test_file(file_path: Path) -> list[TestInventory]:
    """Scan a single test file for patterns."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        visitor = TestVisitor(str(file_path.relative_to(PROJECT_ROOT)))
        visitor.visit(tree)

        return visitor.tests

    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        print(f"Syntax error in {file_path}: {e}")
        return []
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"Error scanning {file_path}: {e}")
        return []


def build_inventory() -> dict[str, Any]:
    """Build complete test inventory."""
    print("🔍 Building complete test surface inventory...")

    # Find all test files
    test_files = find_test_files(PROJECT_ROOT)
    print(f"Found {len(test_files)} test files")

    # Scan each test file
    all_tests = []
    for i, test_file in enumerate(test_files):
        if i % 100 == 0:
            print(f"  Scanning {i}/{len(test_files)}: {test_file.name}")

        tests = scan_test_file(test_file)
        all_tests.extend(tests)

    print(f"  Total tests found: {len(all_tests)}")

    # Build inventory structure
    inventory = {
        "metadata": {
            "scan_timestamp": "2026-03-24T18:31:00Z",
            "total_test_files": len(test_files),
            "total_tests": len(all_tests),
            "scanner_version": "1.0",
        },
        "tests": [],
    }

    # Convert tests to dict format
    for test in all_tests:
        test_dict = asdict(test)
        inventory["tests"].append(test_dict)

    # Add summary statistics
    skip_types = {}
    categories = {}
    behaviors = {}

    for test in all_tests:
        skip_types[test.skip_type] = skip_types.get(test.skip_type, 0) + 1
        categories[test.inferred_category] = categories.get(test.inferred_category, 0) + 1
        behaviors[test.current_behavior] = behaviors.get(test.current_behavior, 0) + 1

    inventory["summary"] = {
        "skip_types": skip_types,
        "categories": categories,
        "behaviors": behaviors,
    }

    return inventory


def main():
    """Main entry point."""
    print("=" * 80)
    print("TEST SURFACE INVENTORY BUILDER")
    print("=" * 80)

    inventory = build_inventory()

    # Write inventory to file
    output_dir = PROJECT_ROOT / "tools" / "test_enforcement"
    output_dir.mkdir(exist_ok=True)

    inventory_file = output_dir / "test_inventory.json"
    with open(inventory_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, sort_keys=True)

    print(f"\n✅ Inventory written to: {inventory_file}")

    # Print summary
    summary = inventory["summary"]
    print("\n📊 SUMMARY:")
    print(f"  Total tests: {inventory['metadata']['total_tests']}")
    print(f"  Skip types: {summary['skip_types']}")
    print(f"  Categories: {summary['categories']}")
    print(f"  Behaviors: {summary['behaviors']}")

    # Highlight potential violations
    import_error_skips = summary["skip_types"].get("import_error", 0)
    if import_error_skips > 0:
        print(f"\n⚠️  FOUND {import_error_skips} ImportError-based skips - NEEDS REVIEW!")

    print("\n" + "=" * 80)
    print("NEXT STEP: Classify tests into MECE categories")
    print("=" * 80)


if __name__ == "__main__":
    main()
