"""
Guardian: Hygiene — Deterministic repo hygiene enforcement.

Verifies:
- No temporary artifacts (.pyc, .pyo, .tmp, .bak, .swp)
- No empty folders within allowed root territories
- No orphaned __init__.py-only folders

Outputs a schema-locked GuardianResult JSON artifact.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_hygiene \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentic_core.L0_routing.config import ROOT_WHITELIST
from agentic_core.L0_routing.types.guardian_contract_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    IGNORE_PATTERNS,
    MAX_FOLDER_DEPTH,
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    ScanBudgetExceeded,
    guard_scan_budget,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root

GUARDIAN_ID = "hygiene"
IGNORE_NAMES = frozenset({".gitkeep", ".git"})
ARTIFACT_EXTENSIONS = frozenset({".pyc", ".pyo", ".tmp", ".bak", ".swp"})


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def scan_temp_artifacts(
    repo_root: Path,
    allowed_roots: frozenset[str],
) -> list[str] | ScanBudgetExceeded:
    """
    Return repo-relative POSIX paths of temporary artifacts.

    Enforces MAX_FILES_PER_SCAN and MAX_FOLDER_DEPTH caps.
    Returns ScanBudgetExceeded sentinel on cap breach instead of raising.
    """
    hits: list[str] = []
    file_count = 0
    # Allowed roots must not be blocked by IGNORE_PATTERNS (e.g. "tests" is in
    # GLOBAL_EXCLUDED_DIRS for production-lens scans but is a valid scan root here).
    effective_ignore = IGNORE_PATTERNS - allowed_roots

    for root_name in sorted(allowed_roots):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for item in root_path.rglob("*"):
            if not item.is_file():
                continue

            # Enforce scan bounds via shared SSOT helper
            file_count += 1
            breach = guard_scan_budget(file_count)
            if breach is not None:
                return breach

            # Check depth
            depth = len(item.relative_to(repo_root).parts)
            if depth > MAX_FOLDER_DEPTH:
                continue  # Skip files beyond depth limit

            # Skip ignored patterns (excluding the allowed roots themselves)
            if any(pattern in item.parts for pattern in effective_ignore):
                continue

            if item.suffix in ARTIFACT_EXTENSIONS:
                hits.append(normalize_repo_path(item.relative_to(repo_root)))
    return sorted(hits)


def scan_empty_folders(repo_root: Path, allowed_roots: frozenset[str]) -> list[str]:
    """Return repo-relative POSIX paths of truly empty folders."""
    hits: list[str] = []
    for root_name in sorted(allowed_roots):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath_str, _dirnames, _filenames in sorted(
            __import__("os").walk(str(root_path), topdown=False),
        ):
            current = Path(dirpath_str)
            if ".git" in current.parts:
                continue
            if current.name in allowed_roots:
                continue
            try:
                children = [x for x in current.iterdir() if x.name not in IGNORE_NAMES]
                if not children:
                    hits.append(normalize_repo_path(current.relative_to(repo_root)))
            except PermissionError:
                pass
    return sorted(hits)


def scan_init_only_folders(repo_root: Path, allowed_roots: frozenset[str]) -> list[str]:
    """Return repo-relative POSIX paths of folders containing only __init__.py."""
    hits: list[str] = []
    for root_name in sorted(allowed_roots):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath_str, _dirnames, _filenames in sorted(
            __import__("os").walk(str(root_path), topdown=False),
        ):
            current = Path(dirpath_str)
            if ".git" in current.parts:
                continue
            if current.name in allowed_roots:
                continue
            try:
                children = list(current.iterdir())
                meaningful = [
                    x for x in children if x.name not in IGNORE_NAMES and not x.name.startswith(".")
                ]
                if len(meaningful) == 1 and meaningful[0].is_file() and meaningful[0].name == "__init__.py":
                    hits.append(normalize_repo_path(current.relative_to(repo_root)))
            except PermissionError:
                pass
    return sorted(hits)


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_hygiene_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """
    Execute the hygiene guardian and return a schema-locked GuardianResult.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism (omitted if None).

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    allowed_roots = frozenset(ROOT_WHITELIST)

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    # --- Check 1: Temporary artifacts ---
    try:
        scan_result = scan_temp_artifacts(repo_root, allowed_roots)
        if isinstance(scan_result, ScanBudgetExceeded):
            result.add_check(
                check_id="scan_budget_exceeded",
                status=CheckStatus.FAIL,
                details=scan_result.details,
                evidence={
                    "cap_name": scan_result.cap_name,
                    "limit": scan_result.limit,
                    "scanned": scan_result.scanned,
                },
            )
            result.remediation_hints.extend(scan_result.remediation_hints)
            result.metrics["temp_artifact_count"] = -1  # Unknown due to cap
        elif scan_result:
            result.add_check(
                check_id="temp_artifacts",
                status=CheckStatus.FAIL,
                details=f"Found {len(scan_result)} temporary artifact(s)",
                evidence={"paths": scan_result},
            )
            result.metrics["temp_artifact_count"] = len(scan_result)
        else:
            result.add_check(
                check_id="temp_artifacts",
                status=CheckStatus.PASS,
                details="No temporary artifacts found",
            )
            result.metrics["temp_artifact_count"] = 0
    # guardian: allow-silent-swallow
    except Exception as exc:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="temp_artifacts",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"temp_artifacts scan failed: {exc}")

    # --- Check 2: Empty folders ---
    try:
        empty = scan_empty_folders(repo_root, allowed_roots)
        if empty:
            result.add_check(
                check_id="empty_folders",
                status=CheckStatus.FAIL,
                details=f"Found {len(empty)} empty folder(s)",
                evidence={"paths": empty},
            )
        else:
            result.add_check(
                check_id="empty_folders",
                status=CheckStatus.PASS,
                details="No empty folders found",
            )
        result.metrics["empty_folder_count"] = len(empty)
    # guardian: allow-silent-swallow
    except Exception as exc:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="empty_folders",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"empty_folders scan failed: {exc}")

    # --- Check 3: Init-only folders ---
    try:
        init_only = scan_init_only_folders(repo_root, allowed_roots)
        if init_only:
            result.add_check(
                check_id="init_only_folders",
                status=CheckStatus.FAIL,
                details=f"Found {len(init_only)} __init__.py-only folder(s)",
                evidence={"paths": init_only},
            )
        else:
            result.add_check(
                check_id="init_only_folders",
                status=CheckStatus.PASS,
                details="No __init__.py-only folders found",
            )
        result.metrics["init_only_folder_count"] = len(init_only)
    # guardian: allow-silent-swallow
    except Exception as exc:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="init_only_folders",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"init_only_folders scan failed: {exc}")

    # --- Finalize summary ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks
    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Hygiene: {passed_checks}/{total_checks} checks passed"
    else:
        result.summary = f"Hygiene: {failed_checks}/{total_checks} checks failed"
        # Extend (not overwrite) to preserve budget cap hints
        default_hints = [
            "Remove temporary artifacts (.pyc/.pyo/.tmp/.bak/.swp)",
            "Remove or populate empty folders",
            "Add meaningful content to __init__.py-only folders or remove them",
        ]
        for hint in default_hints:
            if hint not in result.remediation_hints:
                result.remediation_hints.append(hint)

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(result, artifact_dir, "guardian_hygiene_result.json")
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Hygiene guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Hygiene Guardian")
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

    result = run_hygiene_guardian(
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
