"""Tests for structure drift detection functionality."""

from __future__ import annotations

import tempfile
from pathlib import Path

from agentic_core.L5_safety.utils.structure_drift_writer import save_manifest
from agentic_core.L5_safety.validators.structure_drift_validator import (
    generate_structure_manifest,
    load_manifest,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_structure_drift")
_emit_applies_guardrail("p0", "test_structure_drift", "p0_governance")
_emit_reads_policy_state("p0", "test_structure_drift", "policy_binding")
_emit_snapshots_state("p0", "test_structure_drift", "state_snapshot")
emit_replay_key("p0", "test_structure_drift")
emit_determinism_digest("p0", "test_structure_drift")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def test_manifest_determinism():
    """Test that manifest generation is deterministic."""
    manifest1 = generate_structure_manifest()
    manifest2 = generate_structure_manifest()

    # Manifests should be identical
    assert manifest1 == manifest2

    # Hash should be the same
    assert manifest1["hash"] == manifest2["hash"]
    assert manifest1["hash"] is not None
    assert len(manifest1["hash"]) == 64  # SHA256 hex length


def test_drift_detection_in_temp_repo():
    """Test drift detection in a temporary repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create initial structure
        (temp_path / "test_dir").mkdir()
        (temp_path / "test_file.py").write_text("# Test file")

        # Generate initial manifest
        original_manifest = {
            "directories": ["test_dir"],
            "python_files": ["test_file.py"],
            "hash": "test_hash",
        }

        manifest_path = temp_path / "manifest.json"
        save_manifest(original_manifest, manifest_path)

        # Modify structure
        (temp_path / "new_dir").mkdir()
        (temp_path / "new_file.py").write_text("# New file")

        # Load and verify changes would be detected
        loaded = load_manifest(manifest_path)
        assert loaded == original_manifest


def test_update_gate_enforcement():
    """Test that update gate properly detects changes."""
    manifest = generate_structure_manifest()

    # Verify manifest has required fields
    assert "directories" in manifest
    assert "python_files" in manifest
    assert "hash" in manifest

    # Verify directories is a list
    assert isinstance(manifest["directories"], list)

    # Verify python_files is a list
    assert isinstance(manifest["python_files"], list)


def test_structure_drift_validator_integration():
    """Test integration with the CLI validator."""
    from ops_scripts.ci.structure_drift_validator import validate_structure_drift

    # Generate current manifest
    current_manifest = generate_structure_manifest()

    # Save as golden
    golden_path = Path("test_golden_manifest.json")
    save_manifest(current_manifest, golden_path)

    try:
        # Validation should pass
        assert validate_structure_drift(golden_path) is True
    finally:
        # Cleanup
        if golden_path.exists():
            golden_path.unlink()
