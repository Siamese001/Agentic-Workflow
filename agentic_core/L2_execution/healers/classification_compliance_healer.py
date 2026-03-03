"""
Classification Compliance Healer — Supports dry-run and sandbox-gated apply mode.

Reads guardian evidence from naming_compliance and territory_compliance checks
and either:
- dry_run (default): produces planned actions only, no writes
- apply: performs minimal, deterministic filesystem fixes

Apply-mode mutations:
- territory_compliance: move misplaced files to their canonical folder
- naming_compliance: report-only (renames require human review)
"""

from __future__ import annotations

import shutil
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import normalize_repo_path
from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
from agentic_core.utils.ast_fuzzy_util import parse_evidence as _parse_evidence


def heal_naming_compliance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal naming_compliance violations (compound suffix conflicts).

    Naming violations require human review — automated renames risk breaking
    imports across the codebase. This healer always reports planned actions
    but never applies renames automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (renames require human review).
    """
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "naming_compliance")

    violations = evidence.get("violations", [])
    planned: list[str] = []
    for v in violations:
        path = v.get("path", "unknown")
        planned.append(f"would_review_naming:{path}")
    planned.sort()

    return HealCheckResult(
        check_id=check_id,
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned),
        rollback_info=None,
        notes="naming renames require human review; dry-run only",
    )


def heal_territory_compliance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal territory_compliance violations (misplaced files).

    Dry-run: SKIPPED with planned move actions.
    Apply: Move files to their canonical folder per FILETYPE_TO_FOLDER mapping.
    """
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "territory_compliance")

    violations = evidence.get("violations", [])

    if not apply:
        planned: list[str] = []
        for v in violations:
            path = v.get("path", "unknown")
            expected = v.get("expected_folder", "?")
            planned.append(f"would_move:{path}->folder:{expected}")
        planned.sort()
        return HealCheckResult(
            check_id=check_id,
            status=HealStatus.SKIPPED,
            changes_made=tuple(planned),
            rollback_info=None,
            notes="dry-run healer planned actions",
        )

    if repo_root is None:
        return HealCheckResult(
            check_id=check_id,
            status=HealStatus.FAILED,
            changes_made=(),
            rollback_info=None,
            notes="apply mode requires repo_root",
        )

    performed: list[str] = []
    remaining: list[str] = []

    for v in sorted(violations, key=lambda x: x.get("path", "")):
        rel_path = v.get("path", "")
        expected_folder = v.get("expected_folder", "")
        if not rel_path or not expected_folder:
            remaining.append(f"skipped_incomplete_evidence:{rel_path}")
            continue

        source = repo_root / rel_path
        if not source.is_file():
            remaining.append(f"skipped_missing_source:{rel_path}")
            continue

        # Determine target: same layer, but in the expected subfolder
        parts = Path(rel_path).parts
        if len(parts) < 3:
            remaining.append(f"skipped_shallow_path:{rel_path}")
            continue

        # Rebuild path: territory/layer/expected_folder/filename
        target_rel = Path(*parts[:2]) / expected_folder / parts[-1]
        target = repo_root / target_rel

        if target.exists():
            remaining.append(f"skipped_target_exists:{normalize_repo_path(target_rel)}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        performed.append(f"moved:{rel_path}->{normalize_repo_path(target_rel)}")

    performed.sort()
    remaining.sort()

    if remaining:
        status = HealStatus.PARTIAL
        notes = f"partial: {len(performed)} moved, {len(remaining)} remaining"
    elif performed:
        status = HealStatus.HEALED
        notes = f"healed: {len(performed)} files moved"
    else:
        status = HealStatus.HEALED
        notes = "healed: nothing to do"

    return HealCheckResult(
        check_id=check_id,
        status=status,
        changes_made=tuple(performed),
        rollback_info=None,
        notes=notes,
    )
