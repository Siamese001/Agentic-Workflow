"""
Unit tests for tools/capture_evidence.py - PowerShell detection.
"""

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_capture_evidence")
_emit_applies_guardrail("p0", "test_capture_evidence", "p0_governance")
_emit_reads_policy_state("p0", "test_capture_evidence", "policy_binding")
_emit_snapshots_state("p0", "test_capture_evidence", "state_snapshot")
emit_replay_key("p0", "test_capture_evidence")
emit_determinism_digest("p0", "test_capture_evidence")
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

# Import the module under test via proper package path
from tools.capture_evidence import capture_command


@pytest.mark.unit_min_deps
class TestCaptureEvidence:
    """Test suite for capture_evidence.py."""

    def test_powershell_string_abort(self, tmp_path):
        """Test that capture_command aborts if output contains 'powershell' or 'pwsh'."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return output with "powershell"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "This output contains powershell in it"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="PowerShell detected"):
                capture_command(["echo", "test"], evidence_file)

    def test_pwsh_string_abort(self, tmp_path):
        """Test that capture_command aborts if output contains 'pwsh'."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return output with "pwsh"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = "pwsh: command not found"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="PowerShell detected"):
                capture_command(["echo", "test"], evidence_file)

    def test_clean_output_no_abort(self, tmp_path):
        """Test that capture_command succeeds with clean output."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return clean output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Clean output without shell references"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            exit_code = capture_command(["echo", "test"], evidence_file)
            assert exit_code == 0

            # Verify evidence file was created
            assert evidence_file.exists()
            content = evidence_file.read_text()
            assert "Clean output without shell references" in content

    def test_case_insensitive_detection(self, tmp_path):
        """Test that PowerShell detection is case-insensitive."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return output with "PowerShell" (mixed case)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "PowerShell is detected"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="PowerShell detected"):
                capture_command(["echo", "test"], evidence_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
