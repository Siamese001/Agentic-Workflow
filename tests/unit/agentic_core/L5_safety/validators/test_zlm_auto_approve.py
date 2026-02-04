# TC-ZLM-02: Test auto-approve bypass with HierarchyAgent
# Verifies that SOVEREIGN_AUTO_APPROVE=1 prevents input() calls

import os
from pathlib import Path
from unittest.mock import patch


def test_hierarchy_agent_auto_approve_bypass(tmp_path):
    """TC-ZLM-02: Operation completes without any input() calls when SOVEREIGN_AUTO_APPROVE=1."""

    # Set environment variable
    os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
    os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"

    try:
        from agentic_core.L5_safety.core.archival_gatekeeper_config import ArchivalGatekeeper
        from agentic_core.L5_safety.validators.hierarchy_agent import HierarchyAgent

        # Reset gatekeeper singleton
        ArchivalGatekeeper.reset_instance()

        # Create minimal test structure
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        test_file = tmp_path / "agentic_core" / "test.py"
        test_file.write_text("# test file")

        # Initialize agent
        agent = HierarchyAgent(tmp_path, healing_enabled=True)

        # Mock input to ensure it's never called
        with patch("builtins.input") as mock_input:
            # Run heal_hierarchy in execute mode
            result = agent.heal_hierarchy(execute=True, dry_run=False)

            # Verify input() was NEVER called
            mock_input.assert_not_called()

        # Verify result structure
        assert isinstance(result, dict)
        print("✅ TC-ZLM-02 PASSED: No input() calls with SOVEREIGN_AUTO_APPROVE=1")
        print(f"   Result: {result}")

    finally:
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)
        os.environ.pop("ARCHIVE_BATCH_ACCEPT", None)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_hierarchy_agent_auto_approve_bypass(Path(tmpdir))
