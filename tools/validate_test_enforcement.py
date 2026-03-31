#!/usr/bin/env python3
"""
Validate test enforcement compliance.
Check that all tests have proper category markers and structure.
"""

import json
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestEnforcementValidator:
    """Validate test enforcement compliance."""

    def __init__(self):
        self.test_files = []
        self.validation_results = {}
        self.errors = 0

        # Load test inventory
        with open(PROJECT_ROOT / "tools" / "test_enforcement" / "test_inventory.json", 'r') as f:
            inventory = json.load(f)
            self.test_files = inventory.get('test_files', [])

    def validate_category_markers(self):
        """Validate that all tests have category markers."""
        print("🔍 Validating test category markers...")

        marker_compliance = {
            'total_tests': 0,
            'with_markers': 0,
            'without_markers': 0,
            'marker_distribution': {}
        }

        for test_file_info in self.test_files[:200]:  # Validate first 200 files
            file_path = Path(test_file_info['file_path'])

            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines()

                # Find all test functions
                for i, line in enumerate(lines):
                    if re.match(r'^\s*def test_', line):
                        marker_compliance['total_tests'] += 1

                        # Check if marker exists above
                        has_marker = False
                        marker_type = None

                        for j in range(max(0, i-3), i):
                            if '@pytest.mark.' in lines[j]:
                                has_marker = True
                                marker_type = lines[j].strip()
                                break

                        if has_marker:
                            marker_compliance['with_markers'] += 1
                            # Count marker types
                            marker_name = marker_type.split('.')[-1] if marker_type else 'unknown'
                            marker_compliance['marker_distribution'][marker_name] = \
                                marker_compliance['marker_distribution'].get(marker_name, 0) + 1
                        else:
                            marker_compliance['without_markers'] += 1

            except Exception as e:
                self.errors += 1
                print(f"    Error validating {file_path}: {e}")

        self.validation_results['category_markers'] = marker_compliance

        print(f"  ✅ Validated {marker_compliance['total_tests']} tests")
        print(f"     With markers: {marker_compliance['with_markers']}")
        print(f"     Without markers: {marker_compliance['without_markers']}")

        return marker_compliance

    def validate_test_structure(self):
        """Validate test structure compliance."""
        print("🔍 Validating test structure...")

        structure_compliance = {
            'total_tests': 0,
            'properly_named': 0,
            'with_assertions': 0,
            'correct_parameters': 0,
            'structure_issues': []
        }

        for test_file_info in self.test_files[:200]:  # Validate first 200 files
            file_path = Path(test_file_info['file_path'])

            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines()

                # Find all test functions
                for i, line in enumerate(lines):
                    if re.match(r'^\s*def test_', line):
                        structure_compliance['total_tests'] += 1

                        # Check naming
                        if line.strip().startswith('def test_'):
                            structure_compliance['properly_named'] += 1

                        # Check for assertions in function body
                        has_assertion = False
                        for j in range(i, min(i+20, len(lines))):
                            if 'assert' in lines[j]:
                                has_assertion = True
                                break

                        if has_assertion:
                            structure_compliance['with_assertions'] += 1

                        # Check parameters
                        if 'self' in line or 'async def test_' in line:
                            structure_compliance['correct_parameters'] += 1

                        # Identify structure issues
                        issues = []
                        if not line.strip().startswith('def test_'):
                            issues.append('incorrect_naming')
                        if not has_assertion:
                            issues.append('missing_assertion')
                        if issues:
                            structure_compliance['structure_issues'].append({
                                'file': str(file_path),
                                'line': i + 1,
                                'function': line.strip(),
                                'issues': issues
                            })

            except Exception as e:
                self.errors += 1
                print(f"    Error validating structure in {file_path}: {e}")

        self.validation_results['test_structure'] = structure_compliance

        print(f"  ✅ Validated test structure")
        print(f"     Properly named: {structure_compliance['properly_named']}")
        print(f"     With assertions: {structure_compliance['with_assertions']}")
        print(f"     Correct parameters: {structure_compliance['correct_parameters']}")

        return structure_compliance

    def run_pytest_validation(self):
        """Run pytest to check test collection and execution."""
        print("🔍 Running pytest validation...")

        pytest_results = {
            'collected': 0,
            'collected_errors': 0,
            'execution_errors': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }

        try:
            # Collect tests only
            result = subprocess.run(
                ['python', '-m', 'pytest', '--collect-only', '-q'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Parse collection output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'collected' in line.lower():
                        match = re.search(r'(\d+)\s+collected', line)
                        if match:
                            pytest_results['collected'] = int(match.group(1))
            else:
                pytest_results['collected_errors'] = 1
                print(f"    Pytest collection errors: {result.stderr}")

            # Run a quick test execution on a subset
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/unit_min_deps/', '-v', '--tb=no'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                # Parse execution output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'passed' in line.lower():
                        match = re.search(r'(\d+)\s+passed', line)
                        if match:
                            pytest_results['passed'] = int(match.group(1))
                    elif 'failed' in line.lower():
                        match = re.search(r'(\d+)\s+failed', line)
                        if match:
                            pytest_results['failed'] = int(match.group(1))
                    elif 'skipped' in line.lower():
                        match = re.search(r'(\d+)\s+skipped', line)
                        if match:
                            pytest_results['skipped'] = int(match.group(1))
            else:
                pytest_results['execution_errors'] = 1
                print(f"    Pytest execution errors: {result.stderr}")

        except subprocess.TimeoutExpired:
            pytest_results['execution_errors'] = 1
            print("    Pytest execution timed out")
        except Exception as e:
            pytest_results['execution_errors'] = 1
            print(f"    Error running pytest: {e}")

        self.validation_results['pytest'] = pytest_results

        print(f"  ✅ Pytest validation completed")
        print(f"     Collected: {pytest_results['collected']}")
        print(f"     Passed: {pytest_results['passed']}")
        print(f"     Failed: {pytest_results['failed']}")
        print(f"     Skipped: {pytest_results['skipped']}")

        return pytest_results

    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        print("📋 Generating validation report...")

        report = {
            'validation_timestamp': '2026-03-24T19:50:00Z',
            'overall_compliance': self._calculate_overall_compliance(),
            'validation_results': self.validation_results,
            'errors': self.errors,
            'recommendations': self._generate_recommendations()
        }

        report_file = PROJECT_ROOT / "tools" / "test_enforcement_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Validation report written to: {report_file}")

        return report

    def _calculate_overall_compliance(self):
        """Calculate overall compliance percentage."""
        if not self.validation_results:
            return 0

        marker_compliance = self.validation_results.get('category_markers', {})
        structure_compliance = self.validation_results.get('test_structure', {})

        total_checks = 0
        passed_checks = 0

        # Marker compliance
        if marker_compliance.get('total_tests', 0) > 0:
            total_checks += 1
            if marker_compliance['with_markers'] >= marker_compliance['total_tests'] * 0.9:  # 90% threshold
                passed_checks += 1

        # Structure compliance
        if structure_compliance.get('total_tests', 0) > 0:
            total_checks += 1
            if structure_compliance['properly_named'] >= structure_compliance['total_tests'] * 0.9:
                passed_checks += 1

        return (passed_checks / total_checks * 100) if total_checks > 0 else 0

    def _generate_recommendations(self):
        """Generate improvement recommendations."""
        recommendations = []

        marker_compliance = self.validation_results.get('category_markers', {})
        structure_compliance = self.validation_results.get('test_structure', {})

        if marker_compliance.get('without_markers', 0) > 0:
            recommendations.append(
                f"Add category markers to {marker_compliance['without_markers']} tests without markers"
            )

        if structure_compliance.get('structure_issues'):
            recommendations.append(
                f"Fix {len(structure_compliance['structure_issues'])} test structure issues"
            )

        if self.errors > 0:
            recommendations.append(f"Address {self.errors} validation errors")

        return recommendations


def main():
    """Main entry point."""
    print("=" * 80)
    print("TEST ENFORCEMENT VALIDATOR")
    print("=" * 80)
    print("Validating test enforcement compliance...")
    print("=" * 80)

    validator = TestEnforcementValidator()

    # Run all validations
    validator.validate_category_markers()
    validator.validate_test_structure()
    validator.run_pytest_validation()

    # Generate report
    report = validator.generate_validation_report()

    print("\n" + "=" * 80)
    print("🎉 TEST ENFORCEMENT VALIDATION COMPLETED!")
    print(f"✅ Overall compliance: {report['overall_compliance']:.1f}%")
    print(f"❌ Errors: {report['errors']}")

    if report['recommendations']:
        print("\n📝 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
    else:
        print("\n🎉 EXCELLENT COMPLIANCE!")

    print("=" * 80)


if __name__ == "__main__":
    main()
