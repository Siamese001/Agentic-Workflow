"""Structure Drift Detection - Guardian Tests

Tests for deterministic layer topology manifest generation and drift detection.
Ensures structural blueprint cannot become stale without detection.

DETERMINISM:
- Manifest generation is deterministic (sorted, POSIX paths)
- SHA-256 hash is stable across runs
- No writes to repo artifacts during tests

COVERAGE:
- A) Determinism: two runs produce identical bytes and hash
- B) Drift detection: mutation causes mismatch
- C) Update gate: env var requirement enforced
"""

from __future__ import annotations

from pathlib import Path


def test_manifest_determinism():
    """Test that manifest generation is deterministic across multiple runs."""
    from agentic_core.L5_safety.validators.structure_drift_manifest import (
        canonical_manifest_bytes,
        generate_manifest,
        manifest_hash,
    )

    # Run twice on same tree
    agentic_core = Path("agentic_core")
    manifest1 = generate_manifest(agentic_core)
    manifest2 = generate_manifest(agentic_core)

    # Bytes must be identical
    bytes1 = canonical_manifest_bytes(manifest1)
    bytes2 = canonical_manifest_bytes(manifest2)
    assert bytes1 == bytes2, "Canonical bytes must be deterministic"

    # Hashes must be identical
    hash1 = manifest_hash(manifest1)
    hash2 = manifest_hash(manifest2)
    assert hash1 == hash2, "Hash must be deterministic"
    assert len(hash1) == 64, "SHA-256 hash must be 64 hex characters"


def test_drift_detection_in_temp_repo(tmp_path):
    """Test that drift is detected when layer topology changes."""
    from agentic_core.L5_safety.validators.structure_drift_manifest import (
        canonical_manifest_bytes,
        generate_manifest,
        manifest_hash,
    )

    # Create minimal fake agentic_core structure
    fake_core = tmp_path / "agentic_core"
    l0_utils = fake_core / "L0_routing" / "utils"
    l1_utils = fake_core / "L1_cognition" / "utils"
    l0_utils.mkdir(parents=True)
    l1_utils.mkdir(parents=True)

    # Create initial files
    (l0_utils / "x.py").write_text("# x\n")
    (l1_utils / "y.py").write_text("# y\n")

    # Generate baseline manifest
    baseline_manifest = generate_manifest(fake_core)
    baseline_bytes = canonical_manifest_bytes(baseline_manifest)
    baseline_hash = manifest_hash(baseline_manifest)

    # Mutate: add new file
    (l0_utils / "z.py").write_text("# z\n")

    # Regenerate manifest
    mutated_manifest = generate_manifest(fake_core)
    mutated_bytes = canonical_manifest_bytes(mutated_manifest)
    mutated_hash = manifest_hash(mutated_manifest)

    # Assert drift detected
    assert mutated_bytes != baseline_bytes, "Drift must be detected in bytes"
    assert mutated_hash != baseline_hash, "Drift must be detected in hash"

    # Verify baseline had 2 files, mutated has 3
    baseline_file_count = sum(len(layer["utils_files"]) for layer in baseline_manifest.values())
    mutated_file_count = sum(len(layer["utils_files"]) for layer in mutated_manifest.values())
    assert baseline_file_count == 2, "Baseline should have 2 files"
    assert mutated_file_count == 3, "Mutated should have 3 files"


def test_update_gate_enforcement():
    """Test that golden update requires env var gate."""
    from ops_scripts.ci.structure_drift_validator import can_update_golden

    # Gate missing
    env_missing = {}
    assert not can_update_golden(env_missing), "Gate must be missing"

    # Gate wrong value
    env_wrong = {"STRUCTURE_GOLDEN_UPDATE": "0"}
    assert not can_update_golden(env_wrong), "Gate must reject wrong value"

    # Gate present
    env_present = {"STRUCTURE_GOLDEN_UPDATE": "1"}
    assert can_update_golden(env_present), "Gate must accept correct value"


def test_structure_drift_validator_integration():
    """Guardian integration: validate current structure against golden manifest.

    This test enforces that the layer topology has not drifted from the golden
    manifest. It runs the structure drift validator in read-only mode.

    CRITICAL: This test must fail if structure drift is detected.
    """
    from ops_scripts.ci.structure_drift_validator import validate_manifest

    project_root = Path(__file__).resolve().parents[2]
    exit_code = validate_manifest(project_root)

    assert exit_code == 0, (
        "Structure drift detected! Current layer topology does not match golden manifest. "
        "Run: python -m ops_scripts.ci.structure_drift_validator for details."
    )
