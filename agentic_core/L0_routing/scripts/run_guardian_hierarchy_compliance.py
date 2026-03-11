"""
Guardian: Hierarchy Compliance — Deterministic structural hierarchy enforcement.

Wraps the legacy ``HierarchyAgent`` scan semantics as a scan-only guardian
with zero side effects.

Checks:
- missing_structure: L2/L3 directories missing per SOVEREIGN_TERRITORIES + CORE_SUBFOLDER_MAP
- subfolder_compliance: Non-approved subfolders within agentic_core layers

Uses the SSOT blueprint config for deterministic, filesystem-only detection.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_hierarchy_compliance \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
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

GUARDIAN_ID = "hierarchy_compliance"


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def _get_l3_subfolders(layer_def: object) -> list[str]:
    """Extract L3 subfolder names from a layer definition in SOVEREIGN_TERRITORIES.

    The nested structure is: agentic_core -> subfolders -> L2_layer -> subfolders -> {L3...}
    Works with both dict and MappingProxyType (deep-frozen).
    """
    if not hasattr(layer_def, "get"):
        return []
    nested = layer_def.get("subfolders", {})
    if hasattr(nested, "keys"):
        return list(nested.keys())
    return []


def scan_missing_structure(repo_root: Path) -> list[dict]:
    """Detect missing L2 layer and L3 sub-territory directories.

    Reproduces ``HierarchyAgent.create_missing_structure()`` detection logic
    without creating anything.

    Returns sorted list of violation dicts with keys:
    level, path, parent_layer (for L3 violations).
    """
    from agentic_core.L0_routing.config import (
        AGENTIC_CORE_DIR,
        SOVEREIGN_TERRITORIES,
    )

    violations: list[dict] = []

    # L2 layers under agentic_core
    agentic_core_def = SOVEREIGN_TERRITORIES.get("agentic_core", {})
    l2_subfolders = agentic_core_def.get("subfolders", {})
    approved_l2 = list(l2_subfolders.keys()) if hasattr(l2_subfolders, "keys") else []

    for layer_name in sorted(approved_l2):
        layer_path = repo_root / AGENTIC_CORE_DIR / layer_name
        if not layer_path.exists():
            violations.append(
                {
                    "level": "L2",
                    "path": normalize_repo_path(f"agentic_core/{layer_name}"),
                },
            )
            continue  # Can't check L3 if L2 doesn't exist

        # L3 sub-territories: extracted from nested SOVEREIGN_TERRITORIES
        layer_def = l2_subfolders.get(layer_name, {})
        expected_l3 = _get_l3_subfolders(layer_def)
        for sub_name in sorted(expected_l3):
            sub_path = layer_path / sub_name
            if not sub_path.exists():
                violations.append(
                    {
                        "level": "L3",
                        "path": normalize_repo_path(
                            f"agentic_core/{layer_name}/{sub_name}",
                        ),
                        "parent_layer": layer_name,
                    },
                )

    return sorted(violations, key=lambda v: v["path"])


def scan_subfolder_compliance(repo_root: Path) -> list[dict]:
    """Detect non-approved subfolders within agentic_core layers.

    Reproduces ``HierarchyAgent._relocate_l3_territory_files()`` detection:
    any subfolder under an L2 layer that is not in the SOVEREIGN_TERRITORIES
    blueprint is a compliance violation.

    Returns sorted list of violation dicts with keys:
    path, parent_layer, folder_name.
    """
    from agentic_core.L0_routing.config import (
        SOVEREIGN_EXCLUDED_FOLDERS,
        SOVEREIGN_TERRITORIES,
    )

    violations: list[dict] = []

    agentic_core_def = SOVEREIGN_TERRITORIES.get("agentic_core", {})
    l2_subfolders = agentic_core_def.get("subfolders", {})
    approved_l2 = list(l2_subfolders.keys()) if hasattr(l2_subfolders, "keys") else []

    agentic_core_path = repo_root / AGENTIC_CORE_DIR
    if not agentic_core_path.exists():
        return violations

    for layer_name in sorted(approved_l2):
        layer_path = agentic_core_path / layer_name
        if not layer_path.exists():
            continue

        # Extract approved L3 directly from nested SOVEREIGN_TERRITORIES
        layer_def = l2_subfolders.get(layer_name, {})
        approved_l3 = set(_get_l3_subfolders(layer_def))
        if not approved_l3:
            continue

        try:
            actual_l3 = {
                p.name
                for p in layer_path.iterdir()
                if p.is_dir()
                and not p.name.startswith(".")
                and p.name not in SOVEREIGN_EXCLUDED_FOLDERS
                and p.name != "__pycache__"
            }
        except PermissionError:
            continue

        non_approved = actual_l3 - approved_l3
        for folder_name in sorted(non_approved):
            violations.append(
                {
                    "path": normalize_repo_path(
                        f"agentic_core/{layer_name}/{folder_name}",
                    ),
                    "parent_layer": layer_name,
                    "folder_name": folder_name,
                },
            )

    return sorted(violations, key=lambda v: v["path"])


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_hierarchy_compliance_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """Execute hierarchy compliance guardian.

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

    # --- Check: missing_structure ---
    try:
        missing = scan_missing_structure(repo_root)

        if missing:
            result.add_check(
                check_id="missing_structure",
                status=CheckStatus.FAIL,
                details=f"{len(missing)} missing directory(ies) in hierarchy",
                evidence={
                    "violation_count": len(missing),
                    "violations": missing,
                },
            )
        else:
            result.add_check(
                check_id="missing_structure",
                status=CheckStatus.PASS,
                details="All L2/L3 directories present per blueprint",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="missing_structure",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"missing_structure scan failed: {exc}")

    # --- Check: subfolder_compliance ---
    try:
        non_approved = scan_subfolder_compliance(repo_root)

        if non_approved:
            result.add_check(
                check_id="subfolder_compliance",
                status=CheckStatus.FAIL,
                details=f"{len(non_approved)} non-approved subfolder(s) detected",
                evidence={
                    "violation_count": len(non_approved),
                    "violations": non_approved,
                },
            )
        else:
            result.add_check(
                check_id="subfolder_compliance",
                status=CheckStatus.PASS,
                details="All subfolders approved per CORE_SUBFOLDER_MAP",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="subfolder_compliance",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"subfolder_compliance scan failed: {exc}")

    # --- Finalize ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks

    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Hierarchy compliance: {passed_checks}/{total_checks} checks passed"
    else:
        result.summary = f"Hierarchy compliance: {failed_checks}/{total_checks} checks failed"
        result.remediation_hints = [
            "Create missing L2/L3 directories per SOVEREIGN_TERRITORIES blueprint",
            "Relocate files from non-approved subfolders to LCD-compliant folders",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_hierarchy_compliance_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Hierarchy compliance guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hierarchy Compliance Guardian",
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

    result = run_hierarchy_compliance_guardian(
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
