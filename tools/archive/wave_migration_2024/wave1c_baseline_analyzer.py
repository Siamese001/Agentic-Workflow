#!/usr/bin/env python3
"""
Wave 1c: Downgrade detection and baseline counts.

This script detects test quality downgrades and establishes baseline counts
for measuring improvements across subsequent waves.
"""

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


class BaselineAnalyzer:
    """Analyzer for detecting downgrades and establishing baselines."""

    def __init__(self):
        self.baseline_metrics = {}
        self.downgrade_indicators = []

    def establish_baseline_counts(self) -> dict:
        """Establish baseline counts for the test suite."""
        print("=== Establishing Baseline Counts ===")

        baseline = {
            'timestamp': '2026-03-25 20:10:00',
            'test_suite_metrics': self._get_test_suite_metrics(),
            'quality_metrics': self._get_quality_metrics(),
            'performance_metrics': self._get_performance_metrics(),
            'structural_metrics': self._get_structural_metrics(),
            'downgrade_risk_assessment': self._assess_downgrade_risk()
        }

        return baseline

    def _get_test_suite_metrics(self) -> dict:
        """Get comprehensive test suite metrics."""
        print("  Analyzing test suite metrics...")

        metrics = {
            'total_test_files': 0,
            'total_test_methods': 0,
            'total_fixtures': 0,
            'total_imports': 0,
            'files_with_skips': 0,
            'total_skip_instances': 0,
            'files_with_hollowed_tests': 0,
            'total_hollowed_tests': 0,
            'files_with_syntax_errors': 0,
            'total_syntax_errors': 0,
            'files_with_import_errors': 0,
            'total_import_errors': 0,
            'test_distribution': defaultdict(int),
            'skip_distribution': defaultdict(int),
            'complexity_metrics': {}
        }

        test_dir = Path('tests')

        # Count test files and basic metrics
        test_files = list(test_dir.rglob('test_*.py'))
        metrics['total_test_files'] = len(test_files)

        # Analyze each test file
        for test_file in test_files:
            try:
                # Basic file analysis
                rel_path = str(test_file.relative_to(test_dir))
                parent_dir = rel_path.split('/')[0] if '/' in rel_path else 'root'
                metrics['test_distribution'][parent_dir] += 1

                # Count test methods, skips, etc.
                with open(test_file, encoding='utf-8') as f:
                    content = f.read()

                # Count test methods
                test_methods = len([line for line in content.split('\n') if line.strip().startswith('def test_')])
                metrics['total_test_methods'] += test_methods

                # Count skip instances
                skip_count = content.lower().count('@pytest.mark.skip') + content.lower().count('pytest.skip')
                if skip_count > 0:
                    metrics['files_with_skips'] += 1
                    metrics['total_skip_instances'] += skip_count
                    metrics['skip_distribution'][parent_dir] += skip_count

                # Check for hollowed tests
                if 'pass' in content and 'def test_' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('def test_') and i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line == 'pass':
                                metrics['total_hollowed_tests'] += 1
                                metrics['files_with_hollowed_tests'] += 1
                                break

                # Syntax check
                try:
                    compile(content, str(test_file), 'exec')
                except SyntaxError:
                    metrics['files_with_syntax_errors'] += 1
                    metrics['total_syntax_errors'] += 1

                # Import check
                import_errors = 0
                try:
                    exec(content)
                except Exception as e:
                    if 'ImportError' in str(e) or 'ModuleNotFoundError' in str(e):
                        import_errors += 1

                if import_errors > 0:
                    metrics['files_with_import_errors'] += 1
                    metrics['total_import_errors'] += import_errors

            except Exception as e:
                print(f"    Error analyzing {test_file}: {e}")

        # Calculate complexity metrics
        metrics['complexity_metrics'] = {
            'avg_tests_per_file': metrics['total_test_methods'] / max(metrics['total_test_files'], 1),
            'skip_rate': metrics['total_skip_instances'] / max(metrics['total_test_methods'], 1),
            'hollowed_rate': metrics['total_hollowed_tests'] / max(metrics['total_test_methods'], 1),
            'syntax_error_rate': metrics['files_with_syntax_errors'] / max(metrics['total_test_files'], 1),
            'import_error_rate': metrics['files_with_import_errors'] / max(metrics['total_test_files'], 1)
        }

        return dict(metrics)

    def _get_quality_metrics(self) -> dict:
        """Get quality metrics for the test suite."""
        print("  Analyzing quality metrics...")

        quality = {
            'code_quality_indicators': {
                'print_statements': 0,
                'debug_statements': 0,
                'todo_comments': 0,
                'fixme_comments': 0,
                'hardcoded_values': 0,
                'magic_numbers': 0
            },
            'test_quality_indicators': {
                'tests_without_assertions': 0,
                'tests_with_single_assertion': 0,
                'tests_with_multiple_assertions': 0,
                'tests_without_docstrings': 0,
                'tests_with_generic_names': 0
            },
            'maintenance_metrics': {
                'duplicate_code_blocks': 0,
                'long_test_methods': 0,
                'complex_test_methods': 0,
                'files_with_multiple_classes': 0
            }
        }

        test_dir = Path('tests')

        for test_file in test_dir.rglob('test_*.py'):
            try:
                with open(test_file, encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')

                # Code quality indicators
                quality['code_quality_indicators']['print_statements'] += len([l for l in lines if 'print(' in l])
                quality['code_quality_indicators']['debug_statements'] += len([l for l in lines if 'pdb.' in l or 'breakpoint()' in l])
                quality['code_quality_indicators']['todo_comments'] += len([l for l in lines if '# TODO' in l.upper()])
                quality['code_quality_indicators']['fixme_comments'] += len([l for l in lines if '# FIXME' in l.upper()])

                # Test quality indicators
                test_methods = []
                current_method = None
                current_method_has_assert = False
                current_method_assert_count = 0
                current_method_lines = 0

                for line in lines:
                    stripped = line.strip()

                    if stripped.startswith('def test_'):
                        # Save previous method
                        if current_method:
                            if not current_method_has_assert:
                                quality['test_quality_indicators']['tests_without_assertions'] += 1
                            elif current_method_assert_count == 1:
                                quality['test_quality_indicators']['tests_with_single_assertion'] += 1
                            else:
                                quality['test_quality_indicators']['tests_with_multiple_assertions'] += 1

                            if current_method_lines > 50:
                                quality['maintenance_metrics']['long_test_methods'] += 1

                        # Start new method
                        current_method = stripped
                        current_method_has_assert = False
                        current_method_assert_count = 0
                        current_method_lines = 0

                        # Check for generic names
                        if any(generic in current_method.lower() for generic in ['test_', 'test_func', 'test_method']):
                            quality['test_quality_indicators']['tests_with_generic_names'] += 1

                    elif current_method and (stripped.startswith('def ') or stripped.startswith('class ') or not stripped):
                        # Method ended
                        if current_method:
                            if not current_method_has_assert:
                                quality['test_quality_indicators']['tests_without_assertions'] += 1
                            elif current_method_assert_count == 1:
                                quality['test_quality_indicators']['tests_with_single_assertion'] += 1
                            else:
                                quality['test_quality_indicators']['tests_with_multiple_assertions'] += 1

                            if current_method_lines > 50:
                                quality['maintenance_metrics']['long_test_methods'] += 1

                        current_method = None

                    elif current_method:
                        current_method_lines += 1

                        if 'assert' in stripped:
                            current_method_has_assert = True
                            current_method_assert_count += 1

                        if not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                            # Check for docstring
                            if '"""' in stripped or "'''" in stripped:
                                pass  # Skip docstring lines
                            else:
                                # Non-docstring, non-comment line
                                pass

                # Count classes
                class_count = len([l for l in lines if l.strip().startswith('class ')])
                if class_count > 1:
                    quality['maintenance_metrics']['files_with_multiple_classes'] += class_count - 1

            except Exception as e:
                print(f"    Error analyzing quality in {test_file}: {e}")

        return quality

    def _get_performance_metrics(self) -> dict:
        """Get performance metrics for the test suite."""
        print("  Analyzing performance metrics...")

        performance = {
            'collection_performance': {},
            'execution_performance': {},
            'resource_usage': {}
        }

        # Test collection performance
        try:
            start_time = time.time()
            result = subprocess.run(
                ['pytest', '--collect-only', '--quiet', '--tb=no'],
                capture_output=True,
                text=True,
                timeout=120
            )
            collection_time = time.time() - start_time

            performance['collection_performance'] = {
                'collection_time_seconds': collection_time,
                'collection_success': result.returncode == 0,
                'tests_collected': self._extract_collected_count(result.stdout)
            }
        except Exception as e:
            performance['collection_performance'] = {
                'error': str(e),
                'collection_time_seconds': -1
            }

        # File size metrics
        test_dir = Path('tests')
        file_sizes = []
        total_size = 0

        for test_file in test_dir.rglob('test_*.py'):
            try:
                size = test_file.stat().st_size
                file_sizes.append(size)
                total_size += size
            except:
                pass

        performance['resource_usage'] = {
            'total_file_size_bytes': total_size,
            'average_file_size_bytes': total_size / max(len(file_sizes), 1),
            'largest_file_size_bytes': max(file_sizes) if file_sizes else 0,
            'files_over_10kb': len([s for s in file_sizes if s > 10240])
        }

        return performance

    def _get_structural_metrics(self) -> dict:
        """Get structural metrics for the test suite."""
        print("  Analyzing structural metrics...")

        structural = {
            'directory_structure': {},
            'import_patterns': {},
            'fixture_usage': {},
            'marker_usage': {}
        }

        test_dir = Path('tests')

        # Directory structure
        for item in test_dir.iterdir():
            if item.is_dir():
                structural['directory_structure'][item.name] = {
                    'type': 'directory',
                    'test_files': len(list(item.rglob('test_*.py'))),
                    'subdirectories': len([d for d in item.iterdir() if d.is_dir()])
                }
            elif item.is_file() and item.name.startswith('test_'):
                structural['directory_structure'][item.name] = {
                    'type': 'file',
                    'size': item.stat().st_size
                }

        # Import patterns
        import_patterns = Counter()
        for test_file in test_dir.rglob('test_*.py'):
            try:
                with open(test_file, encoding='utf-8') as f:
                    content = f.read()

                # Count common import patterns
                if 'import pytest' in content:
                    import_patterns['pytest'] += 1
                if 'from unittest' in content:
                    import_patterns['unittest'] += 1
                if 'import mock' in content or 'from unittest.mock' in content:
                    import_patterns['mock'] += 1
                if 'import tempfile' in content:
                    import_patterns['tempfile'] += 1
                if 'from pathlib' in content:
                    import_patterns['pathlib'] += 1

            except:
                pass

        structural['import_patterns'] = dict(import_patterns)

        return structural

    def _assess_downgrade_risk(self) -> dict:
        """Assess risk of test quality downgrades."""
        print("  Assessing downgrade risk...")

        risk_assessment = {
            'overall_risk_level': 'medium',
            'risk_factors': [],
            'high_risk_areas': [],
            'mitigation_recommendations': []
        }

        # This would be enhanced with actual analysis
        # For now, provide a basic framework

        risk_factors = []

        # Check for high skip rates
        # (This would use actual metrics from the analysis above)

        # Check for many hollowed tests

        # Check for syntax errors

        # Check for import issues

        risk_assessment['risk_factors'] = risk_factors

        return risk_assessment

    def _extract_collected_count(self, output: str) -> int:
        """Extract collected test count from pytest output."""
        import re
        match = re.search(r'collected (\d+)', output.lower())
        return int(match.group(1)) if match else 0

    def generate_baseline_hash(self, data: dict) -> str:
        """Generate hash for baseline data."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def generate_wave1c_report(self) -> dict:
        """Generate Wave 1c baseline report."""
        print("=== Wave 1c: Downgrade Detection and Baseline Counts ===")

        baseline = self.establish_baseline_counts()
        baseline['baseline_hash'] = self.generate_baseline_hash(baseline)

        # Create summary
        test_metrics = baseline['test_suite_metrics']
        quality_metrics = baseline['quality_metrics']

        summary = {
            'baseline_hash': baseline['baseline_hash'],
            'test_files': test_metrics['total_test_files'],
            'test_methods': test_metrics['total_test_methods'],
            'skip_instances': test_metrics['total_skip_instances'],
            'hollowed_tests': test_metrics['total_hollowed_tests'],
            'syntax_errors': test_metrics['total_syntax_errors'],
            'import_errors': test_metrics['total_import_errors'],
            'print_statements': quality_metrics['code_quality_indicators']['print_statements'],
            'tests_without_assertions': quality_metrics['test_quality_indicators']['tests_without_assertions']
        }

        baseline['summary'] = summary

        # Save report
        with open('artifacts/wave1c_baseline_report.json', 'w') as f:
            json.dump(baseline, f, indent=2)

        # Print summary
        print("\n=== Wave 1c Summary ===")
        print(f"Baseline Hash: {baseline['baseline_hash'][:12]}...")
        print(f"Test Files: {summary['test_files']}")
        print(f"Test Methods: {summary['test_methods']}")
        print(f"Skip Instances: {summary['skip_instances']}")
        print(f"Hollowed Tests: {summary['hollowed_tests']}")
        print(f"Syntax Errors: {summary['syntax_errors']}")
        print(f"Import Errors: {summary['import_errors']}")
        print(f"Print Statements: {summary['print_statements']}")
        print(f"Tests Without Assertions: {summary['tests_without_assertions']}")

        print("\n📄 Baseline report saved to: artifacts/wave1c_baseline_report.json")

        return baseline


def main():
    """Main execution for Wave 1c."""

    analyzer = BaselineAnalyzer()
    report = analyzer.generate_wave1c_report()

    return report


if __name__ == '__main__':
    main()
