"""
Test Suite: Mixin Enforcement
Path: tests/unit/agentic_core/L0_routing/test_mixin_enforcement.py
Purpose: Validates that mixins are actively renamed to snake_case
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from tests.helpers.dev_tools_loader import load_dev_script

_emit_records_execution_trace("p0", "evidence", "test_mixin_enforcement")
_emit_applies_guardrail("p0", "test_mixin_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_mixin_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_mixin_enforcement", "state_snapshot")
emit_replay_key("p0", "test_mixin_enforcement")
emit_determinism_digest("p0", "test_mixin_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_psf = load_dev_script("pascal_sovereignty_fixer.py")
PascalSovereigntyFixer = _psf.PascalSovereigntyFixer

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))


class TestMixinEnforcement(unittest.TestCase):
    """Validates that mixins are actively renamed, not exempted."""

    def setUp(self):
        """Initialize fixer in dry_run mode."""
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_hygiene_mixin_rename(self):
        """Standard Case: Ensure HygieneMixin.py is flagged for rename to snake_case."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "HygieneMixin"
        mock_path.name = "HygieneMixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(
            new_name,
            "hygiene_mixin.py",
            "HygieneMixin.py should be renamed to hygiene_mixin.py",
        )

    def test_acronym_mixin_rename(self):
        """Acronym Case: Ensure LLMProviderMixin.py becomes llm_provider_mixin.py."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "LLMProviderMixin"
        mock_path.name = "LLMProviderMixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(
            new_name,
            "llm_provider_mixin.py",
            "LLMProviderMixin.py should be renamed to llm_provider_mixin.py",
        )

    def test_already_compliant_mixin(self):
        """Compliance Case: If already snake_case, do not rename."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "auth_mixin"
        mock_path.name = "auth_mixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertIsNone(new_name, "Already compliant auth_mixin.py should return None")

    def test_healer_mixin_compliant(self):
        """Verify healer_mixin.py is already compliant."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "healer_mixin"
        mock_path.name = "healer_mixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertIsNone(new_name, "Already compliant healer_mixin.py should return None")

    def test_cognitive_recovery_mixin_rename(self):
        """Multi-word Case: CognitiveRecoveryMixin -> cognitive_recovery_mixin.py."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "CognitiveRecoveryMixin"
        mock_path.name = "CognitiveRecoveryMixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(
            new_name,
            "cognitive_recovery_mixin.py",
            "CognitiveRecoveryMixin.py should be renamed",
        )

    def test_mcp_hardened_mixin_rename(self):
        """Acronym Case: MCPHardenedMixin -> mcp_hardened_mixin.py."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "MCPHardenedMixin"
        mock_path.name = "MCPHardenedMixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(
            new_name,
            "mcp_hardened_mixin.py",
            "MCPHardenedMixin.py should be renamed to mcp_hardened_mixin.py",
        )

    def test_ast_enforcement_mixin_rename(self):
        """Acronym Case: ASTEnforcementMixin -> ast_enforcement_mixin.py."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "ASTEnforcementMixin"
        mock_path.name = "ASTEnforcementMixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(
            new_name,
            "ast_enforcement_mixin.py",
            "ASTEnforcementMixin.py should be renamed to ast_enforcement_mixin.py",
        )

    def test_tracing_mixin_rename(self):
        """Simple Case: TracingMixin -> tracing_mixin.py."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "TracingMixin"
        mock_path.name = "TracingMixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(
            new_name,
            "tracing_mixin.py",
            "TracingMixin.py should be renamed to tracing_mixin.py",
        )

    def test_config_mixin_rename(self):
        """Simple Case: ConfigMixin -> config_mixin.py."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "ConfigMixin"
        mock_path.name = "ConfigMixin.py"

        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(new_name, "config_mixin.py", "ConfigMixin.py should be renamed to config_mixin.py")

    def test_mixin_without_suffix(self):
        """Edge Case: Mixin class without 'Mixin' in filename should get suffix added."""
        mock_path = Mock(spec=Path)
        mock_path.stem = "Auth"
        mock_path.name = "Auth.py"

        # This would be classified as CLASS, not MIXIN, but if it were MIXIN:
        new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
        self.assertEqual(new_name, "auth_mixin.py", "Auth.py as MIXIN should become auth_mixin.py")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
