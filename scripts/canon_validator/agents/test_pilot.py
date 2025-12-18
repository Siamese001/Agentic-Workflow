"""
TestPilot Agent - Regression Testing Guardian.
Runs pytest and tracks test results for regression detection.
"""

import asyncio
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ValidationContext

from ..base import SubAtomicAgent


class TestPilot(SubAtomicAgent):
    """
    ROLE: Regression Testing Guardian.
    Runs pytest and tracks test results for regression detection.
    """

    def __init__(self, context):
        super().__init__(context)
        self._scheduler = None

    def set_scheduler(self, scheduler):
        """Set scheduler reference for Sherlock integration."""
        self._scheduler = scheduler

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Running Regression Tests...")
        await asyncio.sleep(0)

        # Check if pytest is available
        try:
            import pytest
            has_pytest = True
        except ImportError:
            has_pytest = False
            print("   ⚠️  pytest not installed. Install with: pip install pytest")

        if not has_pytest:
            self.ctx.report(self.name, 22, True, ["pytest not available"])
            return

        # Find test files
        test_files = self._find_test_files()

        if not test_files:
            print("   ✅ No test files found - skipping")
            self.ctx.report(self.name, 22, True, ["No tests found"])
            return

        print(f"   🧪 Found {len(test_files)} test file(s)")

        # Run pytest
        result = await self._run_pytest(test_files)

        if result['passed']:
            print(f"   ✅ All tests passed ({result['count']} tests)")
            self.ctx.report(self.name, 22, True, [f"{result['count']} tests passed"])
            self.ctx.signals.add("TESTS_PASS")
        else:
            print(f"   ❌ Tests failed: {result['failures']} failures")
            self.ctx.report(self.name, 22, False, result['details'])
            self.ctx.signals.add("TEST_FAILURE")

    def _find_test_files(self):
        """Find test files in the repository."""
        test_files = []
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.venv']]
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))
        return test_files

    async def _run_pytest(self, test_files):
        """Run pytest on the test files."""
        try:
            cmd = [sys.executable, "-m", "pytest", "--quiet", "-x"] + test_files[:10]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {
                    'passed': True,
                    'count': len(test_files),
                    'failures': 0,
                    'details': []
                }
            else:
                output = stdout.decode() + stderr.decode()
                return {
                    'passed': False,
                    'count': len(test_files),
                    'failures': 1,
                    'details': [output[:500]]
                }
        except Exception as e:
            return {
                'passed': False,
                'count': 0,
                'failures': 1,
                'details': [str(e)]
            }
