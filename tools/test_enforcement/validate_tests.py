#!/usr/bin/env python3
"""
Test Enforcement Validation Script

SEVERITY SSOT: Uses agentic_core.L5_safety.config.severity.SeverityLevel

Rules:
- no pytest.skip allowed without marker
- no ImportError skip in core tests
- all importorskip must be inside optional tests
- all tests must have category marker
- fail build if violations exist
"""

import ast
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.config.severity import SeverityLevel


class TestValidator:
    """Validate test files according to enforcement rules."""

    def __init__(self):
        self.violations = []

        # Required markers for each category
        self.category_markers = {
            'CORE': ['@pytest.mark.core'],
            'OPTIONAL': ['@pytest.mark.optional', '@pytest.mark.aws', '@pytest.mark.gpu', '@pytest.mark.db'],
            'PLATFORM-SPECIFIC': ['@pytest.mark.platform', '@pytest.mark.windows', '@pytest.mark.linux'],
            'EXTERNAL': ['@pytest.mark.external'],
            'EXPERIMENTAL': ['@pytest.mark.experimental']
        }

    def validate_test_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Validate a single test file."""
        violations = []

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            validator = ValidationVisitor(str(file_path), self.category_markers)
            validator.visit(tree)

            violations.extend(validator.violations)

        except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            violations.append({
                'file_path': str(file_path),
                'line_number': e.lineno or 0,
                'violation_type': 'syntax_error',
                'severity': SeverityLevel.HIGH.value,
                'description': f'Syntax error: {e}',
                'suggested_fix': 'Fix syntax error before validation'
            })
        except Exception as e:
            violations.append({
                'file_path': str(file_path),
                'line_number': 0,
                'violation_type': 'parse_error',
                'severity': SeverityLevel.HIGH.value,
                'description': f'Parse error: {e}',
                'suggested_fix': 'Fix file parsing issue'
            })

        return violations

    def validate_all_tests(self, test_files: list[Path]) -> dict[str, Any]:
        """Validate all test files."""
        print(f"🔍 Validating {len(test_files)} test files...")

        all_violations = []

        for i, test_file in enumerate(test_files):
            if i % 100 == 0:
                print(f"  Validating {i}/{len(test_files)}: {test_file.name}")

            violations = self.validate_test_file(test_file)
            all_violations.extend(violations)

        # Build validation report
        report = {
            "metadata": {
                "validation_timestamp": "2026-03-24T18:31:00Z",
                "total_files_validated": len(test_files),
                "total_violations": len(all_violations),
                "validator_version": "1.0"
            },
            "summary": self._build_summary(all_violations),
            "violations": all_violations
        }

        return report

    def _build_summary(self, violations: list[dict[str, Any]]) -> dict[str, Any]:
        """Build summary statistics."""
        by_type = {}
        by_severity = {
            SeverityLevel.HIGH.value: 0,
            SeverityLevel.MEDIUM.value: 0,
            SeverityLevel.LOW.value: 0,
        }

        for violation in violations:
            vtype = violation['violation_type']
            severity = violation['severity']

            by_type[vtype] = by_type.get(vtype, 0) + 1
            by_severity[severity] += 1

        return {
            "by_type": by_type,
            "by_severity": by_severity
        }


class ValidationVisitor(ast.NodeVisitor):
    """AST visitor to validate test patterns."""

    def __init__(self, file_path: str, category_markers: dict[str, list[str]]):
        self.file_path = file_path
        self.category_markers = category_markers
        self.violations = []
        self.current_function = None
        self.current_markers = []
        self.imports = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name.startswith('test_'):
            self.current_function = node.name
            self.current_markers = []

            # Check decorators
            self.check_decorators(node)

            # Visit function body
            self.generic_visit(node)

            # Validate function
            self.validate_function(node)

            self.current_function = None
            self.current_markers = []
        else:
            self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name.startswith('test_'):
            self.current_function = node.name
            self.current_markers = []

            self.check_decorators(node)
            self.generic_visit(node)
            self.validate_function(node)

            self.current_function = None
            self.current_markers = []
        else:
            self.generic_visit(node)

    def check_decorators(self, node):
        """Extract pytest markers from decorators."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                # Check for pytest.mark.*
                if (isinstance(decorator.value, ast.Name) and
                    decorator.value.id == 'pytest' and
                    isinstance(decorator.attr, str) and
                    decorator.attr.startswith('mark')):

                    marker_name = decorator.attr
                    if marker_name == 'mark':
                        # Handle pytest.mark.something
                        if isinstance(decorator, ast.Attribute) and hasattr(decorator, 'attr'):
                            marker_name = f"mark.{decorator.attr}"

                    self.current_markers.append(marker_name)

    def validate_function(self, node):
        """Validate a test function."""
        if not self.current_function:
            return

        # Rule: All tests must have category marker
        has_category_marker = any(
            any(marker in m for marker in self._get_all_category_markers())
            for m in self.current_markers
        )

        if not has_category_marker:
            self.violations.append({
                'file_path': self.file_path,
                'line_number': node.lineno,
                'violation_type': 'missing_category_marker',
                'severity': 'MEDIUM',
                'description': f'Test {self.current_function} lacks category marker',
                'suggested_fix': 'Add @pytest.mark.core/optional/platform/external/experimental'
            })

    def visit_Call(self, node: ast.Call):
        """Check for improper skip calls."""
        if not self.current_function:
            self.generic_visit(node)
            return

        # Check pytest.skip calls
        if (isinstance(node.func, ast.Attribute) and
            node.func.attr == 'skip'):

            # Rule: pytest.skip requires marker context
            if not self.current_markers:
                self.violations.append({
                    'file_path': self.file_path,
                    'line_number': node.lineno,
                    'violation_type': 'unmarked_skip',
                    'severity': 'HIGH',
                    'description': f'Test {self.current_function} uses pytest.skip without marker',
                    'suggested_fix': 'Add @pytest.mark.optional/external marker or remove skip'
                })

        # Check pytest.importorskip calls
        elif (isinstance(node.func, ast.Attribute) and
              node.func.attr == 'importorskip'):

            # Rule: importorskip must be in optional/external tests
            allowed_markers = ['mark.optional', 'mark.external', 'mark.platform', 'mark.experimental']
            has_allowed_marker = any(marker in m for m in self.current_markers for marker in allowed_markers)

            if not has_allowed_marker:
                self.violations.append({
                    'file_path': self.file_path,
                    'line_number': node.lineno,
                    'violation_type': 'unmarked_importorskip',
                    'severity': 'HIGH',
                    'description': f'Test {self.current_function} uses importorskip without proper marker',
                    'suggested_fix': 'Add @pytest.mark.optional/external/platform marker'
                })

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        """Check for try/except ImportError patterns."""
        if not self.current_function:
            self.generic_visit(node)
            return

        for handler in node.handlers:
            if (isinstance(handler.type, ast.Name) and
                handler.type.id == 'ImportError'):

                # Rule: No ImportError skip in core tests
                if 'mark.core' in self.current_markers:
                    self.violations.append({
                        'file_path': self.file_path,
                        'line_number': node.lineno,
                        'violation_type': 'core_import_error_skip',
                        'severity': 'HIGH',
                        'description': f'Core test {self.current_function} uses ImportError skip',
                        'suggested_fix': 'Remove ImportError handling or reclassify as optional'
                    })
                else:
                    # Rule: ImportError skips should use importorskip
                    self.violations.append({
                        'file_path': self.file_path,
                        'line_number': node.lineno,
                        'violation_type': 'import_error_pattern',
                        'severity': 'MEDIUM',
                        'description': f'Test {self.current_function} uses try/except ImportError pattern',
                        'suggested_fix': 'Use pytest.importorskip with proper marker'
                    })

        self.generic_visit(node)

    def _get_all_category_markers(self) -> list[str]:
        """Get all category marker strings."""
        all_markers = []
        for markers in self.category_markers.values():
            all_markers.extend(markers)
        return all_markers


def find_test_files(root_dir: Path) -> list[Path]:
    """Find all test files."""
    test_files = []

    # Same patterns as inventory builder
    tests_dir = root_dir / "tests"
    if tests_dir.exists():
        test_files.extend(tests_dir.rglob("*.py"))

    test_files.extend(root_dir.rglob("*_test.py"))
    test_files.extend(root_dir.rglob("test_*.py"))

    # Remove duplicates and filter
    unique_files = set()
    for file_path in test_files:
        if file_path.is_file() and file_path.name != "__init__.py":
            unique_files.add(file_path)

    return sorted(list(unique_files))


def main():
    """Main entry point."""
    print("=" * 80)
    print("TEST ENFORCEMENT VALIDATOR")
    print("=" * 80)

    # Find test files
    test_files = find_test_files(PROJECT_ROOT)
    print(f"Found {len(test_files)} test files")

    # Validate tests
    validator = TestValidator()
    report = validator.validate_all_tests(test_files)

    # Write validation report
    output_dir = PROJECT_ROOT / "tools" / "test_enforcement"
    output_dir.mkdir(exist_ok=True)

    validation_file = output_dir / "test_validation_report.json"
    with open(validation_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, sort_keys=True)

    print(f"✅ Validation report written to: {validation_file}")

    # Print summary
    summary = report["summary"]
    print("\n📊 VALIDATION SUMMARY:")
    print(f"  Files validated: {report['metadata']['total_files_validated']}")
    print(f"  Total violations: {report['metadata']['total_violations']}")

    print("\nBy severity:")
    for severity, count in summary["by_severity"].items():
        print(f"  {severity}: {count}")

    print("\nBy type:")
    for vtype, count in summary["by_type"].items():
        print(f"  {vtype}: {count}")

    # Exit with error code if high severity violations
    high_count = summary["by_severity"]["HIGH"]
    if high_count > 0:
        print(f"\n❌ VALIDATION FAILED: {high_count} HIGH severity violations found")
        print("Fix violations before proceeding")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION PASSED: No HIGH severity violations")
        print("Test enforcement rules satisfied")

    print("=" * 80)


if __name__ == "__main__":
    main()
