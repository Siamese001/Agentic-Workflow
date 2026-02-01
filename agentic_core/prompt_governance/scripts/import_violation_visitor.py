#!/usr/bin/env python3
"""
Layer Boundary Enforcement Script (Phase 5)

Ensures prompt_governance (Low Level) does not import from higher layers
to prevent circular dependencies and architectural violations.
"""

import ast
import sys
from pathlib import Path

# Forbidden import namespaces (higher layers)
FORBIDDEN_IMPORTS = {
    "agentic_core.L1_cognition",
    "agentic_core.L2_resources",
    "agentic_core.L3_orchestration",
    "agentic_core.L4_coordination",
    "agentic_core.L5_safety",
    "agentic_core.L6_observability",
}


class ImportViolationVisitor(ast.NodeVisitor):
    """AST visitor to detect forbidden imports."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations = []

    def visit_Import(self, node):
        """Check 'import x.y.z' statements."""
        for alias in node.names:
            import_path = alias.name
            self._check_import(import_path, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Check 'from x.y.z import ...' statements."""
        if node.module:
            import_path = node.module
            self._check_import(import_path, node.lineno)
        self.generic_visit(node)

    def _check_import(self, import_path: str, line: int):
        """Check if import path violates layer boundaries."""
        for forbidden in FORBIDDEN_IMPORTS:
            if import_path.startswith(forbidden):
                self.violations.append(
                    {
                        "file": str(self.file_path),
                        "line": line,
                        "import_statement": import_path,
                        "violated_layer": forbidden,
                        "violation_type": "UPWARD_IMPORT",
                    }
                )


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in the given directory."""
    python_files = []
    for file_path in directory.rglob("*.py"):
        if file_path.is_file():
            python_files.append(file_path)
    return python_files


def analyze_file(file_path: Path) -> list[dict]:
    """Analyze a single Python file for import violations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content, filename=str(file_path))

        # Visit AST to find violations
        visitor = ImportViolationVisitor(file_path)
        visitor.visit(tree)

        return visitor.violations

    except SyntaxError as e:
        return [
            {
                "file": str(file_path),
                "line": e.lineno or 0,
                "import_statement": "SYNTAX_ERROR",
                "violated_layer": "N/A",
                "violation_type": "SYNTAX_ERROR",
                "error": str(e),
            }
        ]
    except Exception as e:
        return [
            {
                "file": str(file_path),
                "line": 0,
                "import_statement": "PARSE_ERROR",
                "violated_layer": "N/A",
                "violation_type": "PARSE_ERROR",
                "error": str(e),
            }
        ]


def enforce_layer_boundaries(prompt_governance_dir: Path) -> list[dict]:
    """Enforce layer boundaries across all Python files in prompt_governance."""
    all_violations = []

    # Find all Python files
    python_files = find_python_files(prompt_governance_dir)

    print(f"Scanning {len(python_files)} Python files...")

    for file_path in python_files:
        violations = analyze_file(file_path)
        all_violations.extend(violations)

    return all_violations


def main():
    # Determine paths
    script_dir = Path(__file__).parent
    prompt_governance_dir = script_dir.parent

    print("Layer Boundary Enforcement Audit (Phase 5)")
    print("=" * 50)
    print(f"Directory: {prompt_governance_dir}")
    print("Forbidden Imports:")
    for forbidden in sorted(FORBIDDEN_IMPORTS):
        print(f"  ❌ {forbidden}")
    print()

    # Run enforcement check
    violations = enforce_layer_boundaries(prompt_governance_dir)

    # Filter out non-violation errors for summary
    import_violations = [v for v in violations if v["violation_type"] == "UPWARD_IMPORT"]
    syntax_errors = [
        v for v in violations if v["violation_type"] in ["SYNTAX_ERROR", "PARSE_ERROR"]
    ]

    # Report results
    print("RESULTS:")
    print(f"  Files scanned: {len(find_python_files(prompt_governance_dir))}")
    print(f"  Import violations: {len(import_violations)}")
    print(f"  Syntax errors: {len(syntax_errors)}")
    print()

    if import_violations:
        print("🚨 LAYER BOUNDARY VIOLATIONS:")
        print("   (prompt_governance importing from higher layers)")
        print()

        # Group by file
        violations_by_file = {}
        for violation in import_violations:
            file_path = violation["file"]
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)

        for file_path, file_violations in violations_by_file.items():
            print(f"  📁 {file_path}")
            for violation in file_violations:
                print(f"    Line {violation['line']}: import {violation['import_statement']}")
                print(f"    ❌ Violates: {violation['violated_layer']}")
            print()

        print("⚠️  ARCHITECTURAL RISK:")
        print("   Upward imports create circular dependency risks")
        print("   and violate the layered architecture principles.")
        print()

    if syntax_errors:
        print("🔍 SYNTAX/PARSE ERRORS:")
        for error in syntax_errors:
            print(f"  📁 {error['file']}")
            if error.get("line"):
                print(f"    Line {error['line']}: {error.get('error', 'Unknown error')}")
            else:
                print(f"    {error.get('error', 'Unknown error')}")
        print()

    # Exit code
    if import_violations:
        print("❌ AUDIT FAILED - Layer boundary violations detected")
        print("   Refactor to remove upward imports from higher layers.")
        sys.exit(1)
    elif syntax_errors:
        print("⚠️  AUDIT WARNING - Syntax errors detected")
        print("   Fix syntax errors before proceeding.")
        sys.exit(2)
    else:
        print("✅ AUDIT PASSED - No layer boundary violations")
        print("   prompt_governance respects architectural boundaries.")
        sys.exit(0)


if __name__ == "__main__":
    main()
