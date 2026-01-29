"""
File: C:/Git/Agentic-Workflow/tests/test_arch_guard.py
Context: Verifies the effectiveness of the Architectural Guard. We simulate an "attack" by creating a dummy Agent file in the utils folder and asserting that the guard script detects it and fails.
"""

import unittest
import os
import sys

# Add the project root to Python path to import scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ops_scripts.architectural_guard import scan_for_violations

# SSOT Path
COMMON_UTILS = r"C:\Git\Agentic-Workflow\apps_shared\common_utils"


class TestArchitecturalGuard(unittest.TestCase):
    def setUp(self):
        # Ensure directory exists
        os.makedirs(COMMON_UTILS, exist_ok=True)
        self.test_files = []

    def tearDown(self):
        # Cleanup any test files created
        for file_path in self.test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except PermissionError:
                    pass

    def create_dummy_violation(self, filename, content):
        path = os.path.join(COMMON_UTILS, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.test_files.append(path)
        return path

    def test_guard_detects_banned_suffix(self):
        """Test 1: Guard must flag files named *Executor.py"""
        self.create_dummy_violation("RogueExecutor.py", "x = 1")
        violations = scan_for_violations()

        found = any("RogueExecutor.py" in v and "Filename Violation" in v for v in violations)
        self.assertTrue(found, "Guard failed to catch file with 'Executor' suffix")

    def test_guard_detects_banned_inheritance(self):
        """Test 2: Guard must flag classes inheriting from Agent"""
        content = """
class SneakyBot(Agent):
    pass
"""
        self.create_dummy_violation("sneaky_util.py", content)
        violations = scan_for_violations()

        found = any("sneaky_util.py" in v and "Inheritance Violation" in v for v in violations)
        self.assertTrue(found, "Guard failed to catch class inheriting from 'Agent'")

    def test_guard_passes_clean_state(self):
        """Test 3: Guard must pass 100% when no violations exist"""
        # Ensure we didn't leave any trash from previous tests
        self.tearDown()

        violations = scan_for_violations()
        self.assertEqual(
            len(violations),
            0,
            f"Guard found violations in what should be a clean state: {violations}",
        )


if __name__ == "__main__":
    unittest.main()
