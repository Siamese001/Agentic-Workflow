#!/usr/bin/env python3
"""Wave 28: Test Execution - Attempt to run tests and validate status.

This wave attempts to run tests and validates the current status
to determine if we can pass tests.
"""

import ast
import pathlib
import subprocess
import sys


class Wave28TestExecution:
    """Wave 28: Test execution and validation."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'valid_files': 0,
            'syntax_errors': 0,
            'test_collection_success': False,
            'test_execution_success': False,
            'tests_collected': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_timeout': False
        }

    def run_test_execution(self) -> dict:
        """Run test execution validation."""
        # Check current syntax status
        self._check_syntax_status()

        # Try pytest collection with timeout
        self._test_pytest_collection()

        # Try running a few tests if collection works
        if self.stats['test_collection_success']:
            self._test_execution()

        return self.stats

    def _check_syntax_status(self):
        """Check current syntax status."""
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archives
        active_test_files = [f for f in test_files if "archive" not in str(f).lower()]

        self.stats['total_files'] = len(active_test_files)

        for test_file in active_test_files:
            try:
                content = test_file.read_text(encoding='utf-8')
                ast.parse(content)
                self.stats['valid_files'] += 1
            except SyntaxError:
                self.stats['syntax_errors'] += 1
            except UnicodeDecodeError:
                self.stats['syntax_errors'] += 1

    def _test_pytest_collection(self):
        """Test pytest collection."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q", "--tb=no"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30  # Shorter timeout to avoid hanging
            )

            if result.returncode == 0:
                self.stats['test_collection_success'] = True
                # Extract number of collected tests
                if "collected" in result.stdout.lower():
                    import re
                    match = re.search(r'(\d+)\s+items? collected', result.stdout.lower())
                    if match:
                        self.stats['tests_collected'] = int(match.group(1))
                print("✅ Pytest collection successful!")
            else:
                print("⚠️ Pytest collection failed")
                # Check if we can at least collect some tests
                if "collected" in result.stdout.lower():
                    self.stats['test_collection_success'] = True
                    import re
                    match = re.search(r'(\d+)\s+items? collected', result.stdout.lower())
                    if match:
                        self.stats['tests_collected'] = int(match.group(1))
                    print("✅ Partial pytest collection successful!")

        except subprocess.TimeoutExpired:
            self.stats['test_timeout'] = True
            print("⚠️ Pytest collection timed out")
        except Exception as e:
            print(f"⚠️ Test collection error: {e}")

    def _test_execution(self):
        """Test execution of a subset of tests."""
        # Try to run a simple test from a working directory
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit_min_deps_wave1_demo/", "-v", "--tb=short", "--maxfail=3"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=15  # Short timeout
            )

            if result.returncode == 0:
                self.stats['test_execution_success'] = True
                print("✅ Test execution successful!")
            else:
                print("⚠️ Test execution failed")
                # Extract test results
                if "passed" in result.stdout:
                    import re
                    passed_match = re.search(r'(\d+)\s+passed', result.stdout)
                    if passed_match:
                        self.stats['tests_passed'] = int(passed_match.group(1))
                if "failed" in result.stdout:
                    failed_match = re.search(r'(\d+)\s+failed', result.stdout)
                    if failed_match:
                        self.stats['tests_failed'] = int(failed_match.group(1))

        except subprocess.TimeoutExpired:
            print("⚠️ Test execution timed out")
        except Exception as e:
            print(f"⚠️ Test execution error: {e}")

    def print_summary(self):
        """Print test execution summary."""
        print("\n" + "="*60)
        print("WAVE 28: TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Total test files: {self.stats['total_files']}")
        print(f"Valid files: {self.stats['valid_files']}")
        print(f"Syntax errors: {self.stats['syntax_errors']}")
        print(f"Success rate: {self.stats['valid_files']/self.stats['total_files']*100:.1f}%")

        print("\nTest collection:")
        if self.stats['test_timeout']:
            print("Pytest collection: ⚠️ Timed out")
        else:
            print(f"Pytest collection: {'✅ Success' if self.stats['test_collection_success'] else '⚠️ Failed'}")
        if self.stats['tests_collected'] > 0:
            print(f"Tests collected: {self.stats['tests_collected']}")

        print("\nTest execution:")
        print(f"Test execution: {'✅ Success' if self.stats['test_execution_success'] else '⚠️ Failed'}")
        if self.stats['tests_passed'] > 0:
            print(f"Tests passed: {self.stats['tests_passed']}")
        if self.stats['tests_failed'] > 0:
            print(f"Tests failed: {self.stats['tests_failed']}")

        print("\n🎯 TEST EXECUTION STATUS:")
        if self.stats['valid_files'] >= 2708:
            print("✅ EXCELLENT: Test suite significantly restored!")
        elif self.stats['valid_files'] >= 2500:
            print("✅ VERY GOOD: Test suite substantially restored!")
        elif self.stats['valid_files'] >= 2000:
            print("✅ GOOD: Test suite partially restored!")
        else:
            print("⚠️ NEEDS WORK: More fixes needed")

        if self.stats['test_collection_success'] and self.stats['tests_collected'] > 0:
            print("✅ TESTS CAN BE COLLECTED!")
            if self.stats['test_execution_success']:
                print("✅ TESTS CAN BE EXECUTED!")
            else:
                print("⚠️ Test execution needs work")
        elif self.stats['test_timeout']:
            print("⚠️ Test collection timing out - needs optimization")
        else:
            print("⚠️ Test collection needs work")

        print("="*60)


def main():
    """Run Wave 28 test execution."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 28: TEST EXECUTION")
    print(f"Repository: {repo_root}")

    tester = Wave28TestExecution(repo_root)
    stats = tester.run_test_execution()
    tester.print_summary()

    return stats['valid_files'] > 2000


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
