# TC-ZLM-06: Verify audit trail logging
# Verifies that ArchivalGatekeeper logs operations to archival_audit.jsonl

import json
import os
from pathlib import Path


def test_audit_trail_logging(tmp_path):
    """TC-ZLM-06: archival_audit.jsonl contains entry with requester_agent."""

    # Set batch mode to auto-approve
    os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"

    try:
        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper
        from agentic_core.L5_safety.validators.ssot_relocator import SSOTRelocator

        # Reset gatekeeper singleton
        ArchivalGatekeeper.reset_instance()

        # Create test structure
        (tmp_path / "agentic_core").mkdir(parents=True)
        source_file = tmp_path / "agentic_core" / "test_source.py"
        source_file.write_text("# test source")

        target_dir = tmp_path / "archives" / "test"
        target_dir.mkdir(parents=True)
        target_file = target_dir / "test_source.py"

        # Initialize relocator
        relocator = SSOTRelocator(tmp_path, dry_run=False)
        assert relocator is not None  # Verify relocator was created

        # Execute a safe move operation
        gk = ArchivalGatekeeper.get_instance(tmp_path)
        result = gk.safe_move(
            source_file, target_file, requester_agent="SSOTRelocator", reason="Test audit trail"
        )
        assert result is not None  # Verify result was returned

        # Verify audit log exists
        audit_log = tmp_path / "archives" / "archival_audit.jsonl"
        assert audit_log.exists(), f"Audit log not found at {audit_log}"

        # Read and verify audit log entry
        with open(audit_log) as f:
            lines = f.readlines()
            assert len(lines) > 0, "Audit log is empty"

            # Parse last entry
            last_entry = json.loads(lines[-1])

            # Verify required fields
            assert "requester_agent" in last_entry, "Missing requester_agent field"
            assert last_entry["requester_agent"] == "SSOTRelocator", (
                f"Expected 'SSOTRelocator', got '{last_entry['requester_agent']}'"
            )
            assert "operation" in last_entry, "Missing operation field"
            assert "timestamp" in last_entry, "Missing timestamp field"
            assert "source_path" in last_entry, "Missing source_path field"

        print("✅ TC-ZLM-06 PASSED: Audit trail logging verified")
        print(f"   Audit entry: {last_entry}")

    finally:
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_audit_trail_logging(Path(tmpdir))
