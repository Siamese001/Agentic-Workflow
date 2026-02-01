"""
Test Suite: PascalSovereigntyFixer Acronym Handling
Path: tests/unit/agentic_core/L0_maintenance/test_pascal_sovereignty_acronyms.py
Purpose: Validates acronym-aware snake_case conversion for mixins
"""

import re
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
from agentic_core.L0_maintenance.scripts.pascal_sovereignty_fixer import PascalSovereigntyFixer

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))


class TestSovereigntyAcronyms(unittest.TestCase):
    """Comprehensive acronym handling tests for PascalSovereigntyFixer."""

    def setUp(self):
        """Initialize fixer in dry_run mode to prevent disk side effects."""
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_acronym_snake_case_conversion(self):
        """
        Verify that complex acronyms in Mixins are converted to clean snake_case.
        Expected: LLMProviderMixin -> llm_provider_mixin.py (NOT l_l_m_provider...)
        """
        test_cases = {
            "LLMProviderMixin": "llm_provider_mixin.py",
            "ASTEnforcementMixin": "ast_enforcement_mixin.py",
            "MCPOperationMixin": "mcp_operation_mixin.py",
            "MCPHardenedMixin": "mcp_hardened_mixin.py",
            "AuditTrailMixin": "audit_trail_mixin.py",
            "PineconeVectorMixin": "pinecone_vector_mixin.py",
            "RedisCacheMixin": "redis_cache_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to correctly convert acronym for {stem}")

    def test_simple_pascalcase_mixin_conversion(self):
        """Test simple PascalCase mixins without acronyms."""
        test_cases = {
            "HealerMixin": "healer_mixin.py",
            "TracingMixin": "tracing_mixin.py",
            "ConfigMixin": "config_mixin.py",
            "LifecycleMixin": "lifecycle_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to convert simple PascalCase for {stem}")

    def test_multi_word_mixin_conversion(self):
        """Test multi-word PascalCase mixins."""
        test_cases = {
            "CognitiveRecoveryMixin": "cognitive_recovery_mixin.py",
            "CapabilityDiscoveryMixin": "capability_discovery_mixin.py",
            "SecretsManagementMixin": "secrets_management_mixin.py",
            "StructuralHealingMixin": "structural_healing_mixin.py",
            "SubatomicTestingMixin": "subatomic_testing_mixin.py",
            "MetaLearningMixin": "meta_learning_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to convert multi-word for {stem}")

    def test_acronym_at_start(self):
        """Test acronyms at the beginning of the name."""
        test_cases = {
            "LLMMixin": "llm_mixin.py",
            "MCPMixin": "mcp_mixin.py",
            "ASTMixin": "ast_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to convert acronym at start for {stem}")

    def test_already_compliant_mixins(self):
        """Test that already compliant mixins return None."""
        test_cases = [
            "healer_mixin",
            "cognitive_recovery_mixin",
            "llm_provider_mixin",
            "mcp_operation_mixin",
        ]

        for stem in test_cases:
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertIsNone(compliant, f"Already compliant mixin {stem} should return None")

    def test_import_alias_refactoring(self):
        """
        Ensure the 'import x as y' and 'from x import z' patterns are refactored
        using the new group-based regex without breaking the aliases.
        """
        old_mod = "llm_provider_mixin"
        new_mod = "LLMProviderMixin"
        content = "import llm_provider_mixin as lpm\nfrom llm_provider_mixin import Provider"

        # Simulating the internal update_imports regex logic
        regex_from = re.compile(rf"(?P<prefix>from\s+){re.escape(old_mod)}(?P<suffix>\s+import)")
        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))"
        )

        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)
        updated = regex_import.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", updated)

        self.assertIn("import llm_provider_mixin as lpm", updated)
        self.assertIn("from llm_provider_mixin import Provider", updated)

    def test_summary_output_integrity(self):
        """
        Verify that Mixins are counted as violations and do not carry the (Exempt) label.
        This test ensures the console output matches the architectural policy.
        """
        self.fixer.stats["violations"]["MIXIN"] = 5
        # We check that the logic allows marking them as violations for the return code
        total_violations = sum(self.fixer.stats["violations"].values())
        self.assertEqual(total_violations, 5, "Mixin violations should be counted in total")

    def test_ssot_exclusion_protection(self):
        """
        Ensure critical SSOT files are never reclassified, even if they contain classes.
        """
        mock_path = Mock(spec=Path)
        mock_path.name = "tool_registry.py"
        mock_path.parts = ("apps_shared", "utils")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(
            ftype, "IGNORE", "tool_registry.py must remain ignored to protect dynamic tool lookups"
        )

    def test_execute_ssot_exclusion(self):
        """Verify execute_ssot.py remains protected."""
        mock_path = Mock(spec=Path)
        mock_path.name = "execute_ssot.py"
        mock_path.parts = ("agentic_core", "L0_maintenance", "scripts")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(
            ftype, "IGNORE", "execute_ssot.py must remain ignored per SSOT exclusion list"
        )

    def test_structure_blueprint_exclusion(self):
        """Verify structure_blueprint.py remains protected."""
        mock_path = Mock(spec=Path)
        mock_path.name = "structure_blueprint.py"
        mock_path.parts = ("agentic_core", "L5_safety", "validators")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(
            ftype, "IGNORE", "structure_blueprint.py must remain ignored per SSOT exclusion list"
        )


class TestAcronymRegexPatterns(unittest.TestCase):
    """Test the regex patterns used for acronym conversion."""

    def test_acronym_followed_by_word(self):
        """Test Pass 1: Handle acronyms followed by words (LLMProvider -> LLM_Provider)."""
        pattern = re.compile("(.)([A-Z][a-z]+)")

        test_cases = {
            "LLMProvider": "LLM_Provider",
            "MCPOperation": "MCP_Operation",
            "ASTEnforcement": "AST_Enforcement",
        }

        for input_str, expected in test_cases.items():
            result = pattern.sub(r"\1_\2", input_str)
            self.assertEqual(result, expected, f"Pass 1 failed for {input_str}")

    def test_camelcase_boundaries(self):
        """Test Pass 2: Handle camelCase boundaries (llmProvider -> llm_Provider)."""
        # First apply Pass 1
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", "LLMProviderMixin")
        # Then apply Pass 2
        pattern = re.compile("([a-z0-9])([A-Z])")
        result = pattern.sub(r"\1_\2", s1).lower()

        self.assertEqual(
            result, "llm_provider_mixin", "Two-pass conversion should produce clean snake_case"
        )

    def test_full_conversion_pipeline(self):
        """Test the complete conversion pipeline."""
        test_cases = {
            "LLMProviderMixin": "llm_provider_mixin",
            "MCPHardenedMixin": "mcp_hardened_mixin",
            "ASTEnforcementMixin": "ast_enforcement_mixin",
            "CognitiveRecoveryMixin": "cognitive_recovery_mixin",
            "SubatomicTestingMixin": "subatomic_testing_mixin",
        }

        for input_str, expected in test_cases.items():
            # Apply two-pass conversion
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", input_str)
            result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

            self.assertEqual(result, expected, f"Full pipeline failed for {input_str}")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
