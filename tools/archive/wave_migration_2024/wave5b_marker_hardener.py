#!/usr/bin/env python3
"""
Wave 5b: Marker and config hardening - markers.

This script hardens pytest markers across the test suite,
focusing on marker standardization, consistency, and proper usage.
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path


class MarkerHardener:
    """Hardener for pytest markers."""

    def __init__(self):
        self.hardening_stats = {
            'files_processed': 0,
            'files_modified': 0,
            'markers_found': 0,
            'markers_standardized': 0,
            'markers_added': 0,
            'errors_encountered': 0
        }
        self.modifications = []

    def scan_test_files_for_markers(self) -> list[dict]:
        """Scan test files for pytest markers."""
        print("=== Scanning Test Files for Markers ===")

        test_files_with_markers = []
        test_dir = Path('tests')

        for test_file in test_dir.rglob('test_*.py'):
            try:
                with open(test_file, encoding='utf-8') as f:
                    content = f.read()

                markers = self._extract_markers_from_file(content)
                if markers:
                    test_files_with_markers.append({
                        'file': str(test_file.relative_to(test_dir)),
                        'path': test_file,
                        'markers': markers
                    })

            except Exception as e:
                print(f"    Error scanning {test_file}: {e}")

        print(f"🔍 Found {len(test_files_with_markers)} files with markers")
        total_markers = sum(len(f['markers']) for f in test_files_with_markers)
        print(f"📊 Total markers found: {total_markers}")

        return test_files_with_markers

    def _extract_markers_from_file(self, content: str) -> list[dict]:
        """Extract markers from a test file."""
        markers = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return markers

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Check for decorators that might be markers
                for decorator in node.decorator_list:
                    marker_info = self._analyze_decorator(decorator, content)
                    if marker_info:
                        marker_info['test_function'] = node.name
                        markers.append(marker_info)

        return markers

    def _analyze_decorator(self, decorator: ast.AST, content: str) -> dict:
        """Analyze a decorator to determine if it's a pytest marker."""
        marker_info = None

        if isinstance(decorator, ast.Attribute):
            # Check for pytest.mark.*
            if (isinstance(decorator.value, ast.Name) and
                decorator.value.id == 'pytest' and
                decorator.attr == 'mark'):

                # Get the marker name
                if hasattr(decorator, 'attr') and hasattr(decorator, 'value'):
                    # This is pytest.mark.something
                    if hasattr(decorator, 'attr'):
                        marker_name = decorator.attr
                        marker_info = {
                            'type': 'pytest_marker',
                            'name': marker_name,
                            'full_decorator': ast.unparse(decorator) if hasattr(ast, 'unparse') else str(decorator)
                        }

        elif isinstance(decorator, ast.Call):
            # Check for pytest.mark.marker_name(...)
            if (isinstance(decorator.func, ast.Attribute) and
                isinstance(decorator.func.value, ast.Name) and
                decorator.func.value.id == 'pytest' and
                decorator.func.attr == 'mark'):

                if hasattr(decorator.func, 'attr'):
                    marker_name = decorator.func.attr
                    marker_info = {
                        'type': 'pytest_marker_with_args',
                        'name': marker_name,
                        'full_decorator': ast.unparse(decorator) if hasattr(ast, 'unparse') else str(decorator)
                    }

        return marker_info

    def analyze_marker_usage(self, test_files: list[dict]) -> dict:
        """Analyze marker usage patterns."""
        print("=== Analyzing Marker Usage Patterns ===")

        analysis = {
            'total_files': len(test_files),
            'total_markers': 0,
            'unique_markers': set(),
            'marker_frequency': defaultdict(int),
            'marker_issues': [],
            'standardization_needs': []
        }

        for file_info in test_files:
            for marker in file_info['markers']:
                analysis['total_markers'] += 1
                marker_name = marker['name']
                analysis['unique_markers'].add(marker_name)
                analysis['marker_frequency'][marker_name] += 1

                # Check for marker issues
                issues = self._check_marker_issues(marker)
                if issues:
                    analysis['marker_issues'].extend([
                        {**issue, 'file': file_info['file'], 'test': marker['test_function']}
                        for issue in issues
                    ])

        # Check for standardization needs
        standard_markers = {'slow', 'integration', 'unit', 'smoke', 'regression'}
        missing_standard = standard_markers - analysis['unique_markers']
        if missing_standard:
            analysis['standardization_needs'].extend([
                {'type': 'missing_standard_marker', 'marker': marker}
                for marker in missing_standard
            ])

        analysis['unique_markers'] = list(analysis['unique_markers'])

        print(f"📊 Found {len(analysis['unique_markers'])} unique markers")
        print(f"🔧 Marker issues: {len(analysis['marker_issues'])}")

        return analysis

    def _check_marker_issues(self, marker: dict) -> list[dict]:
        """Check for issues with a specific marker."""
        issues = []
        marker_name = marker['name']

        # Check for non-standard markers
        standard_markers = {'slow', 'integration', 'unit', 'smoke', 'regression', 'skip', 'skipif', 'xfail'}
        if marker_name not in standard_markers:
            issues.append({
                'type': 'non_standard_marker',
                'marker': marker_name,
                'severity': 'info'
            })

        # Check for marker naming conventions
        if not re.match(r'^[a-z][a-z0-9_]*$', marker_name):
            issues.append({
                'type': 'naming_convention',
                'marker': marker_name,
                'severity': 'warning'
            })

        return issues

    def harden_markers(self, test_files: list[dict]) -> dict:
        """Harden markers in test files."""
        print("=== Hardening Markers ===")

        # Analyze current marker usage
        analysis = self.analyze_marker_usage(test_files)

        # Harden each file
        for file_info in test_files:
            self._harden_file_markers(file_info, analysis)

        return {
            'stats': self.hardening_stats,
            'analysis': analysis,
            'modifications': self.modifications
        }

    def _harden_file_markers(self, file_info: dict, analysis: dict) -> dict:
        """Harden markers in a single file."""
        file_path = file_info['path']
        rel_path = file_info['file']

        self.hardening_stats['files_processed'] += 1

        try:
            # Read original content
            with open(file_path, encoding='utf-8') as f:
                original_content = f.read()

            # Generate hardened content
            hardened_content = self._generate_hardened_content(file_info, analysis, original_content)

            # Write back if changed
            if hardened_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(hardened_content)

                self.hardening_stats['files_modified'] += 1

                # Count markers added
                markers_added = hardened_content.count('@pytest.mark.') - original_content.count('@pytest.mark.')
                self.hardening_stats['markers_added'] += markers_added

                # Record modification
                self.modifications.append({
                    'file': rel_path,
                    'original_markers': len(file_info['markers']),
                    'markers_added': markers_added,
                    'standardization_applied': True
                })

                print(f"✅ {rel_path}: Hardened with {markers_added} marker improvements")
            else:
                print(f"⚪ {rel_path}: No marker hardening needed")

        except Exception as e:
            print(f"❌ Error hardening {rel_path}: {e}")
            self.hardening_stats['errors_encountered'] += 1

    def _generate_hardened_content(self, file_info: dict, analysis: dict, content: str) -> str:
        """Generate hardened content with improved markers."""
        lines = content.split('\n')
        hardened_lines = []

        # Track if we need to add standard markers
        markers_in_file = {marker['name'] for marker in file_info['markers']}
        standard_markers_needed = {'slow', 'integration', 'unit', 'smoke', 'regression'} - markers_in_file

        # Add appropriate markers based on file path and content
        added_markers = set()

        for line in lines:
            hardened_lines.append(line)

            # Add markers after function definition if needed
            if line.strip().startswith('def test_') and standard_markers_needed:
                # Determine appropriate markers based on context
                file_path = file_info['file']
                test_function = line.strip().split('(')[0].replace('def ', '')

                # Add markers based on file path patterns
                markers_to_add = self._determine_appropriate_markers(file_path, test_function, content)

                for marker in markers_to_add:
                    if marker in standard_markers_needed and marker not in added_markers:
                        hardened_lines.append(f"@pytest.mark.{marker}")
                        added_markers.add(marker)

        return '\n'.join(hardened_lines)

    def _determine_appropriate_markers(self, file_path: str, test_function: str, content: str) -> list[str]:
        """Determine appropriate markers for a test."""
        markers = []
        file_path_lower = file_path.lower()
        test_function_lower = test_function.lower()

        # Integration tests
        if any(path in file_path_lower for path in ['integration', 'e2e', 'end_to_end']):
            markers.append('integration')

        # Unit tests
        elif any(path in file_path_lower for path in ['unit', 'test_']):
            markers.append('unit')

        # Smoke tests
        elif any(path in file_path_lower for path in ['smoke']):
            markers.append('smoke')

        # Performance tests
        elif any(keyword in test_function_lower for keyword in ['performance', 'slow', 'benchmark']):
            markers.append('slow')

        # Regression tests
        elif any(keyword in test_function_lower for keyword in ['regression', 'bug', 'fix']):
            markers.append('regression')

        # Default to unit for unknown patterns
        if not markers:
            markers.append('unit')

        return markers

    def validate_marker_hardening(self) -> dict:
        """Validate that marker hardening was successful."""
        print("=== Validating Marker Hardening ===")

        validation = {
            'files_validated': 0,
            'hardening_confirmed': 0,
            'markers_confirmed': 0,
            'remaining_issues': []
        }

        # Check modified files
        for modification in self.modifications:
            file_path = modification['file']
            full_path = Path('tests') / file_path

            try:
                with open(full_path, encoding='utf-8') as f:
                    content = f.read()

                # Check that standard markers are present
                standard_markers = ['slow', 'integration', 'unit', 'smoke', 'regression']
                markers_found = 0

                for marker in standard_markers:
                    if f"@pytest.mark.{marker}" in content:
                        markers_found += 1

                if markers_found >= 1:  # At least 1 standard marker
                    validation['hardening_confirmed'] += 1
                    validation['markers_confirmed'] += markers_found
                else:
                    validation['remaining_issues'].append({
                        'file': file_path,
                        'issue': 'No standard markers found'
                    })

                validation['files_validated'] += 1

            except Exception as e:
                validation['remaining_issues'].append({
                    'file': file_path,
                    'issue': f'Validation error: {e}'
                })

        return validation

    def generate_wave5b_report(self) -> dict:
        """Generate Wave 5b hardening report."""
        print("=== Wave 5b: Marker and Config Hardening - Markers ===")

        # Scan for test files with markers
        test_files = self.scan_test_files_for_markers()

        # Harden markers
        hardening_results = self.harden_markers(test_files)

        # Validate hardening
        validation_results = self.validate_marker_hardening()

        # Create report
        report = {
            'wave': 'Wave 5b',
            'timestamp': '2026-03-25 21:00:00',
            'title': 'Marker and Config Hardening - Markers',
            'test_files_with_markers': len(test_files),
            'hardening_results': hardening_results,
            'validation_results': validation_results,
            'summary': {
                'test_files_with_markers': len(test_files),
                'files_processed': self.hardening_stats['files_processed'],
                'files_modified': self.hardening_stats['files_modified'],
                'markers_added': self.hardening_stats['markers_added'],
                'hardening_confirmed': validation_results['hardening_confirmed'],
                'success_rate': (validation_results['hardening_confirmed'] / max(self.hardening_stats['files_modified'], 1)) * 100
            }
        }

        # Save report
        with open('artifacts/wave5b_hardening_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 5b Summary ===")
        print(f"Test files with markers: {summary['test_files_with_markers']}")
        print(f"Files processed: {summary['files_processed']}")
        print(f"Files modified: {summary['files_modified']}")
        print(f"Markers added: {summary['markers_added']}")
        print(f"Hardening confirmed: {summary['hardening_confirmed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")

        if validation_results['remaining_issues']:
            print(f"\n⚠️  Remaining issues: {len(validation_results['remaining_issues'])}")
            for issue in validation_results['remaining_issues'][:3]:
                print(f"  - {issue['file']}: {issue['issue']}")

        print("\n📄 Report saved to: artifacts/wave5b_hardening_report.json")

        return report


def main():
    """Main execution for Wave 5b."""
    hardener = MarkerHardener()
    report = hardener.generate_wave5b_report()

    return report


if __name__ == '__main__':
    main()
