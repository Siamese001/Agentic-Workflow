# TC-ZLM-04: Verify void violation skip in batch mode
# Verifies that LocationHealerAgent._heal_void_violation skips interactive prompts
# when batch mode is active

import os
from pathlib import Path
from unittest.mock import patch


def test_void_violation_batch_mode_skip(tmp_path):
    """TC-ZLM-04: Method returns 'SKIPPED: Batch mode active' instead of prompting for input."""

    # Set batch mode environment variables
    os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"

    try:
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        # Create test structure
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        test_file = tmp_path / "agentic_core" / "unknown_subfolder" / "test.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# test file")

        # Initialize agent
        agent = LocationHealerAgent(project_root=tmp_path)

        # Mock input to ensure it's never called
        with patch("builtins.input") as mock_input:
            # Call _heal_void_violation with a void violation scenario
            result = agent._heal_void_violation(
                file_path=test_file,
                msg="Subfolder 'unknown_subfolder' not in SSOT",
                dry_run=False,
                affected_paths=[],
                import_touched_paths=[],
            )

            # Verify input() was NEVER called
            mock_input.assert_not_called()

            # Verify result indicates batch mode skip
            assert result["applied"] is False
            assert (
                "Batch mode active" in result["action_taken"] or "SKIPPED" in result["action_taken"]
            )

        print("✅ TC-ZLM-04 PASSED: Void violation skipped in batch mode")
        print(f"   Action taken: {result['action_taken']}")

    finally:
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_void_violation_batch_mode_skip(Path(tmpdir))
