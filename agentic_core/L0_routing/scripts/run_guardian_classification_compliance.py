"""
Guardian: Classification Compliance — Deterministic file classification enforcement.

Wraps the legacy ``FileClassificationAgent`` scan semantics as a scan-only
guardian with zero side effects.

Checks:
- naming_compliance: Compound suffix conflicts in filenames
- territory_compliance: Files residing in incorrect LCD folders per classification

Uses the SSOT classification kernel (``classify_file_standalone``) and
``FILETYPE_TO_FOLDER`` mapping for deterministic, AST-based detection.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_classification_compliance \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root

GUARDIAN_ID = "classification_compliance"

# Directories to skip during scanning (deterministic, no globs)
SKIP_PARTS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        ".pytest_cache",
        ".nox",
        "archives",
        ".sovereign_healing_backup",
        ".healing_backups",
        "artifacts",
    },
)

# LCD canonical folders where territory compliance applies
LCD_FOLDERS: frozenset[str] = frozenset(
    {
        "config",
        "types",
        "reasoning",
        "enforcement",
        "validators",
        "utils",
        "tools",
        "scripts",
    },
)

# Files that should never be classified (skip always)
SKIP_FILENAMES: frozenset[str] = frozenset(
    {
        "__init__.py",
        "__main__.py",
        "conftest.py",
        "setup.py",
    },
)


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def _collect_python_files(repo_root: Path) -> list[Path]:
    """Return sorted list of Python files in agentic_core/ and apps_*/ trees.

    Deterministic: sorted by repo-relative POSIX path, skips SKIP_PARTS.
    """
    result: list[Path] = []
    scan_roots: list[Path] = []

    for item in sorted(repo_root.iterdir(), key=lambda p: p.name):
        if not item.is_dir():
            continue
        if item.name == "agentic_core" or item.name.startswith("apps_"):
            scan_roots.append(item)

    for scan_root in scan_roots:
        for dirpath, dirnames, filenames in os.walk(scan_root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_PARTS)
            for fname in sorted(filenames):
                if fname.endswith(".py") and fname not in SKIP_FILENAMES:
                    result.append(Path(dirpath) / fname)

    return result


def scan_naming_compliance(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect compound suffix conflicts in filenames.

    Returns sorted list of violation dicts with keys:
    filename, path, conflicting_tags, pattern_matched.
    """
    from agentic_core.L0_routing.config import COMPOUND_SUFFIX_CONFLICTS

    if files is None:
        files = _collect_python_files(repo_root)

    violations: list[dict] = []
    for fpath in files:
        stem = fpath.stem
        for pattern, tag_a, tag_b, _example in COMPOUND_SUFFIX_CONFLICTS:
            if re.search(pattern, stem):
                rel = normalize_repo_path(fpath.relative_to(repo_root))
                violations.append(
                    {
                        "filename": fpath.name,
                        "path": rel,
                        "conflicting_tags": sorted([tag_a, tag_b]),
                        "pattern_matched": pattern,
                    },
                )
                break  # First match per file

    return sorted(violations, key=lambda v: v["path"])


def scan_territory_compliance(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect files residing in incorrect LCD folders per classification.

    Uses the SSOT classification kernel for AST-based file classification
    and FILETYPE_TO_FOLDER for expected folder mapping.

    Only checks files that are inside a recognized LCD folder within
    agentic_core/ layers. Files in apps_* are excluded (they have
    their own territory rules in FileClassificationAgent).

    Returns sorted list of violation dicts with keys:
    filename, path, classified_as, current_folder, expected_folder.
    """
    from agentic_core.L0_routing.config import FILETYPE_TO_FOLDER
    from agentic_core.L0_routing.seams.safety_kernel_seam import (
        load_classification_kernel,
    )

    classify_file_standalone = load_classification_kernel().classify_file_standalone

    if files is None:
        files = _collect_python_files(repo_root)

    violations: list[dict] = []
    for fpath in files:
        parts = fpath.parts

        # Only check files inside agentic_core/ layers in LCD folders
        if "agentic_core" not in parts:
            continue

        # Must be inside a recognized LCD subfolder
        parent_name = fpath.parent.name
        if parent_name not in LCD_FOLDERS:
            continue

        # Must be inside a layer (L0-L6)
        in_layer = any(p.startswith(("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_")) for p in parts)
        if not in_layer:
            continue

        # Classify using SSOT kernel
        file_type = classify_file_standalone(fpath)

        # Types that don't get folder-routed
        if file_type in ("CLASS", "STUB", "TEST", "IGNORE", "BASE_AGENT"):
            continue

        expected_folder = FILETYPE_TO_FOLDER.get(file_type)
        if expected_folder is None:
            continue

        # GLOBAL sentinels are handled separately (mixins → GLOBAL_MIXINS)
        if expected_folder in ("GLOBAL_MIXINS", "GLOBAL_INTERFACES"):
            continue

        if parent_name != expected_folder:
            rel = normalize_repo_path(fpath.relative_to(repo_root))
            violations.append(
                {
                    "filename": fpath.name,
                    "path": rel,
                    "classified_as": file_type,
                    "current_folder": parent_name,
                    "expected_folder": expected_folder,
                },
            )

    return sorted(violations, key=lambda v: v["path"])


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_classification_compliance_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """Execute classification compliance guardian.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    files = _collect_python_files(repo_root)

    # --- Check: naming_compliance ---
    try:
        naming_violations = scan_naming_compliance(repo_root, files)

        if naming_violations:
            result.add_check(
                check_id="naming_compliance",
                status=CheckStatus.FAIL,
                details=f"{len(naming_violations)} compound suffix conflict(s) detected",
                evidence={
                    "violation_count": len(naming_violations),
                    "violations": naming_violations,
                },
            )
        else:
            result.add_check(
                check_id="naming_compliance",
                status=CheckStatus.PASS,
                details="No compound suffix conflicts detected",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:
        result.add_check(
            check_id="naming_compliance",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"naming_compliance scan failed: {exc}")

    # --- Check: territory_compliance ---
    try:
        territory_violations = scan_territory_compliance(repo_root, files)

        if territory_violations:
            result.add_check(
                check_id="territory_compliance",
                status=CheckStatus.FAIL,
                details=f"{len(territory_violations)} territory violation(s) detected",
                evidence={
                    "violation_count": len(territory_violations),
                    "violations": territory_violations,
                },
            )
        else:
            result.add_check(
                check_id="territory_compliance",
                status=CheckStatus.PASS,
                details="All files in correct LCD folders",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:
        result.add_check(
            check_id="territory_compliance",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"territory_compliance scan failed: {exc}")

    # --- Finalize ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks

    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks
    result.metrics["files_scanned"] = len(files)

    if result.status == GuardianStatus.PASS.value:
        result.summary = (
            f"Classification compliance: {passed_checks}/{total_checks} checks passed "
            f"({len(files)} files scanned)"
        )
    else:
        result.summary = (
            f"Classification compliance: {failed_checks}/{total_checks} checks failed "
            f"({len(files)} files scanned)"
        )
        result.remediation_hints = [
            "Rename files with compound suffix conflicts (keep terminal suffix only)",
            "Move misplaced files to correct LCD folders per classification",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_classification_compliance_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Classification compliance guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classification Compliance Guardian",
    )
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

    result = run_classification_compliance_guardian(
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
