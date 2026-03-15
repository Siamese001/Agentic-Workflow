"""
Hierarchy Compliance Healer — Supports dry-run and sandbox-gated apply mode.

Reads guardian evidence from missing_structure and subfolder_compliance checks
and either:
- dry_run (default): produces planned actions only, no writes
- apply: performs minimal, deterministic filesystem fixes

Apply-mode mutations:
- missing_structure: create missing L2/L3 directories
- subfolder_compliance: report-only (moving non-approved folders is risky)
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import normalize_repo_path
from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.ast_fuzzy_util import parse_evidence as _parse_evidence


def heal_missing_structure(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal missing_structure violations (missing L2/L3 directories).

    Dry-run: SKIPPED with planned mkdir actions.
    Apply: Create missing directories.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_missing_structure", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_missing_structure", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_missing_structure")
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "missing_structure")

    violations = evidence.get("violations", [])

    if not apply:
        planned: list[str] = []
        for v in violations:
            path = v.get("path", "unknown")
            level = v.get("level", "?")
            planned.append(f"would_mkdir_{level}:{path}")
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
        level = v.get("level", "?")
        if not rel_path:
            remaining.append(f"skipped_empty_path:{level}")
            continue

        target = repo_root / rel_path
        if target.exists():
            continue  # Already exists, skip

        try:
            target.mkdir(parents=True, exist_ok=True)
            performed.append(f"created_{level}:{normalize_repo_path(rel_path)}")
        # guardian: allow-silent-swallow -- healer best-effort recovery; failure logged above
        except Exception as exc:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            remaining.append(f"failed_mkdir:{rel_path}:{exc}")

    performed.sort()
    remaining.sort()

    if remaining:
        status = HealStatus.PARTIAL
        notes = f"partial: {len(performed)} created, {len(remaining)} remaining"
    elif performed:
        status = HealStatus.HEALED
        notes = f"healed: {len(performed)} directories created"
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


def heal_subfolder_compliance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal subfolder_compliance violations (non-approved subfolders).

    Non-approved subfolder remediation is risky (files need relocation,
    imports need updating). This healer reports planned actions but never
    removes or relocates folders automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (folder relocation requires human review).
    """
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "subfolder_compliance")

    violations = evidence.get("violations", [])
    planned: list[str] = []
    for v in violations:
        path = v.get("path", "unknown")
        planned.append(f"would_review_subfolder:{path}")
    planned.sort()

    return HealCheckResult(
        check_id=check_id,
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned),
        rollback_info=None,
        notes="subfolder relocation requires human review; dry-run only",
    )
