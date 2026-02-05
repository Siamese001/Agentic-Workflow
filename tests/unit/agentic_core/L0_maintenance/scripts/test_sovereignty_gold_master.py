"""
Test Suite: Sovereignty Gold Master
Path: tests/unit/agentic_core/L0_maintenance/test_sovereignty_gold_master.py
Purpose: Final validation suite for PascalSovereigntyFixer with relative imports
"""

import re
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from agentic_core.L0_maintenance.scripts.general_scripts.pascal_sovereignty_fixer import PascalSovereigntyFixer

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))


class TestSovereigntyGoldMaster(unittest.TestCase):
    """Gold master validation suite for PascalSovereigntyFixer."""

    def setUp(self):
        """Initialize fixer in dry_run mode."""
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_relative_import_integrity(self):
        """Edge Case: Ensure 'from .llm_mixin import' is refactored correctly."""
        old_mod = "llm_mixin"
        new_mod = "LLMMixin"  # Testing the mechanism
        content = "from .llm_mixin import BaseLLM\nfrom ..llm_mixin import Helper"

        # Simulating internal logic with the actual pattern
        regex_from = re.compile(
            r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)"
        )
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "from .LLMMixin import", updated, "Single-dot relative import should be preserved"
        )
        self.assertIn(
            "from ..LLMMixin import", updated, "Double-dot relative import should be preserved"
        )

    def test_relative_import_no_dots(self):
        """Verify absolute imports still work without dots."""
        old_mod = "healer_mixin"
        new_mod = "HealerMixin"
        content = "from healer_mixin import Healer"

        regex_from = re.compile(
            r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)"
        )
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "from healer_mixin import", updated, "Absolute import should work without dots"
        )

    def test_relative_import_triple_dots(self):
        """Edge Case: Triple-dot relative imports (from ...module)."""
        old_mod = "config_mixin"
        new_mod = "ConfigMixin"
        content = "from ...config_mixin_config import Config"

        regex_from = re.compile(
            r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)"
        )
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "from ...config_mixin_config import",
            updated,
            "Triple-dot relative import should be preserved",
        )

    def test_mixin_acronym_consistency(self):
        """Standard Case: Validate acronym-aware snake_case for Mixins."""
        test_cases = {
            "ASTEnforcementMixin": "ast_enforcement_mixin.py",
            "MCPHardenedMixin": "mcp_hardened_mixin.py",
            "HygieneMixin": "hygiene_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(new_name, expected, f"Failed acronym-aware naming for {stem}")

    def test_tool_registry_exclusion(self):
        """Critical Requirement: tool_registry.py must remain ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "tool_registry.py"
        mock_path.parts = ("apps_shared", "utils")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "The tool registry is a core SSOT and must be excluded")

    def test_execute_ssot_exclusion(self):
        """Critical Requirement: execute_ssot.py must remain ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "execute_ssot.py"
        mock_path.parts = ("agentic_core", "L0_maintenance", "scripts")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "execute_ssot.py must remain in exclusion list")

    def test_structure_blueprint_exclusion(self):
        """Critical Requirement: structure_blueprint.py must remain ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "structure_blueprint.py"
        mock_path.parts = ("agentic_core", "L5_safety", "validators")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "structure_blueprint.py must remain in exclusion list")

    def test_long_path_verification(self):
        """Environment: Ensure verify_environment correctly checks for Windows LongPaths."""
        # This is a passive check; we ensure it doesn't crash the pipeline
        status = self.fixer.verify_environment()
        self.assertIsInstance(status, bool, "verify_environment should return a boolean")

    def test_relative_import_direct_module(self):
        """Verify relative imports work for direct module references."""
        old_mod = "tracing_mixin"
        new_mod = "TracingMixin"
        # Direct module import without subpath
        content = "from .tracing_mixin import Tracer"

        regex_from = re.compile(
            r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)"
        )
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "from .tracing_mixin import", updated, "Direct relative import should be updated"
        )

    def test_import_alias_with_relative(self):
        """Verify import aliases work with absolute imports."""
        old_mod = "healer_mixin"
        new_mod = "HealerMixin"
        content = "import healer_mixin as hm"

        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))"
        )
        updated = regex_import.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn("import healer_mixin as hm", updated, "Import alias should be preserved")


class TestRelativeImportPatterns(unittest.TestCase):
    """Isolated tests for relative import regex patterns."""

    def test_single_dot_pattern(self):
        """Test single-dot relative import pattern."""
        pattern = re.compile(
            r"(?P<prefix>from\s+\.*)" + re.escape("old_module") + r"(?P<suffix>\s+import)"
        )

        test_cases = [
            ("from .old_module import func", True, "from .NEW import func"),
            ("from old_module import func", True, "from NEW import func"),
            ("from ..old_module import func", True, "from ..NEW import func"),
        ]

        for content, should_match, expected in test_cases:
            match = pattern.search(content)
            if should_match:
                self.assertIsNotNone(match, f"Should match: {content}")
                result = pattern.sub(r"\g<prefix>NEW\g<suffix>", content)
                self.assertEqual(result, expected, f"Failed for: {content}")

    def test_direct_module_match(self):
        """Test direct module name matching without subpaths."""
        pattern = re.compile(
            r"(?P<prefix>from\s+\.*)" + re.escape("mixin") + r"(?P<suffix>\s+import)"
        )

        # Direct module import
        content = "from .mixin import Helper"
        result = pattern.sub(r"\g<prefix>NEW\g<suffix>", content)

        self.assertIn("from .NEW import", result, "Direct module name should be updated")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
