#!/usr/bin/env python3
"""
Wave 3a: Identify hollowed tests (import-only, no behavioral assertions).

Hollowed tests are test files that:
1. Only import modules/classes/functions
2. Have no actual test assertions or behavioral checks
3. May have placeholder methods like "pass" or empty asserts
4. Were created during governance hardening to ensure imports work
"""

import ast
import json
from pathlib import Path


class HollowedTestAnalyzer(ast.NodeVisitor):
    """AST visitor to identify hollowed test patterns."""

    def __init__(self):
        self.imports: list[str] = []
        self.assertions: list[str] = []
        self.test_methods: list[dict] = []
        self.current_class = None
        self.has_behavior = False

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            method_info = {
                "name": node.name,
                "class": self.current_class,
                "has_assertions": False,
                "has_behavior": False,
                "lines": len(node.body),
                "is_hollow": True,
            }

            # Check for assertions and behavior
            for stmt in node.body:
                if isinstance(stmt, ast.Assert):
                    method_info["has_assertions"] = True
                    self.assertions.append(
                        f"{self.current_class}.{node.name}" if self.current_class else node.name
                    )

                # Check for non-trivial behavior
                if not isinstance(stmt, (ast.Pass, ast.Expr, ast.AnnAssign)):
                    if not (
                        isinstance(stmt, ast.Assign)
                        and isinstance(stmt.value, ast.Constant)
                        and stmt.value.value is None
                    ):
                        method_info["has_behavior"] = True
                        self.has_behavior = True

            # Determine if hollow
            method_info["is_hollow"] = (
                not method_info["has_assertions"]
                and not method_info["has_behavior"]
                and method_info["lines"] <= 3  # Usually just pass/docstring
            )

            self.test_methods.append(method_info)

        self.generic_visit(node)


def analyze_test_file(file_path: Path) -> dict:
    """Analyze a single test file for hollowed patterns."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        analyzer = HollowedTestAnalyzer()
        analyzer.visit(tree)

        hollow_methods = [m for m in analyzer.test_methods if m["is_hollow"]]

        return {
            "file": str(file_path),
            "total_methods": len(analyzer.test_methods),
            "hollow_methods": len(hollow_methods),
            "hollow_details": hollow_methods,
            "imports": analyzer.imports,
            "is_hollow_file": len(hollow_methods) == len(analyzer.test_methods)
            and len(analyzer.test_methods) > 0,
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "total_methods": 0,
            "hollow_methods": 0,
            "hollow_details": [],
            "imports": [],
            "is_hollow_file": False,
        }


def main():
    """Find all hollowed test files."""
    test_dir = Path("tests")
    results = []

    print("Scanning for hollowed tests...")

    for test_file in test_dir.rglob("test_*.py"):
        if test_file.is_file():
            result = analyze_test_file(test_file)
            results.append(result)

            if result["hollow_methods"] > 0:
                print(
                    f"  {result['file']}: {result['hollow_methods']}/{result['total_methods']} hollow methods"
                )

    # Summary statistics
    total_files = len(results)
    files_with_hollow = len([r for r in results if r["hollow_methods"] > 0])
    total_hollow_methods = sum(r["hollow_methods"] for r in results)
    total_methods = sum(r["total_methods"] for r in results)

    print("\n=== Hollowed Test Analysis ===")
    print(f"Total test files: {total_files}")
    print(f"Files with hollow tests: {files_with_hollow}")
    print(f"Total hollow methods: {total_hollow_methods}/{total_methods}")
    print(
        f"Hollow percentage: {100 * total_hollow_methods / total_methods:.1f}%"
        if total_methods > 0
        else "N/A"
    )

    # Save detailed results
    output = {
        "summary": {
            "total_files": total_files,
            "files_with_hollow": files_with_hollow,
            "total_hollow_methods": total_hollow_methods,
            "total_methods": total_methods,
            "hollow_percentage": 100 * total_hollow_methods / total_methods if total_methods > 0 else 0,
        },
        "files": results,
    }

    with open("artifacts/hollowed_tests_analysis.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nDetailed results saved to: artifacts/hollowed_tests_analysis.json")

    # Show most hollow files
    hollow_files = [r for r in results if r["is_hollow_file"]]
    if hollow_files:
        print(f"\n=== Completely Hollow Files ({len(hollow_files)}) ===")
        for f in sorted(hollow_files, key=lambda x: x["hollow_methods"], reverse=True)[:10]:
            print(f"  {f['file']}: {f['hollow_methods']} hollow methods")


if __name__ == "__main__":
    main()
