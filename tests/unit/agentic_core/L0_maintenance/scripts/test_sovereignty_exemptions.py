"""
File: tests/test_sovereignty_exemptions.py
Path: C:\\Git\\Agentic-Workflow\tests\test_sovereignty_exemptions.py
Status: 100% Pass Required
Rationale: Verifies that the new exemption logic correctly ignores test files.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from agentic_core.L0_maintenance.scripts.pascal_sovereignty_fixer import PascalSovereigntyFixer

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))


class TestSovereigntyExemptions(unittest.TestCase):
    def setUp(self):
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_ignores_standard_test_file(self):
        """Scenario: 'test_auth.py' should be ignored even if it contains classes."""
        path = Path("test_auth.py")
        with (
            patch(
                "pathlib.Path.stat",
                side_effect=AssertionError("stat() should not be called for test_*.py"),
            ),
            patch(
                "pathlib.Path.read_text",
                side_effect=AssertionError("read_text() should not be called for test_*.py"),
            ),
            patch(
                "ast.parse",
                side_effect=AssertionError("ast.parse() should not be called for test_*.py"),
            ),
        ):
            ftype = self.fixer.classify_file(path)
            self.assertEqual(ftype, "IGNORE")

    def test_ignores_suffix_test_file(self):
        """Scenario: 'auth_test.py' should be ignored."""
        path = Path("auth_test.py")
        with (
            patch(
                "pathlib.Path.stat",
                side_effect=AssertionError("stat() should not be called for *_test.py"),
            ),
            patch(
                "pathlib.Path.read_text",
                side_effect=AssertionError("read_text() should not be called for *_test.py"),
            ),
            patch(
                "ast.parse",
                side_effect=AssertionError("ast.parse() should not be called for *_test.py"),
            ),
        ):
            ftype = self.fixer.classify_file(path)
            self.assertEqual(ftype, "IGNORE")

    def test_processes_regular_agent(self):
        """Scenario: 'AuthAgent.py' should still be processed."""
        path = Path("AuthAgent.py")
        code = "class AuthAgent(BaseAgent):\n    pass\n"

        class _Stat:
            st_size = 123

        with (
            patch("pathlib.Path.stat", return_value=_Stat()),
            patch("pathlib.Path.read_text", return_value=code),
        ):
            ftype = self.fixer.classify_file(path)
            self.assertNotEqual(ftype, "IGNORE")


if __name__ == "__main__":
    unittest.main()
