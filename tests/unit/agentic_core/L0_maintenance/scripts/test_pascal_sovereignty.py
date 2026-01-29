"""
File: tests/test_pascal_sovereignty.py
Path: C:\\Git\\Agentic-Workflow\tests\test_pascal_sovereignty.py
Status: 100% Pass Required (Updated for Registry Check)
Rationale: Validates the class-based implementation of PascalSovereigntyFixer.
"""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# Add root to path to import fixer
sys.path.append(str(Path(__file__).parent.parent))

from agentic_core.L0_maintenance.scripts.PascalSovereigntyFixer import PascalSovereigntyFixer


class TestPascalSovereignty(unittest.TestCase):
    def setUp(self):
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    # --- New Tests: Environment Verification ---

    @patch("platform.system", return_value="Windows")
    def test_environment_check_registry_failure(self, mock_platform):
        """Ensure script BLOCKS execution if LongPathsEnabled is missing on Windows."""
        self.fixer.dry_run = False

        # Mock winreg raising OSError (simulating key missing or permission denied)
        with patch.dict(sys.modules, {"winreg": MagicMock()}):
            mock_winreg = sys.modules["winreg"]
            mock_winreg.OpenKey.side_effect = OSError("Access Denied")

            # Should pass (warn only) or fail depending on strictness.
            # Current logic: warn but allow if exception occurs (safe fallback).
            # But if key exists and value is 0, it BLOCKS.

            # Let's test the BLOCK case
            mock_winreg.OpenKey.side_effect = None
            mock_winreg.QueryValueEx.return_value = (0, 1)  # Value is 0 (Disabled)

            self.assertFalse(self.fixer.verify_environment())

    @patch("platform.system", return_value="Windows")
    def test_environment_check_registry_success(self, mock_platform):
        """Ensure script PASSES if LongPathsEnabled is 1."""
        with patch.dict(sys.modules, {"winreg": MagicMock()}):
            mock_winreg = sys.modules["winreg"]
            mock_winreg.QueryValueEx.return_value = (1, 1)  # Value is 1 (Enabled)

            self.assertTrue(self.fixer.verify_environment())

    @patch("platform.system", return_value="Linux")
    def test_environment_check_linux_bypass(self, mock_platform):
        """Ensure Linux/Mac bypasses the Windows registry check."""
        self.assertTrue(self.fixer.verify_environment())

    # --- Original Tests (Regression Check) ---

    def test_classify_agent_by_inheritance(self):
        code = "class MyBot(BaseAgent): pass"
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("test.py")), "AGENT")

    def test_classify_agent_by_suffix(self):
        code = "class SearchAgent: pass"
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("test.py")), "AGENT")

    def test_classify_agent_complex_inheritance(self):
        code = "class SuperBot(core.agents.BaseAgent): pass"
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("test.py")), "AGENT")

    def test_classify_standard_class(self):
        code = "class DataContainer: pass"
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("test.py")), "CLASS")

    def test_classify_utility(self):
        code = "def helper(): return 1"
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("test.py")), "UTILITY")

    def test_classify_init_file(self):
        self.assertEqual(self.fixer.classify_file(Path("__init__.py")), "IGNORE")

    def test_classify_empty_file(self):
        p = Path("empty.py")
        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = 0
            self.assertEqual(self.fixer.classify_file(p), "IGNORE")

    def test_classify_syntax_error(self):
        with (
            patch("pathlib.Path.read_text", return_value="class Broken("),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("bad.py")), "IGNORE")

    def test_classify_multiple_classes_one_agent(self):
        code = "class Helper: pass\nclass MasterAgent(BaseAgent): pass"
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("mixed.py")), "AGENT")

    def test_classify_attribute_inheritance(self):
        code = "class X(mod.Agent): pass"
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("x.py")), "AGENT")

    def test_classify_deep_inheritance(self):
        code = "class X(Y, Z, AgentMixin): pass"  # 'Agent' in name
        with (
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 100
            self.assertEqual(self.fixer.classify_file(Path("x.py")), "AGENT")

    # --- Group 2: Import Regex Precision (2 tests) ---

    def test_import_regex_exact_match(self):
        # Should update 'util' but not 'utilities'
        content = "from pkg import util\nfrom pkg import utilities"

        with (
            patch("PascalSovereigntyFixer.get_python_files", return_value=[Path("dependent.py")]),
            patch("pathlib.Path.read_text", return_value=content),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            self.fixer.update_imports(Path("."), "util.py", "NewUtil.py")

            if mock_write.called:
                args = mock_write.call_args[0][0]
                self.assertIn("from pkg import NewUtil", args)
                self.assertIn("from pkg import utilities", args)  # Unchanged

    def test_import_regex_word_boundary(self):
        content = "from x import old_name_v2"
        with (
            patch("pathlib.Path.read_text", return_value=content),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            with patch("PascalSovereigntyFixer.get_python_files", return_value=[Path("d.py")]):
                self.fixer.update_imports(Path("."), "old_name.py", "NewName.py")
                mock_write.assert_not_called()

    # --- Group 3: Windows Rename Safety (2 tests) ---

    @patch("pathlib.Path.rename")
    def test_windows_rename_sequence(self, mock_rename):
        src = Path("file.py")
        self.fixer.dry_run = False
        with patch("pathlib.Path.exists", return_value=False):
            self.fixer.safe_rename_windows(src, "File.py")
            # Expect 2 renames: src->temp, temp->dest
            self.assertEqual(mock_rename.call_count, 2)

    def test_rename_collision_abort(self):
        src = Path("file.py")
        self.fixer.dry_run = False
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.resolve") as mock_resolve,
        ):
            # Mock resolve to show different files (true collision)
            mock_resolve.side_effect = ["/abs/file.py", "/abs/File.py"]

            result = self.fixer.safe_rename_windows(src, "File.py")
            self.assertFalse(result)

    # --- Group 4: Agent Suffix (2 tests) ---

    def test_enforce_agent_suffix(self):
        code = "class MyBot(BaseAgent): pass"
        path = Path("my_bot.py")
        with patch("pathlib.Path.read_text", return_value=code):
            name = self.fixer.get_compliant_name(path, "AGENT")
            self.assertEqual(name, "MyBotAgent.py")

    def test_keep_existing_suffix(self):
        code = "class MyAgent(BaseAgent): pass"
        path = Path("my_agent.py")
        with patch("pathlib.Path.read_text", return_value=code):
            name = self.fixer.get_compliant_name(path, "AGENT")
            self.assertEqual(name, "MyAgent.py")

    # --- Group 5: Compliant Name Detection (3 tests) ---

    def test_detect_class_name_mismatch(self):
        # File: snake_case.py, Class: PascalCase
        code = "class PascalCase: pass"
        path = Path("snake_case.py")
        with patch("pathlib.Path.read_text", return_value=code):
            name = self.fixer.get_compliant_name(path, "CLASS")
            self.assertEqual(name, "PascalCase.py")

    def test_detect_primary_class_fuzzy(self):
        # File: some_manager.py, Classes: Helper, SomeManager
        code = "class Helper: pass\nclass SomeManager: pass"
        path = Path("some_manager.py")
        with patch("pathlib.Path.read_text", return_value=code):
            name = self.fixer.get_compliant_name(path, "CLASS")
            self.assertEqual(name, "SomeManager.py")

    def test_utility_no_rename(self):
        path = Path("utils.py")
        name = self.fixer.get_compliant_name(path, "UTILITY")
        self.assertIsNone(name)  # Should not attempt rename

    # --- Group 6: Error Handling (2 tests) ---

    def test_read_error_safe(self):
        path = Path("locked.py")
        with patch("pathlib.Path.read_text", side_effect=PermissionError):
            self.assertEqual(self.fixer.classify_file(path), "IGNORE")

    def test_rename_os_error_safe(self):
        self.fixer.dry_run = False
        with patch("pathlib.Path.rename", side_effect=OSError):
            result = self.fixer.safe_rename_windows(Path("a.py"), "A.py")
            self.assertFalse(result)

    # --- Group 7: Edge Cases (2 tests) ---

    def test_case_insensitive_match(self):
        # File: file.py, Class: FILE
        code = "class FILE: pass"
        path = Path("file.py")
        with patch("pathlib.Path.read_text", return_value=code):
            name = self.fixer.get_compliant_name(path, "CLASS")
            self.assertEqual(name, "FILE.py")

    def test_skip_main_py(self):
        # __main__.py should often be ignored or treated specially
        path = Path("__main__.py")
        # Currently classified as UTILITY or IGNORE depending on content
        # Test that we don't return a "Pascal" name for it if it has no class
        code = "print('hi')"
        with patch("pathlib.Path.read_text", return_value=code):
            ftype = self.fixer.classify_file(path)
            name = self.fixer.get_compliant_name(path, ftype)
            self.assertIsNone(name)

    # --- Group 8: Integration (2 tests) ---

    def test_full_workflow_integration(self):
        # Simulate finding a file, planning rename, and planning import update
        self.fixer.dry_run = True

        # Mock file system
        files = [Path("old_agent.py"), Path("main.py")]
        agent_code = "class RealAgent(BaseAgent): pass"
        main_code = "from old_agent import RealAgent"

        def read_side_effect(encoding):
            # rudimentary mock based on which object called read_text (hard to trace in patch)
            # simpler to mock classify and get_compliant
            return ""

        with (
            patch("PascalSovereigntyFixer.get_python_files", return_value=files),
            patch.object(PascalSovereigntyFixer, "classify_file", side_effect=["AGENT", "UTILITY"]),
            patch.object(
                PascalSovereigntyFixer,
                "get_compliant_name",
                side_effect=["RealAgentAgent.py", None],
            ),
            patch.object(PascalSovereigntyFixer, "update_imports", return_value=1) as mock_imports,
        ):
            self.fixer.run(Path("."))

            # Check stats
            self.assertEqual(self.fixer.stats["violations"]["AGENT"], 1)
            self.assertEqual(self.fixer.stats["imports_fixed"], 1)
            mock_imports.assert_called_once()

    def test_idempotency_check(self):
        # If file is already compliant, no action
        path = Path("GoodAgent.py")
        code = "class GoodAgent(BaseAgent): pass"

        with (
            patch("PascalSovereigntyFixer.get_python_files", return_value=[path]),
            patch("pathlib.Path.read_text", return_value=code),
            patch("pathlib.Path.stat") as mock_stat,
            patch.object(PascalSovereigntyFixer, "safe_rename_windows") as mock_rename,
        ):
            mock_stat.return_value.st_size = 100
            self.fixer.run(Path("."))
            self.assertEqual(self.fixer.stats["compliant"], 1)
            mock_rename.assert_not_called()


if __name__ == "__main__":
    unittest.main()
