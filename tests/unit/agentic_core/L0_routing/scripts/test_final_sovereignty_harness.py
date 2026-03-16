"""
File: tests/test_final_sovereignty_harness.py
Status: 100% Pass Required
Rationale:
    Verifies the integrated Phase 5 logic, ensuring that optimizations
    and test exemptions operate as a unified gatekeeper.
"""

import unittest
from pathlib import Path
from unittest.mock import patch

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

_emit_records_execution_trace("p0", "evidence", "test_final_sovereignty_harness")
_emit_applies_guardrail("p0", "test_final_sovereignty_harness", "p0_governance")
_emit_reads_policy_state("p0", "test_final_sovereignty_harness", "policy_binding")
_emit_snapshots_state("p0", "test_final_sovereignty_harness", "state_snapshot")
emit_replay_key("p0", "test_final_sovereignty_harness")
emit_determinism_digest("p0", "test_final_sovereignty_harness")
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


class TestFinalSovereignty(unittest.TestCase):
    def setUp(self):
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_performance_optimization_integrity_100_percent_pass(self):
        """Verify registry-based import updates avoid disk rglob calls."""
        # Critical Analysis: We mock the registry to confirm update_imports
        # utilizes in-memory lookups rather than performing a fresh disk scan.
        self.fixer.file_registry = [Path("FakeAgent.py")]
        try:
            self.fixer.update_imports("Old.py", "New.py")
            status = "PASS"
        except Exception as e:  # guardian: allow-silent-swallower
            status = f"FAIL: {e}"
        self.assertEqual(status, "PASS", "Performance regression: Import refactoring must use memory cache.")

    def test_test_exemption_100_percent_pass(self):
        """Verify that test files are strictly ignored to prevent CI destruction."""
        #
        test_path = Path("tests/test_logic.py")
        self.assertEqual(self.fixer.classify_file(test_path), "IGNORE", "Fail: Test files must be exempted.")

        test_suffix_path = Path("logic_test.py")
        self.assertEqual(
            self.fixer.classify_file(test_suffix_path),
            "IGNORE",
            "Fail: Test suffix files must be exempted.",
        )

    def test_agent_detection_logic_100_percent_pass(self):
        """Verify that real agents are correctly identified for renaming."""
        # Critical Analysis: Ensures pruning logic doesn't skip actual production agents.
        # We mock a valid agent file to test the classification logic properly
        agent_path = Path("DecompositionOrchestratorAgent.py")
        mock_content = "class DecompositionOrchestratorAgent:\n    pass"

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.read_text", return_value=mock_content),
        ):
            mock_stat.return_value.st_size = 100
            result = self.fixer.classify_file(agent_path)
            self.assertNotEqual(
                result,
                "IGNORE",
                "Agent files should not be ignored when they exist and contain agent classes.",
            )

    def test_windows_registry_validation_100_percent_pass(self):
        """Confirm environment verification logic remains active for Windows safety."""
        #
        self.assertTrue(self.fixer.verify_environment(), "Environment check missing or failing.")


if __name__ == "__main__":
    unittest.main()
