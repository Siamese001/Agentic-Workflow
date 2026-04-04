#!/usr/bin/env python3
"""
Wave 4a: Identify guardian swallow patterns in test files.

This script identifies test files that use guardian swallow patterns
that should be converted to proper fixture patterns.
"""

import ast
import json
import re
from pathlib import Path


class GuardianSwallowAnalyzer(ast.NodeVisitor):
    """AST visitor to identify guardian swallow patterns."""

    def __init__(self):
        self.swallow_patterns: list[dict] = []
        self.fixture_patterns: list[dict] = []
        self.current_class = None
        self.current_function = None

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name

        # Check for guardian swallow patterns in this function
        self._check_swallow_patterns(node)

        self.generic_visit(node)
        self.current_function = old_function

    def _check_swallow_patterns(self, node):
        """Check for guardian swallow patterns in a function."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Try):
                self._analyze_try_except(stmt)
            elif isinstance(stmt, ast.With):
                self._analyze_with_context(stmt)

    def _analyze_try_except(self, node):
        """Analyze try-except blocks for guardian swallow patterns."""
        for handler in node.handlers:
            if isinstance(handler.type, ast.Name):
                exception_name = handler.type.id
            elif isinstance(handler.type, ast.Attribute):
                exception_name = f"{handler.type.value.id}.{handler.type.attr}"
            else:
                continue

            # Check for guardian swallow patterns
            for stmt in handler.body:
                if self._is_guardian_swallow(stmt, exception_name):
                    self.swallow_patterns.append({
                        'type': 'try_except',
                        'exception': exception_name,
                        'class': self.current_class,
                        'function': self.current_function,
                        'line': getattr(stmt, 'lineno', 0),
                        'pattern': self._extract_pattern(stmt)
                    })

    def _analyze_with_context(self, node):
        """Analyze with blocks for guardian swallow patterns."""
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Name):
                    func_name = item.context_expr.func.id
                elif isinstance(item.context_expr.func, ast.Attribute):
                    func_name = f"{item.context_expr.func.value.id}.{item.context_expr.func.attr}"
                else:
                    continue

                # Check for pytest.raises or similar context managers
                if func_name in ['pytest.raises', 'temp_file', 'mock_patch']:
                    self.fixture_patterns.append({
                        'type': 'context_manager',
                        'context': func_name,
                        'class': self.current_class,
                        'function': self.current_function,
                        'line': getattr(item, 'lineno', 0)
                    })

    def _is_guardian_swallow(self, stmt, exception_name):
        """Check if a statement is a guardian swallow pattern."""
        if isinstance(stmt, ast.Pass):
            return True
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            return str(stmt.value.value).startswith('# guardian:')
        elif isinstance(stmt, ast.Assign):
            # Check for assignment to None or similar swallow pattern
            if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                if stmt.targets[0].id in ['swallowed', 'ignored', '_']:
                    return True
        return False

    def _extract_pattern(self, stmt):
        """Extract the swallow pattern from a statement."""
        if isinstance(stmt, ast.Pass):
            return "pass"
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            return str(stmt.value.value)
        elif isinstance(stmt, ast.Assign):
            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            return f"{targets} = ..."
        return "unknown"


def find_guardian_swallow_patterns(file_path: Path) -> dict:
    """Find guardian swallow patterns in a test file."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # First check with regex for common patterns
        swallow_regex = re.compile(
            r'# guardian: allow-[a-zA-Z_-]+(?:.*--.*)?|'
            r'except\s+\w+.*:\s*pass|'
            r'except\s+\w+.*:\s*#\s*guardian|'
            r'#\s*guardian:\s*allow-silent-swallow',
            re.MULTILINE
        )

        regex_matches = swallow_regex.findall(content)

        # Then parse with AST for more detailed analysis
        try:
            tree = ast.parse(content)
            analyzer = GuardianSwallowAnalyzer()
            analyzer.visit(tree)

            return {
                'file': str(file_path),
                'regex_matches': len(regex_matches),
                'swallow_patterns': analyzer.swallow_patterns,
                'fixture_patterns': analyzer.fixture_patterns,
                'total_swallows': len(analyzer.swallow_patterns),
                'total_fixtures': len(analyzer.fixture_patterns),
                'needs_conversion': len(analyzer.swallow_patterns) > 0 or len(regex_matches) > 0
            }
        except SyntaxError:
            # File has syntax errors, report regex matches only
            return {
                'file': str(file_path),
                'regex_matches': len(regex_matches),
                'swallow_patterns': [],
                'fixture_patterns': [],
                'total_swallows': 0,
                'total_fixtures': 0,
                'needs_conversion': len(regex_matches) > 0,
                'syntax_error': True
            }

    except Exception as e:
        return {
            'file': str(file_path),
            'error': str(e),
            'regex_matches': 0,
            'swallow_patterns': [],
            'fixture_patterns': [],
            'total_swallows': 0,
            'total_fixtures': 0,
            'needs_conversion': False
        }


def group_files_by_layer(results: list[dict]) -> dict[str, list[dict]]:
    """Group analysis results by layer."""
    layers = {
        'L0_routing': [],
        'L1_cognition': [],
        'L2_execution': [],
        'L3_orchestration': [],
        'L4_state': [],
        'L5_safety': [],
        'L6_observability': [],
        'other': []
    }

    for result in results:
        if 'error' in result:
            continue

        file_path = result['file']
        assigned = False

        for layer in ['L0_routing', 'L1_cognition', 'L2_execution', 'L3_orchestration', 'L4_state', 'L5_safety', 'L6_observability']:
            if layer in file_path:
                layers[layer].append(result)
                assigned = True
                break

        if not assigned:
            layers['other'].append(result)

    return layers


def main():
    """Find all guardian swallow patterns in test files."""
    print("=== Wave 4a: Identifying Guardian Swallow Patterns ===")

    test_dir = Path('tests')
    results = []

    print("Scanning test files for guardian swallow patterns...")

    for test_file in test_dir.rglob('test_*.py'):
        if test_file.is_file():
            result = find_guardian_swallow_patterns(test_file)
            results.append(result)

            if result.get('needs_conversion', False):
                swallows = result.get('total_swallows', 0)
                regex_matches = result.get('regex_matches', 0)
                fixtures = result.get('total_fixtures', 0)
                print(f"  {result['file']}: {swallows} swallows, {regex_matches} regex, {fixtures} fixtures")

    # Group by layer
    layers = group_files_by_layer(results)

    # Summary statistics
    total_files = len(results)
    files_needing_conversion = len([r for r in results if r.get('needs_conversion', False)])
    total_swallow_patterns = sum(r.get('total_swallows', 0) for r in results)
    total_regex_matches = sum(r.get('regex_matches', 0) for r in results)
    total_fixture_patterns = sum(r.get('total_fixtures', 0) for r in results)

    print("\n=== Guardian Swallow Analysis ===")
    print(f"Total test files: {total_files}")
    print(f"Files needing conversion: {files_needing_conversion}")
    print(f"Total swallow patterns: {total_swallow_patterns}")
    print(f"Total regex matches: {total_regex_matches}")
    print(f"Total fixture patterns: {total_fixture_patterns}")

    print("\n=== By Layer ===")
    for layer, files in layers.items():
        if files:
            needs_conversion = len([f for f in files if f.get('needs_conversion', False)])
            swallows = sum(f.get('total_swallows', 0) for f in files)
            regex_matches = sum(f.get('regex_matches', 0) for f in files)
            print(f"{layer}: {needs_conversion}/{len(files)} files, {swallows} swallows, {regex_matches} regex")

    # Save detailed results
    output = {
        'summary': {
            'total_files': total_files,
            'files_needing_conversion': files_needing_conversion,
            'total_swallow_patterns': total_swallow_patterns,
            'total_regex_matches': total_regex_matches,
            'total_fixture_patterns': total_fixture_patterns
        },
        'layers': layers,
        'all_results': results
    }

    with open('artifacts/guardian_swallow_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nDetailed results saved to: artifacts/guardian_swallow_analysis.json")

    # Show files needing most conversion
    files_needing = [r for r in results if r.get('needs_conversion', False)]
    if files_needing:
        print("\n=== Top Files Needing Conversion ===")
        sorted_files = sorted(files_needing,
                             key=lambda x: x.get('total_swallows', 0) + x.get('regex_matches', 0),
                             reverse=True)
        for file_info in sorted_files[:10]:
            swallows = file_info.get('total_swallows', 0)
            regex_matches = file_info.get('regex_matches', 0)
            total = swallows + regex_matches
            print(f"  {file_info['file']}: {total} patterns ({swallows} swallows, {regex_matches} regex)")


if __name__ == '__main__':
    main()
