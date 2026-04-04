#!/usr/bin/env python3
"""Wave 17: Test Validation - Run tests and validate current status.

This wave runs a subset of tests to validate our current progress
and identify the specific issues remaining.
"""

import ast
import pathlib
import subprocess
import sys


class Wave17TestValidation:
    """Wave 17: Test validation and status check."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'valid_files': 0,
            'syntax_errors': 0,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }

    def validate_status(self) -> dict:
        """Validate current status and run some tests."""
        # Check syntax status
        self._check_syntax_status()

        # Run a subset of tests
        self._run_test_subset()

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

    def _run_test_subset(self):
        """Run a subset of tests to validate functionality."""
        # Try to run a few tests from different categories
        test_categories = [
            "tests/unit_min_deps_wave1_demo/",
            "tests/smoke/",
            "tests/audit/"
        ]

        for category in test_categories:
            category_path = self.tests_dir / category
            if category_path.exists():
                try:
                    # Run pytest on this category
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", str(category_path), "-v", "--tb=short"],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    self.stats['tests_run'] += 1
                    if result.returncode == 0:
                        self.stats['tests_passed'] += 1
                    else:
                        self.stats['tests_failed'] += 1

                except subprocess.TimeoutExpired:
                    self.stats['tests_failed'] += 1
                except Exception:
                    self.stats['tests_failed'] += 1

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("WAVE 17: TEST VALIDATION SUMMARY")
        print("="*60)
        print(f"Total test files: {self.stats['total_files']}")
        print(f"Valid files: {self.stats['valid_files']}")
        print(f"Syntax errors: {self.stats['syntax_errors']}")
        print(f"Success rate: {self.stats['valid_files']/self.stats['total_files']*100:.1f}%")

        print("\nTest subset results:")
        print(f"Test categories attempted: {self.stats['tests_run']}")
        print(f"Tests passed: {self.stats['tests_passed']}")
        print(f"Tests failed: {self.stats['tests_failed']}")

        if self.stats['tests_run'] > 0:
            test_success_rate = self.stats['tests_passed'] / self.stats['tests_run'] * 100
            print(f"Test success rate: {test_success_rate:.1f}%")

        print("="*60)


def main():
    """Run Wave 17 test validation."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 17: TEST VALIDATION")
    print(f"Repository: {repo_root}")

    validator = Wave17TestValidation(repo_root)
    stats = validator.validate_status()
    validator.print_summary()

    return stats['valid_files'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
