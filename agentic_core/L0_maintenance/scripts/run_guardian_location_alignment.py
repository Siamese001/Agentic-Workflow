"""
Guardian: Location Alignment — Deterministic location compliance enforcement.

Reproduces the legacy ``LocationAgent`` / ``LocationValidatorAgent`` detection
semantics as a scan-only guardian with zero side effects.

Checks:
- misplaced_files: Python files violating structural location rules
  (files floating at territory root, forbidden backup/temp patterns)
- missing_directories: Required sovereign root directories that do not exist

Outputs a schema-locked GuardianResult JSON artifact.

CLI:
    python -m agentic_core.L0_maintenance.scripts.run_guardian_location_alignment \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentic_core.L0_maintenance.types.guardian_contract import (
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    ROOT_WHITELIST,
    get_validated_project_root,
)

GUARDIAN_ID = "location_alignment"

# Legacy-equivalent forbidden file patterns
# (from LocationValidatorAgent._check_naming_conventions)
FORBIDDEN_FILE_PATTERNS: tuple[str, ...] = (".bak", ".backup", ".old", ".tmp")

# Files allowed at territory root level (not considered misplaced)
ROOT_LEVEL_ALLOWED: frozenset[str] = frozenset({"__init__.py"})

# Legacy-equivalent skip patterns
# (from LocationValidatorAgent.run)
SKIP_PARTS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        "archives",
        ".venv",
        ".sovereign_healing_backup",
        "node_modules",
        ".pytest_cache",
        ".nox",
    },
)


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def scan_missing_directories(
    repo_root: Path,
    required_roots: frozenset[str] | None = None,
) -> list[str]:
    """Return sorted list of required sovereign roots that are missing or not directories.

    Reproduces ``LocationValidatorAgent.validate_sovereign_roots()``.
    """
    if required_roots is None:
        required_roots = ROOT_WHITELIST

    missing: list[str] = []
    for root_name in sorted(required_roots):
        root_path = repo_root / root_name
        if not root_path.exists():
            missing.append(root_name)
        elif not root_path.is_dir():
            missing.append(root_name)
    return sorted(missing)


def scan_misplaced_files(
    repo_root: Path,
    scan_roots: frozenset[str] | None = None,
) -> list[str]:
    """Return sorted repo-relative POSIX paths of misplaced Python files.

    Reproduces key structural checks from ``LocationValidatorAgent.run()``
    and ``validate_file_location()``:

    1. Python files sitting directly at a sovereign territory root
       (should be in a recognized subfolder; __init__.py exempt).
    2. Files with forbidden backup/temp patterns anywhere in territories.
    """
    if scan_roots is None:
        scan_roots = ROOT_WHITELIST

    hits: list[str] = []
    for root_name in sorted(scan_roots):
        root_path = repo_root / root_name
        if not root_path.exists() or not root_path.is_dir():
            continue

        # Pass 1: Python files — check structural placement
        for py_file in sorted(root_path.rglob("*.py")):
            if any(skip in py_file.parts for skip in SKIP_PARTS):
                continue

            rel_to_root = py_file.relative_to(root_path)

            # Rule 1: files floating at territory root (not in a subfolder)
            if len(rel_to_root.parts) == 1 and rel_to_root.name not in ROOT_LEVEL_ALLOWED:
                hits.append(normalize_repo_path(py_file.relative_to(repo_root)))
                continue

            # Rule 2: forbidden file patterns in .py files
            for pattern in FORBIDDEN_FILE_PATTERNS:
                if pattern in py_file.name:
                    hits.append(normalize_repo_path(py_file.relative_to(repo_root)))
                    break

        # Pass 2: forbidden backup/temp files (any extension matching patterns)
        for pattern in FORBIDDEN_FILE_PATTERNS:
            for bad_file in sorted(root_path.rglob(f"*{pattern}")):
                if not bad_file.is_file():
                    continue
                if any(skip in bad_file.parts for skip in SKIP_PARTS):
                    continue
                hits.append(normalize_repo_path(bad_file.relative_to(repo_root)))

    return sorted(set(hits))


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_location_alignment_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    required_roots: frozenset[str] | None = None,
    scan_roots: frozenset[str] | None = None,
) -> GuardianResult:
    """
    Execute the location alignment guardian and return a schema-locked GuardianResult.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism (omitted if None).
        required_roots: Override ROOT_WHITELIST for testing.
        scan_roots: Override scan scope for testing.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    # --- Check 1: misplaced_files ---
    try:
        misplaced = scan_misplaced_files(repo_root, scan_roots)
        if misplaced:
            result.add_check(
                check_id="misplaced_files",
                status=CheckStatus.FAIL,
                details=f"Found {len(misplaced)} misplaced file(s)",
                evidence={"paths": misplaced},
            )
        else:
            result.add_check(
                check_id="misplaced_files",
                status=CheckStatus.PASS,
                details="No misplaced files detected",
                evidence={"paths": []},
            )
        result.metrics["misplaced_file_count"] = len(misplaced)

    # guardian: allow-silent-swallow
    except Exception as exc:
        result.add_check(
            check_id="misplaced_files",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"misplaced_files scan failed: {exc}")

    # --- Check 2: missing_directories ---
    try:
        missing = scan_missing_directories(repo_root, required_roots)
        if missing:
            result.add_check(
                check_id="missing_directories",
                status=CheckStatus.FAIL,
                details=f"Found {len(missing)} missing sovereign root(s)",
                evidence={"directories": missing},
            )
        else:
            result.add_check(
                check_id="missing_directories",
                status=CheckStatus.PASS,
                details="All required sovereign roots present",
                evidence={"directories": []},
            )
        result.metrics["missing_directory_count"] = len(missing)

    # guardian: allow-silent-swallow
    except Exception as exc:
        result.add_check(
            check_id="missing_directories",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"missing_directories scan failed: {exc}")

    # --- Finalize summary ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks
    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Location alignment: {passed_checks}/{total_checks} checks passed"
    else:
        result.summary = f"Location alignment: {failed_checks}/{total_checks} checks failed"
        result.remediation_hints = [
            "Move misplaced files into recognized subfolders (config/, types/, reasoning/, engines/, etc.)",
            "Remove or relocate backup/temp files (.bak, .backup, .old, .tmp)",
            "Create missing sovereign root directories",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_location_alignment_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Location alignment guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Location Alignment Guardian")
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

    result = run_location_alignment_guardian(
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
