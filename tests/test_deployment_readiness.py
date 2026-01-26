"""
File: tests/test_deployment_readiness.py
Path: C:\Git\Agentic-Workflow\tests\test_deployment_readiness.py
Test Strategy: 100% Environment Validation
Rationale: Ensures the execution harness itself is valid before allowing the migration.
"""

import unittest
import os
from pathlib import Path

class TestDeploymentReadiness(unittest.TestCase):

    def setUp(self):
        self.root = Path(".")
        self.fixer = self.root / "pascal_sovereignty_fixer.py"
        self.batch = self.root / "execute_sovereignty.bat"
        self.tests = self.root / "tests" / "test_pascal_sovereignty.py"

    def test_critical_artifacts_exist_100_percent_pass(self):
        """Ensure all components for the deployment pipeline are present."""
        self.assertTrue(self.fixer.exists(), "Fixer script missing")
        self.assertTrue(self.batch.exists(), "Deployment batch script missing")
        self.assertTrue(self.tests.exists(), "Safety test suite missing")

    def test_batch_script_contains_safety_gate(self):
        """Verify the batch script forces a user prompt (The 'Gatekeeper')."""
        if not self.batch.exists():
            self.skipTest("Batch file not created yet")
            
        content = self.batch.read_text(encoding="utf-8")
        self.assertIn("set /p", content, "Batch script lacks user confirmation prompt")
        self.assertIn("python tests/test_pascal_sovereignty.py", content, "Batch script skips pre-flight tests")

    def test_fixer_is_executable(self):
        """Verify the fixer script has valid python syntax before batch execution."""
        with open(self.fixer, "r") as f:
            try:
                compile(f.read(), self.fixer, "exec")
            except SyntaxError as e:
                self.fail(f"Fixer script has syntax errors: {e}")

    def test_environment_safety_check(self):
        """Ensure we are not running in a sensitive production root inadvertently."""
        # Edge Case: We must be in the repo root to see 'agentic_core'
        # If 'agentic_core' is missing, the import refactoring logic will fail silently or incorrectly
        self.assertTrue(os.path.exists("agentic_core") or os.path.exists("apps_rg"), 
                       "Must run from repo root containing 'agentic_core' or 'apps_*'")

if __name__ == '__main__':
    unittest.main()
