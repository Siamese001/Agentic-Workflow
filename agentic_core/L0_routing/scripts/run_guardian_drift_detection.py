"""
Guardian: Drift Detection — Deterministic root-level SSOT drift enforcement.

Reproduces the legacy ``FilesystemSSOTReconcilerAgent.detect_root_drift()``
detection semantics as a scan-only guardian with zero side effects.

Checks:
- Forbidden folders at project root (scripts, logs, coverage_html, observability)
- Archived/backup/old files at project root
- Duplicate folders at root that shadow SSOT locations

Outputs a schema-locked GuardianResult JSON artifact.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_drift_detection \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract import (
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root import get_validated_project_root

GUARDIAN_ID = "drift_detection"

# Legacy-equivalent constants (from FilesystemSSOTReconcilerAgent)
FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset(
    {
        "scripts",
        "logs",
        "coverage_html",
        "observability",
    },
)

ARCHIVE_PATTERNS: tuple[str, ...] = (".archived", ".backup", ".old")

SSOT_DUPLICATE_MAP: dict[str, str] = {
    "scripts": "agentic_core/L0_routing/scripts",
    "logs": "agentic_core/L0_routing/logs",
}


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def scan_forbidden_root_folders(repo_root: Path) -> list[str]:
    """Return sorted list of forbidden folder names found at project root."""
    hits: list[str] = []
    try:
        for item in repo_root.iterdir():
            if item.is_dir() and item.name in FORBIDDEN_ROOT_FOLDERS:
                hits.append(item.name)
    except PermissionError:
        pass
    return sorted(hits)


def scan_archived_files_at_root(repo_root: Path) -> list[str]:
    """Return sorted repo-relative POSIX paths of archived files at root."""
    hits: list[str] = []
    try:
        for item in repo_root.iterdir():
            if item.is_file():
                for pattern in ARCHIVE_PATTERNS:
                    if pattern in item.name:
                        hits.append(normalize_repo_path(item.relative_to(repo_root)))
                        break
    except PermissionError:
        pass
    return sorted(hits)


def scan_duplicate_ssot_folders(repo_root: Path) -> list[dict[str, str]]:
    """Return sorted list of duplicate folder dicts found at root.

    Each dict has keys: name, root_path, ssot_path (repo-relative POSIX).
    Only reported when BOTH root and SSOT paths exist simultaneously.
    """
    hits: list[dict[str, str]] = []
    for folder_name, ssot_rel in sorted(SSOT_DUPLICATE_MAP.items()):
        root_path = repo_root / folder_name
        ssot_path = repo_root / ssot_rel
        if root_path.exists() and ssot_path.exists():
            hits.append(
                {
                    "name": folder_name,
                    "root_path": normalize_repo_path(
                        root_path.relative_to(repo_root),
                    ),
                    "ssot_path": normalize_repo_path(ssot_rel),
                },
            )
    return sorted(hits, key=lambda d: d["name"])


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_drift_detection_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """
    Execute the drift detection guardian and return a schema-locked GuardianResult.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism (omitted if None).

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    # --- Check: root_drift (composite of 3 legacy sub-checks) ---
    try:
        forbidden = scan_forbidden_root_folders(repo_root)
        archived = scan_archived_files_at_root(repo_root)
        duplicates = scan_duplicate_ssot_folders(repo_root)

        drift_detected = bool(forbidden or archived or duplicates)

        evidence: dict = {
            "forbidden_folders": forbidden,
            "archived_files_at_root": archived,
            "duplicate_folders": duplicates,
        }

        if drift_detected:
            details_parts: list[str] = []
            if forbidden:
                details_parts.append(
                    f"{len(forbidden)} forbidden root folder(s)",
                )
            if archived:
                details_parts.append(
                    f"{len(archived)} archived file(s) at root",
                )
            if duplicates:
                details_parts.append(
                    f"{len(duplicates)} duplicate SSOT folder(s)",
                )

            result.add_check(
                check_id="root_drift",
                status=CheckStatus.FAIL,
                details="Root drift detected: " + "; ".join(details_parts),
                evidence=evidence,
            )
        else:
            result.add_check(
                check_id="root_drift",
                status=CheckStatus.PASS,
                details="No root-level SSOT drift detected",
                evidence=evidence,
            )

        result.metrics["forbidden_folder_count"] = len(forbidden)
        result.metrics["archived_file_count"] = len(archived)
        result.metrics["duplicate_folder_count"] = len(duplicates)
        result.metrics["drift_detected"] = drift_detected

    # guardian: allow-silent-swallow
    except Exception as exc:
        result.add_check(
            check_id="root_drift",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"root_drift scan failed: {exc}")

    # --- Finalize summary ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks
    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Drift detection: {passed_checks}/{total_checks} checks passed"
    else:
        result.summary = f"Drift detection: {failed_checks}/{total_checks} checks failed"
        result.remediation_hints = [
            "Remove forbidden root folders (scripts/, logs/, coverage_html/, observability/)",
            "Move archived/backup/old files to archives/",
            "Remove duplicate folders that shadow SSOT locations",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_drift_detection_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Drift detection guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Drift Detection Guardian")
    parser.add_argument(
        "--write-artifacts",
        default=None,
        help="Repo-relative directory to write result JSON (default: none)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Non-zero exit on FAIL/ERROR",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Injectable ISO-8601 timestamp (omitted if not provided)",
    )
    args = parser.parse_args()

    result = run_drift_detection_guardian(
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
