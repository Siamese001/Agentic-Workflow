"""
Guardian: Manifest — Deterministic manifest.json integrity enforcement.

Verifies:
- manifest.json exists
- .manifest.lock exists
- SHA-256 checksum matches between manifest and lock file

Outputs a schema-locked GuardianResult JSON artifact.

CLI:
    python -m agentic_core.L0_maintenance.scripts.run_guardian_manifest \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from agentic_core.L0_maintenance.types.guardian_contract import (
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    get_validated_project_root,
)

GUARDIAN_ID = "manifest_integrity"
MANIFEST_FILENAME = "manifest.json"
LOCK_FILENAME = ".manifest.lock"


# ---------------------------------------------------------------------------
# Pure check functions
# ---------------------------------------------------------------------------


def _sha256(file_path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def run_manifest_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """
    Execute the manifest integrity guardian.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    manifest_path = repo_root / MANIFEST_FILENAME
    lock_path = repo_root / LOCK_FILENAME

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    # --- Check 1: manifest.json exists ---
    if manifest_path.exists():
        result.add_check(
            check_id="manifest_exists",
            status=CheckStatus.PASS,
            details=f"{MANIFEST_FILENAME} found",
        )
    else:
        result.add_check(
            check_id="manifest_exists",
            status=CheckStatus.SKIP,
            details=f"{MANIFEST_FILENAME} not found — integrity check not applicable",
        )
        result.summary = f"Manifest integrity: SKIP ({MANIFEST_FILENAME} absent)"
        result.metrics["manifest_exists"] = 0
        if write_artifacts_dir:
            artifact_dir = repo_root / write_artifacts_dir
            out = write_guardian_result(result, artifact_dir, "guardian_manifest_result.json")
            result.add_artifact(
                ArtifactType.JSON,
                normalize_repo_path(out.relative_to(repo_root)),
                "Manifest guardian result JSON",
            )
        return result

    result.metrics["manifest_exists"] = 1

    # --- Check 2: .manifest.lock exists ---
    if lock_path.exists():
        result.add_check(
            check_id="lock_exists",
            status=CheckStatus.PASS,
            details=f"{LOCK_FILENAME} found",
        )
        result.metrics["lock_exists"] = 1
    else:
        result.add_check(
            check_id="lock_exists",
            status=CheckStatus.FAIL,
            details=f"{LOCK_FILENAME} missing — cannot verify integrity",
        )
        result.metrics["lock_exists"] = 0
        result.summary = f"Manifest integrity: FAIL ({LOCK_FILENAME} missing)"
        result.remediation_hints = [
            f"Run ManifestGuardian.seal_manifest() to create {LOCK_FILENAME}",
        ]
        if write_artifacts_dir:
            artifact_dir = repo_root / write_artifacts_dir
            out = write_guardian_result(result, artifact_dir, "guardian_manifest_result.json")
            result.add_artifact(
                ArtifactType.JSON,
                normalize_repo_path(out.relative_to(repo_root)),
                "Manifest guardian result JSON",
            )
        return result

    # --- Check 3: Checksum match ---
    try:
        current_checksum = _sha256(manifest_path)
        stored_checksum = lock_path.read_text(encoding="utf-8").strip()

        if current_checksum == stored_checksum:
            result.add_check(
                check_id="checksum_match",
                status=CheckStatus.PASS,
                details="SHA-256 matches lock file",
                evidence={"sha256": current_checksum[:16] + "..."},
            )
        else:
            result.add_check(
                check_id="checksum_match",
                status=CheckStatus.FAIL,
                details="SHA-256 mismatch — manifest modified after seal",
                evidence={
                    "expected": stored_checksum[:16] + "...",
                    "actual": current_checksum[:16] + "...",
                },
            )
            result.remediation_hints = [
                "Re-seal manifest with ManifestGuardian.seal_manifest() after intentional changes",
            ]
    except Exception as exc:
        result.add_check(
            check_id="checksum_match",
            status=CheckStatus.FAIL,
            details=f"Checksum computation error: {exc}",
        )
        result.set_error(f"Checksum computation failed: {exc}")

    # --- Finalize ---
    total = len(result.checks)
    failed = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    result.metrics["total_checks"] = total
    result.metrics["failed_checks"] = failed

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Manifest integrity: {total}/{total} checks passed"
    else:
        result.summary = f"Manifest integrity: {failed}/{total} checks failed"

    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out = write_guardian_result(result, artifact_dir, "guardian_manifest_result.json")
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out.relative_to(repo_root)),
            "Manifest guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Manifest Integrity Guardian")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--timestamp", default=None)
    args = parser.parse_args()

    result = run_manifest_guardian(
        write_artifacts_dir=args.write_artifacts,
        timestamp=args.timestamp,
    )

    if args.format == "json":
        print(result.to_json())
    else:
        print(f"Guardian: {result.guardian_id} | Status: {result.status}")
        print(f"Summary: {result.summary}")
        for check in result.checks:
            print(f"  [{check.status}] {check.check_id}: {check.details}")

    if args.strict and result.status != GuardianStatus.PASS.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
