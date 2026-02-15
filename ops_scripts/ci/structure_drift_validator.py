#!/usr/bin/env python3
"""Structure Drift Validator - CI Gate for Layer Topology Stability

Validates that the current L* layer topology matches the golden manifest.
Prevents structural blueprint staleness by detecting drift in layer structure
and utils/ directory inventory.

USAGE:
    # Validate against golden (read-only, CI-safe)
    python -m ops_scripts.ci.structure_drift_validator

    # Update golden artifacts (requires gate)
    STRUCTURE_GOLDEN_UPDATE=1 python -m ops_scripts.ci.structure_drift_validator --update-golden

GOLDEN ARTIFACTS:
    - artifacts/structure/structure_manifest.json
    - artifacts/structure/structure_manifest.sha256

EXIT CODES:
    0 = validation passed or golden updated successfully
    1 = validation failed (drift detected) or update gate missing

DETERMINISM:
    - Manifest generation is deterministic (sorted, POSIX paths)
    - SHA-256 hash is stable across runs on same tree
    - Golden update requires BOTH --update-golden flag AND env var gate
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def validate_manifest(project_root: Path) -> int:
    """
    Validate current manifest against golden artifacts.

    Returns:
        0 if validation passes, 1 if drift detected
    """
    from agentic_core.L5_safety.validators.structure_drift_manifest import (
        canonical_manifest_bytes,
        generate_manifest,
        manifest_hash,
    )

    golden_json = project_root / "artifacts" / "structure" / "structure_manifest.json"
    golden_sha = project_root / "artifacts" / "structure" / "structure_manifest.sha256"

    # Check golden artifacts exist
    if not golden_json.exists():
        print(f"ERROR: Golden manifest not found: {golden_json}")
        print("Run with --update-golden and STRUCTURE_GOLDEN_UPDATE=1 to initialize")
        return 1

    if not golden_sha.exists():
        print(f"ERROR: Golden hash not found: {golden_sha}")
        print("Run with --update-golden and STRUCTURE_GOLDEN_UPDATE=1 to initialize")
        return 1

    # Read golden artifacts
    golden_json_bytes = golden_json.read_bytes()
    golden_hash_content = golden_sha.read_text(encoding="utf-8").strip()

    # Generate current manifest
    agentic_core = project_root / "agentic_core"
    current_manifest = generate_manifest(agentic_core)
    current_bytes = canonical_manifest_bytes(current_manifest)
    current_hash = manifest_hash(current_manifest)

    # Compare bytes (canonical form)
    if current_bytes != golden_json_bytes:
        # Count utils files for summary
        golden_manifest = __import__("json").loads(golden_json_bytes.decode("utf-8"))
        expected_count = sum(len(layer["utils_files"]) for layer in golden_manifest.values())
        actual_count = sum(len(layer["utils_files"]) for layer in current_manifest.values())

        print("FAIL: Structure drift detected")
        print(f"  expected_hash={golden_hash_content}")
        print(f"  actual_hash={current_hash}")
        print(f"  expected_utils_file_count={expected_count}")
        print(f"  actual_utils_file_count={actual_count}")
        return 1

    # Compare hash
    if current_hash != golden_hash_content:
        print("FAIL: Hash mismatch (bytes match but hash differs - should not happen)")
        print(f"  expected_hash={golden_hash_content}")
        print(f"  actual_hash={current_hash}")
        return 1

    print("PASS: Structure manifest matches golden")
    print(f"  hash={current_hash}")
    return 0


def update_golden(project_root: Path) -> int:
    """
    Update golden artifacts with current manifest.

    Requires STRUCTURE_GOLDEN_UPDATE=1 environment variable.

    Returns:
        0 if update successful, 1 if gate missing
    """
    from agentic_core.L5_safety.validators.structure_drift_manifest import (
        canonical_manifest_bytes,
        generate_manifest,
        manifest_hash,
    )

    # Check gate
    gate_value = os.environ.get("STRUCTURE_GOLDEN_UPDATE", "")
    if gate_value != "1":
        print("ERROR: Golden update requires STRUCTURE_GOLDEN_UPDATE=1 environment variable")
        print(
            "Example: STRUCTURE_GOLDEN_UPDATE=1 python -m ops_scripts.ci.structure_drift_validator --update-golden"
        )
        return 1

    # Generate current manifest
    agentic_core = project_root / "agentic_core"
    current_manifest = generate_manifest(agentic_core)
    current_bytes = canonical_manifest_bytes(current_manifest)
    current_hash = manifest_hash(current_manifest)

    # Ensure artifacts directory exists
    artifacts_dir = project_root / "artifacts" / "structure"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Write golden artifacts
    golden_json = artifacts_dir / "structure_manifest.json"
    golden_sha = artifacts_dir / "structure_manifest.sha256"

    golden_json.write_bytes(current_bytes)
    golden_sha.write_text(current_hash + "\n", encoding="utf-8")

    print("SUCCESS: Golden artifacts updated")
    print(f"  manifest={golden_json}")
    print(f"  hash_file={golden_sha}")
    print(f"  hash={current_hash}")
    return 0


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]

    # Check for --update-golden flag
    if "--update-golden" in sys.argv:
        return update_golden(project_root)
    else:
        return validate_manifest(project_root)


if __name__ == "__main__":
    sys.exit(main())
