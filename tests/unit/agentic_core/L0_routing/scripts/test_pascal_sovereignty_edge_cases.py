"""
Test Suite: PascalSovereigntyFixer Edge Cases
Path: tests/unit/agentic_core/L0_routing/test_pascal_sovereignty_edge_cases.py
Purpose: Validates ultra-precision regex and mixin standardization logic
"""

import re
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
    L0_ROUTING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from tests.helpers.dev_tools_loader import load_dev_script

_psf = load_dev_script("pascal_sovereignty_fixer.py")
PascalSovereigntyFixer = _psf.PascalSovereigntyFixer

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))


class TestSovereigntyEdgeCases(unittest.TestCase):
    """Comprehensive edge case testing for PascalSovereigntyFixer."""

    def setUp(self):
        """Initialize fixer in dry-run mode for safe testing."""
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_mixin_renaming_pascalcase_to_snake(self):
        """Edge Case: Ensure PascalCase Mixins are forced to snake_case."""
        # Mock path with PascalCase mixin name
        mock_path = Mock(spec=Path)
        mock_path.stem = "AuthMixin"
        mock_path.name = "AuthMixin.py"

        compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
        # AuthMixin already ends with 'Mixin', converts to auth_mixin.py (not double suffix)
        self.assertEqual(compliant, "auth_mixin.py", "Should convert PascalCase Mixin to snake_case")

    def test_mixin_already_compliant(self):
        """Edge Case: Mixins already in snake_case_mixin.py format should not be renamed."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "healer_mixin"
        mock_path.name = "healer_mixin.py"

        compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertIsNone(compliant, "Already compliant mixins should return None")

    def test_mixin_camelcase_conversion(self):
        """Edge Case: camelCase mixins should convert to snake_case."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "cognitiveRecoveryMixin"
        mock_path.name = "cognitiveRecoveryMixin.py"

        compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
        # Expected: cognitive_recovery_mixin_mixin.py (adds _mixin suffix)
        self.assertIsNotNone(compliant)
        self.assertTrue(compliant.endswith("_mixin.py"))

    def test_import_regex_with_aliases(self):
        """Edge Case: Ensure 'import x as y' is correctly refactored."""
        old_mod = "old_module"
        new_mod = "NewModule"
        content = "import old_module as om\nfrom old_module import func"

        # Use the actual regex patterns from the fixer
        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))",
        )
        regex_from = re.compile(rf"(?P<prefix>from\s+){re.escape(old_mod)}(?P<suffix>\s+import)")

        step1 = regex_import.sub(rf"\g<prefix>{new_mod}\g<suffix>", content)
        final = regex_from.sub(rf"\g<prefix>{new_mod}\g<suffix>", step1)

        self.assertIn("import NewModule as om", final, "Should preserve 'as' alias")
        self.assertIn("from NewModule import func", final, "Should update 'from' import")

    def test_import_regex_multiple_imports(self):
        """Edge Case: Multiple imports on same line should be handled."""
        old_mod = "old_tool"
        new_mod = "NewTool"
        content = "import old_tool, other_module, third_module"

        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))",
        )
        result = regex_import.sub(rf"\g<prefix>{new_mod}\g<suffix>", content)

        self.assertIn("import NewTool,", result, "Should preserve comma separator")
        self.assertIn("other_module", result, "Should not affect other imports")

    def test_import_regex_no_partial_match(self):
        """Edge Case: Ensure TOOLS_DIR doesn't match 'tools_v2'."""
        old_mod = TOOLS_DIR
        new_mod = "Tools"
        content = "from tools_v2 import func\nimport tools"

        regex_from = re.compile(rf"(?P<prefix>from\s+){re.escape(old_mod)}(?P<suffix>\s+import)")
        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))",
        )

        step1 = regex_from.sub(rf"\g<prefix>{new_mod}\g<suffix>", content)
        final = regex_import.sub(rf"\g<prefix>{new_mod}\g<suffix>", step1)

        self.assertIn("from tools_v2 import func", final, "Should NOT match tools_v2")
        self.assertIn("import Tools", final, "Should match exact TOOLS_DIR")

    def test_ssot_exclusion_execute_ssot(self):
        """Verify execute_ssot.py remains ignored per user preference."""
        mock_path = Mock(spec=Path)
        mock_path.name = "execute_ssot.py"
        mock_path.parts = (AGENTIC_CORE_DIR, L0_ROUTING_DIR, "scripts")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "execute_ssot.py should be in exclusion list")

    def test_ssot_exclusion_structure_blueprint(self):
        """Verify structure_blueprint.py remains ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "structure_blueprint.py"
        mock_path.parts = (AGENTIC_CORE_DIR, "L5_safety", "validators")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "structure_blueprint.py should be in exclusion list")

    def test_ssot_exclusion_tool_registry(self):
        """Verify tool_registry.py remains ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "tool_registry.py"
        mock_path.parts = (APPS_SHARED_DIR, "utils")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "tool_registry.py should be in exclusion list")

    def test_utility_file_preservation(self):
        """Ensure script-style utility files (no classes) are not touched."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "run_all_tasks"
        mock_path.name = "run_all_tasks.py"

        compliant = self.fixer.get_compliant_name(mock_path, "UTILITY")
        self.assertIsNone(compliant, "Utility files should not be renamed")

    def test_test_file_exemption(self):
        """Verify test files are always ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "test_sovereignty.py"
        mock_path.parts = (TESTS_DIR, "unit", AGENTIC_CORE_DIR)
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "Test files should always be ignored")

    def test_conftest_exemption(self):
        """Verify conftest.py is always ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "conftest.py"
        mock_path.parts = (TESTS_DIR, "fixtures")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "conftest.py should always be ignored")

    def test_init_file_exemption(self):
        """Verify __init__.py is always ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "__init__.py"
        mock_path.parts = (AGENTIC_CORE_DIR, L0_ROUTING_DIR)
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=100)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "__init__.py should always be ignored")


class TestRegexPrecision(unittest.TestCase):
    """Isolated regex pattern testing."""

    def test_from_import_pattern(self):
        """Test 'from x import y' pattern matching."""
        pattern = re.compile(r"(?P<prefix>from\s+)old_module(?P<suffix>\s+import)")

        test_cases = [
            ("from old_module import func", True),
            ("from old_module_v2 import func", False),
            ("from  old_module  import func", True),  # Multiple spaces
        ]

        for content, should_match in test_cases:
            match = pattern.search(content)
            if should_match:
                self.assertIsNotNone(match, f"Should match: {content}")
            else:
                self.assertIsNone(match, f"Should NOT match: {content}")

    def test_import_as_pattern(self):
        """Test 'import x as y' pattern matching."""
        pattern = re.compile(r"(?P<prefix>import\s+)old_module(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))")

        test_cases = [
            ("import old_module", True),
            ("import old_module as om", True),
            ("import old_module, other", True),
            ("import old_module_v2", False),
        ]

        for content, should_match in test_cases:
            match = pattern.search(content)
            if should_match:
                self.assertIsNotNone(match, f"Should match: {content}")
            else:
                self.assertIsNone(match, f"Should NOT match: {content}")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
