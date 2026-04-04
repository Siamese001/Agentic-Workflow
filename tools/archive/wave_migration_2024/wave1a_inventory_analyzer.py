#!/usr/bin/env python3
"""
Wave 1a: Full inventory of all test files and skip patterns.

This script performs comprehensive inventory of the test suite,
identifying all test files, skip patterns, and baseline metrics.
"""

import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


class TestSuiteInventory:
    """Comprehensive test suite inventory analyzer."""

    def __init__(self):
        self.test_files = []
        self.skip_patterns = []
        self.test_methods = []
        self.fixtures = []
        self.imports = defaultdict(set)
        self.markers = set()

    def scan_test_files(self) -> dict:
        """Scan all test files in the repository."""
        print("=== Scanning Test Files ===")

        test_dir = Path('tests')
        test_files = list(test_dir.rglob('test_*.py'))

        print(f"Found {len(test_files)} test files")

        inventory = {
            'total_test_files': len(test_files),
            'test_files_by_directory': defaultdict(list),
            'test_files_by_size': [],
            'python_version_analysis': {},
            'file_structure': {}
        }

        # Analyze each test file
        for test_file in test_files:
            try:
                rel_path = test_file.relative_to(test_dir)
                parent_dir = str(rel_path.parent)

                inventory['test_files_by_directory'][parent_dir].append(str(rel_path))

                # File size analysis
                file_size = test_file.stat().st_size
                inventory['test_files_by_size'].append({
                    'file': str(rel_path),
                    'size': file_size,
                    'size_category': self._categorize_size(file_size)
                })

                # Python version analysis
                version_info = self._analyze_python_version(test_file)
                if version_info:
                    inventory['python_version_analysis'][str(rel_path)] = version_info

                # File structure analysis
                structure_info = self._analyze_file_structure(test_file)
                if structure_info:
                    inventory['file_structure'][str(rel_path)] = structure_info

            except Exception as e:
                print(f"Error analyzing {test_file}: {e}")

        return inventory

    def identify_skip_patterns(self) -> dict:
        """Identify all skip patterns in test files."""
        print("=== Identifying Skip Patterns ===")

        test_dir = Path('tests')
        skip_patterns = {
            'pytest_skip': [],
            'pytest_skipif': [],
            'pytest_xfail': [],
            'decorator_skips': [],
            'conditional_skips': [],
            'manual_skips': [],
            'commented_skips': [],
            'fixture_skips': [],
            'total_skips': 0,
            'skip_reasons': defaultdict(int)
        }

        skip_pattern_regexes = {
            'pytest_skip': re.compile(r'@pytest\.mark\.skip\s*(?:\(\s*(.*?)\s*\))?'),
            'pytest_skipif': re.compile(r'@pytest\.mark\.skipif\s*\(\s*(.*?)\s*\)'),
            'pytest_xfail': re.compile(r'@pytest\.mark\.xfail\s*(?:\(\s*(.*?)\s*\))?'),
            'decorator_skips': re.compile(r'@.*skip.*', re.IGNORECASE),
            'conditional_skips': re.compile(r'if.*skip.*:', re.IGNORECASE),
            'manual_skips': re.compile(r'pytest\.skip\s*\(\s*(.*?)\s*\)'),
            'commented_skips': re.compile(r'#.*skip.*', re.IGNORECASE),
        }

        for test_file in test_dir.rglob('test_*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    line_stripped = line.strip()

                    for pattern_type, pattern in skip_pattern_regexes.items():
                        matches = pattern.findall(line_stripped)
                        if matches:
                            for match in matches:
                                skip_info = {
                                    'file': str(test_file.relative_to(test_dir)),
                                    'line': line_num,
                                    'line_content': line.strip(),
                                    'pattern_type': pattern_type,
                                    'match': match,
                                    'reason': self._extract_skip_reason(match, pattern_type)
                                }
                                skip_patterns[pattern_type].append(skip_info)
                                skip_patterns['total_skips'] += 1

                                if skip_info['reason']:
                                    skip_patterns['skip_reasons'][skip_info['reason']] += 1

                # Check for fixture-based skips
                if 'skip' in content.lower():
                    fixture_matches = re.findall(r'def\s+(test_skip_.*|.*_skip_test)', content)
                    for match in fixture_matches:
                        skip_patterns['fixture_skips'].append({
                            'file': str(test_file.relative_to(test_dir)),
                            'fixture_name': match,
                            'type': 'fixture_based'
                        })

            except Exception as e:
                print(f"Error analyzing skips in {test_file}: {e}")

        return skip_patterns

    def analyze_test_methods(self) -> dict:
        """Analyze all test methods."""
        print("=== Analyzing Test Methods ===")

        test_dir = Path('tests')
        test_methods = {
            'total_methods': 0,
            'methods_by_file': defaultdict(list),
            'method_types': defaultdict(int),
            'parameter_analysis': defaultdict(int),
            'assertion_analysis': defaultdict(int),
            'hollowed_tests': []
        }

        for test_file in test_dir.rglob('test_*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')

                # Parse AST
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        method_info = {
                            'name': node.name,
                            'line': node.lineno,
                            'args_count': len(node.args.args),
                            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                            'has_assertions': self._has_assertions(node),
                            'is_hollowed': self._is_hollowed_test(node),
                            'docstring': ast.get_docstring(node)
                        }

                        test_methods['total_methods'] += 1
                        test_methods['methods_by_file'][str(test_file.relative_to(test_dir))].append(method_info)

                        # Method type classification
                        if method_info['is_hollowed']:
                            test_methods['method_types']['hollowed'] += 1
                            test_methods['hollowed_tests'].append({
                                'file': str(test_file.relative_to(test_dir)),
                                'method': method_info['name'],
                                'line': method_info['line']
                            })
                        elif method_info['has_assertions']:
                            test_methods['method_types']['with_assertions'] += 1
                        else:
                            test_methods['method_types']['no_assertions'] += 1

                        # Parameter analysis
                        test_methods['parameter_analysis'][method_info['args_count']] += 1

                        # Assertion analysis
                        if method_info['has_assertions']:
                            assertion_count = self._count_assertions(node)
                            test_methods['assertion_analysis'][assertion_count] += 1

            except Exception as e:
                print(f"Error analyzing methods in {test_file}: {e}")

        return test_methods

    def analyze_fixtures(self) -> dict:
        """Analyze all fixtures."""
        print("=== Analyzing Fixtures ===")

        test_dir = Path('tests')
        fixtures = {
            'total_fixtures': 0,
            'fixtures_by_file': defaultdict(list),
            'fixture_types': defaultdict(int),
            'fixture_parameters': defaultdict(int),
            'fixture_scopes': defaultdict(int)
        }

        for test_file in test_dir.rglob('test_*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not node.name.startswith('test_'):
                        # Check if it's a fixture
                        is_fixture = any(
                            self._get_decorator_name(d) == 'fixture'
                            for d in node.decorator_list
                        )

                        if is_fixture:
                            fixture_info = {
                                'name': node.name,
                                'line': node.lineno,
                                'args_count': len(node.args.args),
                                'return_type': self._infer_return_type(node),
                                'scope': self._get_fixture_scope(node)
                            }

                            fixtures['total_fixtures'] += 1
                            fixtures['fixtures_by_file'][str(test_file.relative_to(test_dir))].append(fixture_info)

                            # Fixture type classification
                            if 'temp' in node.name.lower():
                                fixtures['fixture_types']['temporary'] += 1
                            elif 'mock' in node.name.lower():
                                fixtures['fixture_types']['mock'] += 1
                            elif 'data' in node.name.lower():
                                fixtures['fixture_types']['data'] += 1
                            else:
                                fixtures['fixture_types']['other'] += 1

                            fixtures['fixture_parameters'][fixture_info['args_count']] += 1
                            fixtures['fixture_scopes'][fixture_info['scope']] += 1

            except Exception as e:
                print(f"Error analyzing fixtures in {test_file}: {e}")

        return fixtures

    def analyze_imports(self) -> dict:
        """Analyze import patterns."""
        print("=== Analyzing Imports ===")

        test_dir = Path('tests')
        imports = {
            'total_imports': 0,
            'import_types': defaultdict(int),
            'import_sources': defaultdict(int),
            'frequent_imports': Counter(),
            'problematic_imports': []
        }

        for test_file in test_dir.rglob('test_*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports['total_imports'] += 1
                            imports['import_types']['import'] += 1
                            imports['import_sources'][alias.name.split('.')[0]] += 1
                            imports['frequent_imports'][alias.name] += 1

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports['total_imports'] += 1
                            imports['import_types']['from_import'] += 1
                            imports['import_sources'][node.module.split('.')[0]] += 1

                            for alias in node.names:
                                full_import = f"{node.module}.{alias.name}" if node.module else alias.name
                                imports['frequent_imports'][full_import] += 1

                            # Check for problematic imports
                            if node.module and any(problem in node.module for problem in ['.', '..']):
                                imports['problematic_imports'].append({
                                    'file': str(test_file.relative_to(test_dir)),
                                    'import': f"from {node.module} import ...",
                                    'line': node.lineno
                                })

            except Exception as e:
                print(f"Error analyzing imports in {test_file}: {e}")

        return imports

    def _categorize_size(self, size: int) -> str:
        """Categorize file size."""
        if size < 1000:
            return 'small'
        elif size < 5000:
            return 'medium'
        elif size < 20000:
            return 'large'
        else:
            return 'very_large'

    def _analyze_python_version(self, file_path: Path) -> dict:
        """Analyze Python version requirements."""
        try:
            content = file_path.read_text(encoding='utf-8')

            version_info = {
                'has_future_imports': False,
                'has_type_hints': False,
                'has_f_strings': False,
                'has_walrus_operator': False,
                'estimated_min_version': '3.6'
            }

            # Check for version-specific features
            if 'from __future__' in content:
                version_info['has_future_imports'] = True

            if re.search(r':\s*[A-Z][a-zA-Z_]*(?:\[[^\]]*\])?\s*=', content):
                version_info['has_type_hints'] = True
                version_info['estimated_min_version'] = '3.5'

            if re.search(r'f["\'].*?\{.*?\}.*?["\']', content):
                version_info['has_f_strings'] = True
                version_info['estimated_min_version'] = '3.6'

            if ':=' in content:
                version_info['has_walrus_operator'] = True
                version_info['estimated_min_version'] = '3.8'

            return version_info

        except Exception:
            return {}

    def _analyze_file_structure(self, file_path: Path) -> dict:
        """Analyze file structure."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            structure = {
                'classes': 0,
                'functions': 0,
                'test_methods': 0,
                'fixtures': 0,
                'imports': 0,
                'docstring': ast.get_docstring(tree)
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    structure['classes'] += 1
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        structure['test_methods'] += 1
                    elif any(self._get_decorator_name(d) == 'fixture' for d in node.decorator_list):
                        structure['fixtures'] += 1
                    else:
                        structure['functions'] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    structure['imports'] += 1

            return structure

        except Exception:
            return {}

    def _extract_skip_reason(self, match: str, pattern_type: str) -> str:
        """Extract skip reason from pattern match."""
        if not match:
            return ''

        # Clean up the reason
        reason = match.strip('\'"')
        reason = re.sub(r'^reason\s*=\s*', '', reason)
        reason = re.sub(r'^.*?,\s*reason\s*=\s*', '', reason)

        return reason

    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return ''

    def _has_assertions(self, node: ast.FunctionDef) -> bool:
        """Check if function has assertions."""
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                return True
        return False

    def _is_hollowed_test(self, node: ast.FunctionDef) -> bool:
        """Check if test is hollowed (import-only or pass-only)."""
        # Check for pass-only tests
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return True

        # Check for import-only tests
        if len(node.body) <= 2:
            has_imports = False
            has_assertions = False

            for stmt in node.body:
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    has_imports = True
                elif isinstance(stmt, ast.Assert):
                    has_assertions = True

            return has_imports and not has_assertions

        return False

    def _count_assertions(self, node: ast.FunctionDef) -> int:
        """Count assertions in function."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                count += 1
        return count

    def _infer_return_type(self, node: ast.FunctionDef) -> str:
        """Infer return type of fixture."""
        # Simple heuristic based on name
        name = node.name.lower()
        if 'temp' in name or 'tmp' in name:
            return 'Path'
        elif 'mock' in name:
            return 'Mock'
        elif 'data' in name:
            return 'dict'
        elif 'config' in name:
            return 'dict'
        else:
            return 'unknown'

    def _get_fixture_scope(self, node: ast.FunctionDef) -> str:
        """Get fixture scope."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and self._get_decorator_name(decorator.func) == 'fixture':
                for keyword in decorator.keywords:
                    if keyword.arg == 'scope':
                        if isinstance(keyword.value, ast.Str):
                            return keyword.value.s
                        elif isinstance(keyword.value, ast.Name):
                            return keyword.value.id
        return 'function'  # default scope

    def generate_wave1a_report(self) -> dict:
        """Generate comprehensive Wave 1a report."""
        print("=== Generating Wave 1a Inventory Report ===")

        inventory = self.scan_test_files()
        skip_patterns = self.identify_skip_patterns()
        test_methods = self.analyze_test_methods()
        fixtures = self.analyze_fixtures()
        imports = self.analyze_imports()

        report = {
            'wave': 'Wave 1a',
            'timestamp': '2026-03-25 20:00:00',
            'title': 'Full Inventory of Test Files and Skip Patterns',
            'inventory': inventory,
            'skip_patterns': skip_patterns,
            'test_methods': test_methods,
            'fixtures': fixtures,
            'imports': imports,
            'summary': {
                'total_test_files': inventory['total_test_files'],
                'total_test_methods': test_methods['total_methods'],
                'total_fixtures': fixtures['total_fixtures'],
                'total_imports': imports['total_imports'],
                'total_skips': skip_patterns['total_skips'],
                'hollowed_tests': len(test_methods['hollowed_tests']),
                'files_with_skips': len(set(skip['file'] for skip_list in skip_patterns.values() if isinstance(skip_list, list) for skip in skip_list))
            }
        }

        return report


def main():
    """Main execution for Wave 1a."""
    print("=== Wave 1a: Full Inventory of All Test Files and Skip Patterns ===")

    inventory_analyzer = TestSuiteInventory()
    report = inventory_analyzer.generate_wave1a_report()

    # Save report
    with open('artifacts/wave1a_inventory_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    summary = report['summary']
    print("\n=== Wave 1a Summary ===")
    print(f"Total test files: {summary['total_test_files']}")
    print(f"Total test methods: {summary['total_test_methods']}")
    print(f"Total fixtures: {summary['total_fixtures']}")
    print(f"Total imports: {summary['total_imports']}")
    print(f"Total skips: {summary['total_skips']}")
    print(f"Hollowed tests: {summary['hollowed_tests']}")
    print(f"Files with skips: {summary['files_with_skips']}")

    print("\n📄 Report saved to: artifacts/wave1a_inventory_report.json")

    return report


if __name__ == '__main__':
    main()
