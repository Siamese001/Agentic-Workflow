#!/usr/bin/env python3
"""
Wave 5a: Identify remaining test quality issues and anti-patterns.

This script analyzes the test suite for remaining quality issues,
anti-patterns, and areas for improvement after Waves 1-4.
"""

import ast
import json
import re
from collections import Counter
from pathlib import Path


class TestQualityAnalyzer(ast.NodeVisitor):
    """AST visitor to identify test quality issues and anti-patterns."""

    def __init__(self):
        self.issues = []
        self.current_class = None
        self.current_function = None
        self.imports = set()
        self.fixtures = set()
        self.mocks = set()
        self.assertions = []
        self.test_methods = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name

        if node.name.startswith('test_'):
            self.test_methods.append(node.name)
            self._analyze_test_method(node)

        self.generic_visit(node)
        self.current_function = old_function

    def _analyze_test_method(self, node):
        """Analyze a test method for quality issues."""
        method_body = ast.get_source_segment(open(node.end_lineno).read(), node) if hasattr(node, 'end_lineno') else None

        # Check for various anti-patterns
        self._check_long_methods(node)
        self._check_multiple_assertions(node)
        self._check_hardcoded_values(node)
        self._check_missing_teardown(node)
        self._check_test_isolation(node)
        self._check_assertion_quality(node)
        self._check_mock_usage(node)
        self._check_fixture_usage(node)

    def _check_long_methods(self, node):
        """Check for overly long test methods."""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            lines = node.end_lineno - node.lineno
            if lines > 50:  # Very long test method
                self.issues.append({
                    'type': 'long_test_method',
                    'severity': 'medium',
                    'function': self.current_function,
                    'class': self.current_class,
                    'line': node.lineno,
                    'message': f'Test method is {lines} lines long (consider splitting)',
                    'suggestion': 'Break into multiple smaller test methods'
                })

    def _check_multiple_assertions(self, node):
        """Check for too many assertions in a single test."""
        assertion_count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                assertion_count += 1

        if assertion_count > 10:  # Too many assertions
            self.issues.append({
                'type': 'too_many_assertions',
                'severity': 'medium',
                'function': self.current_function,
                'class': self.current_class,
                'line': node.lineno,
                'message': f'Test has {assertion_count} assertions (consider splitting)',
                'suggestion': 'Split into multiple focused test methods'
            })

    def _check_hardcoded_values(self, node):
        """Check for hardcoded magic numbers and strings."""
        for child in ast.walk(node):
            if isinstance(child, ast.Constant):
                if isinstance(child.value, (int, float)) and child.value not in [0, 1, -1, 10, 100]:
                    self.issues.append({
                        'type': 'hardcoded_value',
                        'severity': 'low',
                        'function': self.current_function,
                        'class': self.current_class,
                        'line': getattr(child, 'lineno', 0),
                        'message': f'Hardcoded value: {child.value}',
                        'suggestion': 'Use named constants or test data factories'
                    })
                elif isinstance(child.value, str) and len(child.value) > 50:
                    # Long hardcoded strings
                    self.issues.append({
                        'type': 'hardcoded_string',
                        'severity': 'low',
                        'function': self.current_function,
                        'class': self.current_class,
                        'line': getattr(child, 'lineno', 0),
                        'message': f'Long hardcoded string ({len(child.value)} chars)',
                        'suggestion': 'Use test data factories or fixtures'
                    })

    def _check_missing_teardown(self, node):
        """Check for tests that create resources but don't clean up."""
        creates_resources = False
        has_cleanup = False

        for child in ast.walk(node):
            # Look for resource creation patterns
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                    if func_name in ['open', 'TemporaryFile', 'mkdtemp', 'NamedTemporaryFile']:
                        creates_resources = True
                elif isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['mkdir', 'write', 'create']:
                        creates_resources = True

            # Look for cleanup patterns
            elif isinstance(child, ast.With):
                has_cleanup = True
                break

        if creates_resources and not has_cleanup:
            self.issues.append({
                'type': 'missing_cleanup',
                'severity': 'high',
                'function': self.current_function,
                'class': self.current_class,
                'line': node.lineno,
                'message': 'Test creates resources but may not clean them up',
                'suggestion': 'Use context managers (with statements) or fixtures'
            })

    def _check_test_isolation(self, node):
        """Check for tests that might have side effects."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    # Look for potentially problematic calls
                    if child.func.attr in ['write', 'delete', 'remove', 'rmdir']:
                        self.issues.append({
                            'type': 'potential_side_effect',
                            'severity': 'high',
                            'function': self.current_function,
                            'class': self.current_class,
                            'line': getattr(child, 'lineno', 0),
                            'message': f'Potentially problematic call: {child.func.attr}',
                            'suggestion': 'Use fixtures or temp directories for file operations'
                        })

    def _check_assertion_quality(self, node):
        """Check for poor assertion patterns."""
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                # Check for assertions without messages
                if not (hasattr(child, 'msg') and child.msg):
                    self.issues.append({
                        'type': 'assertion_without_message',
                        'severity': 'low',
                        'function': self.current_function,
                        'class': self.current_class,
                        'line': getattr(child, 'lineno', 0),
                        'message': 'Assertion without descriptive message',
                        'suggestion': 'Add descriptive message to assertions'
                    })

    def _check_mock_usage(self, node):
        """Check for mock usage patterns."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['patch', 'MagicMock', 'Mock']:
                        self.mocks.add(self.current_function)

    def _check_fixture_usage(self, node):
        """Check for fixture usage."""
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if child.id in ['temp_dir', 'tmp_path', 'fixture', 'monkeypatch']:
                    self.fixtures.add(self.current_function)


def analyze_test_file(file_path: Path) -> dict:
    """Analyze a single test file for quality issues."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)

        analyzer = TestQualityAnalyzer()
        analyzer.visit(tree)

        # Additional regex-based checks
        regex_issues = []

        # Check for TODO/FIXME comments in tests
        todo_pattern = re.compile(r'#\s*(TODO|FIXME|XXX|HACK)\s*[:].*', re.IGNORECASE)
        for match in todo_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            regex_issues.append({
                'type': 'todo_comment',
                'severity': 'medium',
                'line': line_num,
                'message': f'TODO/FIXME comment found: {match.group().strip()}',
                'suggestion': 'Address the TODO or remove if no longer relevant'
            })

        # Check for print statements in tests
        print_pattern = re.compile(r'print\s*\(')
        for match in print_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            regex_issues.append({
                'type': 'print_statement',
                'severity': 'low',
                'line': line_num,
                'message': 'Print statement in test',
                'suggestion': 'Use proper assertions or logging instead of print'
            })

        # Check for sleep statements
        sleep_pattern = re.compile(r'time\.sleep\s*\(')
        for match in sleep_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            regex_issues.append({
                'type': 'sleep_statement',
                'severity': 'medium',
                'line': line_num,
                'message': 'time.sleep in test (potential performance issue)',
                'suggestion': 'Use mock time or avoid sleeps in tests'
            })

        all_issues = analyzer.issues + regex_issues

        return {
            'file': str(file_path),
            'test_methods': analyzer.test_methods,
            'imports': list(analyzer.imports),
            'fixtures': list(analyzer.fixtures),
            'mocks': list(analyzer.mocks),
            'total_issues': len(all_issues),
            'issues': all_issues,
            'severity_counts': Counter(issue['severity'] for issue in all_issues),
            'issue_types': Counter(issue['type'] for issue in all_issues)
        }

    except Exception as e:
        return {
            'file': str(file_path),
            'error': str(e),
            'total_issues': 0,
            'issues': [],
            'test_methods': [],
            'imports': [],
            'fixtures': [],
            'mocks': [],
            'severity_counts': {},
            'issue_types': {}
        }


def analyze_test_suite():
    """Analyze the entire test suite for quality issues."""
    print("=== Wave 5a: Identifying Remaining Test Quality Issues ===")

    test_dir = Path('tests')
    results = []

    print("Scanning test files for quality issues...")

    for test_file in test_dir.rglob('test_*.py'):
        if test_file.is_file():
            result = analyze_test_file(test_file)
            results.append(result)

            if result['total_issues'] > 0:
                high = result['severity_counts'].get('high', 0)
                medium = result['severity_counts'].get('medium', 0)
                low = result['severity_counts'].get('low', 0)
                print(f"  {test_file.name}: {result['total_issues']} issues (H:{high} M:{medium} L:{low})")

    # Summary statistics
    total_files = len(results)
    files_with_issues = len([r for r in results if r['total_issues'] > 0])
    total_issues = sum(r['total_issues'] for r in results)

    # Aggregate severity counts
    all_severity_counts = Counter()
    all_issue_types = Counter()

    for result in results:
        all_severity_counts.update(result['severity_counts'])
        all_issue_types.update(result['issue_types'])

    print("\n=== Test Quality Analysis ===")
    print(f"Total test files: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues found: {total_issues}")

    print("\n=== Issues by Severity ===")
    for severity in ['high', 'medium', 'low']:
        count = all_severity_counts.get(severity, 0)
        if count > 0:
            print(f"{severity.capitalize()}: {count}")

    print("\n=== Top Issue Types ===")
    for issue_type, count in all_issue_types.most_common(10):
        print(f"{issue_type}: {count}")

    # Find files with most issues
    files_with_most_issues = sorted(
        [r for r in results if r['total_issues'] > 0],
        key=lambda x: x['total_issues'],
        reverse=True
    )[:10]

    if files_with_most_issues:
        print("\n=== Files with Most Issues ===")
        for result in files_with_most_issues:
            high = result['severity_counts'].get('high', 0)
            print(f"  {Path(result['file']).name}: {result['total_issues']} issues (H:{high})")

    # Save detailed results
    output = {
        'summary': {
            'total_files': total_files,
            'files_with_issues': files_with_issues,
            'total_issues': total_issues,
            'severity_counts': dict(all_severity_counts),
            'issue_types': dict(all_issue_types)
        },
        'all_results': results
    }

    with open('artifacts/test_quality_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nDetailed results saved to: artifacts/test_quality_analysis.json")

    return output


def main():
    """Main execution."""
    results = analyze_test_suite()

    # Make recommendations for next waves
    print("\n=== Recommendations for Wave 5b-5h ===")

    high_issues = results['summary']['severity_counts'].get('high', 0)
    medium_issues = results['summary']['severity_counts'].get('medium', 0)

    if high_issues > 0:
        print(f"Wave 5b: Fix {high_issues} high-severity issues (test isolation, side effects)")

    if medium_issues > 0:
        print(f"Wave 5c: Address {medium_issues} medium-severity issues (performance, long methods)")

    if results['summary']['issue_types'].get('hardcoded_value', 0) > 0:
        print(f"Wave 5g: Create test data factories for {results['summary']['issue_types']['hardcoded_value']} hardcoded values")

    if results['summary']['issue_types'].get('todo_comment', 0) > 0:
        print(f"Wave 5f: Address {results['summary']['issue_types']['todo_comment']} TODO comments")


if __name__ == '__main__':
    main()
