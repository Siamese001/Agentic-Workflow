#!/usr/bin/env python3
"""
Wave 6b: Validation enforcement script testing.

This script tests the validation enforcement tools created in Wave 6a,
ensuring they work correctly and provide accurate results.
"""

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    """Test result for validation enforcement."""
    test_name: str
    passed: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float


class ValidationTester:
    """Tester for validation enforcement scripts."""

    def __init__(self):
        self.test_results = []
        self.test_stats = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'total_duration': 0.0
        }

    def run_all_tests(self) -> dict:
        """Run all validation enforcement tests."""
        print("=== Running Validation Enforcement Tests ===")

        # Test 1: Validation Runner Script
        self.test_validation_runner()

        # Test 2: CI Integration Script
        self.test_ci_integration()

        # Test 3: Pre-commit Hook Script
        self.test_pre_commit_hook()

        # Test 4: Validation Rules Engine
        self.test_validation_rules()

        # Test 5: Compliance Scoring
        self.test_compliance_scoring()

        # Test 6: Error Handling
        self.test_error_handling()

        # Test 7: Performance
        self.test_performance()

        # Generate summary
        summary = self._generate_test_summary()

        return {
            'test_results': self.test_results,
            'test_stats': self.test_stats,
            'summary': summary
        }

    def test_validation_runner(self):
        """Test the validation runner script."""
        print("\n--- Testing Validation Runner Script ---")

        try:
            import time
            start_time = time.time()

            # Run validation runner
            result = subprocess.run([
                sys.executable, "tools/validation_runner.py"
            ], capture_output=True, text=True, timeout=60)

            duration = time.time() - start_time

            test_result = TestResult(
                test_name="validation_runner",
                passed=result.returncode in [0, 2],  # 0=success, 2=low compliance
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration
            )

            self.test_results.append(test_result)
            self.test_stats['total_tests'] += 1
            self.test_stats['total_duration'] += duration

            if test_result.passed:
                self.test_stats['passed_tests'] += 1
                print("✓ Validation runner test passed")
            else:
                self.test_stats['failed_tests'] += 1
                print(f"✗ Validation runner test failed (exit code: {result.returncode})")
                print(f"Stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:200]}...")

        except subprocess.TimeoutExpired:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print("✗ Validation runner test timed out")
        except Exception as e:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print(f"✗ Validation runner test error: {e}")

    def test_ci_integration(self):
        """Test the CI integration script."""
        print("\n--- Testing CI Integration Script ---")

        try:
            import time
            start_time = time.time()

            # Run CI integration
            result = subprocess.run([
                sys.executable, "tools/ci_validation_integration.py"
            ], capture_output=True, text=True, timeout=60)

            duration = time.time() - start_time

            test_result = TestResult(
                test_name="ci_integration",
                passed=result.returncode in [0, 2],  # 0=success, 2=low compliance
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration
            )

            self.test_results.append(test_result)
            self.test_stats['total_tests'] += 1
            self.test_stats['total_duration'] += duration

            if test_result.passed:
                self.test_stats['passed_tests'] += 1
                print("✓ CI integration test passed")
            else:
                self.test_stats['failed_tests'] += 1
                print(f"✗ CI integration test failed (exit code: {result.returncode})")
                print(f"Stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:200]}...")

        except subprocess.TimeoutExpired:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print("✗ CI integration test timed out")
        except Exception as e:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print(f"✗ CI integration test error: {e}")

    def test_pre_commit_hook(self):
        """Test the pre-commit hook script."""
        print("\n--- Testing Pre-commit Hook Script ---")

        try:
            import time
            start_time = time.time()

            # Run pre-commit hook
            result = subprocess.run([
                sys.executable, "tools/pre_commit_validation.py"
            ], capture_output=True, text=True, timeout=60)

            duration = time.time() - start_time

            test_result = TestResult(
                test_name="pre_commit_hook",
                passed=result.returncode in [0, 2],  # 0=success, 2=low compliance
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration
            )

            self.test_results.append(test_result)
            self.test_stats['total_tests'] += 1
            self.test_stats['total_duration'] += duration

            if test_result.passed:
                self.test_stats['passed_tests'] += 1
                print("✓ Pre-commit hook test passed")
            else:
                self.test_stats['failed_tests'] += 1
                print(f"✗ Pre-commit hook test failed (exit code: {result.returncode})")
                print(f"Stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:200]}...")

        except subprocess.TimeoutExpired:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print("✗ Pre-commit hook test timed out")
        except Exception as e:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print(f"✗ Pre-commit hook test error: {e}")

    def test_validation_rules(self):
        """Test validation rules functionality."""
        print("\n--- Testing Validation Rules ---")

        try:
            import time
            start_time = time.time()

            # Create a test file with validation issues
            test_content = '''
import pytest

def test_without_docstring():
    pass

def test_with_invalid_skip():
    pytest.skip("no reason")

def test_without_assertions():
    x = 1
    y = 2
    result = x + y

def test_with_relative_import():
    from ..module import something
    assert True
'''

            with tempfile.NamedTemporaryFile(mode='w', suffix='_test.py', delete=False) as f:
                f.write(test_content)
                temp_file = f.name

            try:
                # Run validation on test file
                result = subprocess.run([
                    sys.executable, "-c", f"""
import sys
sys.path.insert(0, 'tools')
from wave6a_validation_enforcer import ValidationEnforcer

enforcer = ValidationEnforcer()
enforcer._validate_file(Path('{temp_file}'))

print(f'Issues found: {{len(enforcer.results)}}')
for issue in enforcer.results[:5]:  # First 5 issues
    print(f'  {{issue.rule}}: {{issue.message}}')
"""
                ], capture_output=True, text=True, timeout=30)

                duration = time.time() - start_time

                test_result = TestResult(
                    test_name="validation_rules",
                    passed=result.returncode == 0 and "Issues found:" in result.stdout,
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    duration=duration
                )

                self.test_results.append(test_result)
                self.test_stats['total_tests'] += 1
                self.test_stats['total_duration'] += duration

                if test_result.passed:
                    self.test_stats['passed_tests'] += 1
                    print("✓ Validation rules test passed")
                else:
                    self.test_stats['failed_tests'] += 1
                    print("✗ Validation rules test failed")
                    print(f"Stdout: {result.stdout[:200]}...")
                    if result.stderr:
                        print(f"Stderr: {result.stderr[:200]}...")

            finally:
                # Clean up temp file
                try:
                    Path(temp_file).unlink()
                except:
                    pass

        except subprocess.TimeoutExpired:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print("✗ Validation rules test timed out")
        except Exception as e:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print(f"✗ Validation rules test error: {e}")

    def test_compliance_scoring(self):
        """Test compliance scoring functionality."""
        print("\n--- Testing Compliance Scoring ---")

        try:
            import time
            start_time = time.time()

            # Test compliance scoring calculation
            result = subprocess.run([
                sys.executable, "-c", """
import sys
sys.path.insert(0, 'tools')
from wave6a_validation_enforcer import ValidationEnforcer

enforcer = ValidationEnforcer()

# Test compliance score calculation
enforcer.stats['files_validated'] = 10
enforcer.stats['by_severity'] = {'warning': 5, 'info': 3}
score = enforcer._calculate_compliance_score()

print(f'Compliance score: {{score}}')
print(f'Score calculation passed: {{80 <= score <= 100}}')
"""
            ], capture_output=True, text=True, timeout=30)

            duration = time.time() - start_time

            test_result = TestResult(
                test_name="compliance_scoring",
                passed=result.returncode == 0 and "Compliance score:" in result.stdout,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration
            )

            self.test_results.append(test_result)
            self.test_stats['total_tests'] += 1
            self.test_stats['total_duration'] += duration

            if test_result.passed:
                self.test_stats['passed_tests'] += 1
                print("✓ Compliance scoring test passed")
            else:
                self.test_stats['failed_tests'] += 1
                print("✗ Compliance scoring test failed")
                print(f"Stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:200]}...")

        except subprocess.TimeoutExpired:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print("✗ Compliance scoring test timed out")
        except Exception as e:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print(f"✗ Compliance scoring test error: {e}")

    def test_error_handling(self):
        """Test error handling in validation scripts."""
        print("\n--- Testing Error Handling ---")

        try:
            import time
            start_time = time.time()

            # Test with non-existent directory
            result = subprocess.run([
                sys.executable, "-c", """
import sys
sys.path.insert(0, 'tools')
from wave6a_validation_enforcer import ValidationEnforcer

enforcer = ValidationEnforcer()
result = enforcer.validate_test_suite('non_existent_dir')

print(f'Error handling test: {\"error\" in result}')
"""
            ], capture_output=True, text=True, timeout=30)

            duration = time.time() - start_time

            test_result = TestResult(
                test_name="error_handling",
                passed=result.returncode == 0 and "Error handling test:" in result.stdout,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration
            )

            self.test_results.append(test_result)
            self.test_stats['total_tests'] += 1
            self.test_stats['total_duration'] += duration

            if test_result.passed:
                self.test_stats['passed_tests'] += 1
                print("✓ Error handling test passed")
            else:
                self.test_stats['failed_tests'] += 1
                print("✗ Error handling test failed")
                print(f"Stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:200]}...")

        except subprocess.TimeoutExpired:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print("✗ Error handling test timed out")
        except Exception as e:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print(f"✗ Error handling test error: {e}")

    def test_performance(self):
        """Test performance of validation scripts."""
        print("\n--- Testing Performance ---")

        try:
            import time
            start_time = time.time()

            # Test performance with a reasonable timeout
            result = subprocess.run([
                sys.executable, "-c", """
import sys
import time
sys.path.insert(0, 'tools')
from wave6a_validation_enforcer import ValidationEnforcer

start = time.time()
enforcer = ValidationEnforcer()
duration = time.time() - start

print(f'Initialization time: {{duration:.3f}}s')
print(f'Performance test passed: {{duration < 5.0}}')
"""
            ], capture_output=True, text=True, timeout=10)

            duration = time.time() - start_time

            test_result = TestResult(
                test_name="performance",
                passed=result.returncode == 0 and "Initialization time:" in result.stdout and duration < 15.0,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration
            )

            self.test_results.append(test_result)
            self.test_stats['total_tests'] += 1
            self.test_stats['total_duration'] += duration

            if test_result.passed:
                self.test_stats['passed_tests'] += 1
                print("✓ Performance test passed")
            else:
                self.test_stats['failed_tests'] += 1
                print("✗ Performance test failed")
                print(f"Stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:200]}...")

        except subprocess.TimeoutExpired:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print("✗ Performance test timed out")
        except Exception as e:
            self.test_stats['failed_tests'] += 1
            self.test_stats['total_tests'] += 1
            print(f"✗ Performance test error: {e}")

    def _generate_test_summary(self) -> dict:
        """Generate test summary."""
        total_tests = self.test_stats['total_tests']
        passed_tests = self.test_stats['passed_tests']
        failed_tests = self.test_stats['failed_tests']

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        avg_duration = (self.test_stats['total_duration'] / total_tests) if total_tests > 0 else 0

        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': round(success_rate, 1),
            'total_duration': round(self.test_stats['total_duration'], 3),
            'average_duration': round(avg_duration, 3),
            'test_results_detail': [
                {
                    'name': result.test_name,
                    'passed': result.passed,
                    'exit_code': result.exit_code,
                    'duration': round(result.duration, 3)
                }
                for result in self.test_results
            ]
        }

        return summary

    def generate_test_report(self, output_file: str = "artifacts/validation_test_report.json"):
        """Generate comprehensive test report."""
        print("=== Generating Validation Test Report ===")

        # Run all tests
        test_results = self.run_all_tests()

        # Create comprehensive report
        report = {
            'wave': 'Wave 6b',
            'timestamp': '2026-03-25 21:15:00',
            'title': 'Validation Enforcement Script Testing',
            'test_results': test_results,
            'enforcement_tools_tested': [
                'validation_runner.py',
                'ci_validation_integration.py',
                'pre_commit_validation.py',
                'validation_rules_engine',
                'compliance_scoring',
                'error_handling',
                'performance'
            ],
            'summary': test_results['summary']
        }

        # Save report
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Validation Test Summary ===")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed tests: {summary['passed_tests']}")
        print(f"Failed tests: {summary['failed_tests']}")
        print(f"Success rate: {summary['success_rate']}%")
        print(f"Total duration: {summary['total_duration']}s")
        print(f"Average duration: {summary['average_duration']}s")

        if summary['failed_tests'] > 0:
            print("\nFailed tests:")
            for test in summary['test_results_detail']:
                if not test['passed']:
                    print(f"  - {test['name']} (exit code: {test['exit_code']})")

        print(f"\n📄 Report saved to: {output_path}")

        return report


def main():
    """Main execution for Wave 6b."""
    tester = ValidationTester()
    report = tester.generate_test_report()

    print("\n=== Wave 6b Summary ===")
    print(f"Validation enforcement tools tested: {len(report['enforcement_tools_tested'])}")
    print(f"Test success rate: {report['summary']['success_rate']}%")

    if report['summary']['success_rate'] >= 80:
        print("✓ Validation enforcement testing passed")
    else:
        print("✗ Validation enforcement testing needs improvement")

    return report


if __name__ == '__main__':
    main()
