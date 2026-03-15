"""
Drift Detection Healer — Supports dry-run and sandbox-gated apply mode.

Reads guardian evidence from the drift_detection check and either:
- dry_run (default): produces planned actions only, no writes
- apply: performs minimal, deterministic filesystem fixes for root drift

Apply-mode mutations:
- Remove empty forbidden root folders
- Delete archived files at root
- Duplicate folders are NEVER touched (too risky)
"""

from __future__ import annotations

import shutil
from pathlib import Path

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


def heal_guardian_drift_detection(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal guardian_drift_detection with dry-run or apply mode.

    Args:
        check: Full check dict from guardian aggregate.
        repo_root: Root of the repo/sandbox to mutate (required if apply=True).
        apply: If True, perform safe filesystem mutations inside repo_root.

    Dry-run mode (apply=False):
        Returns SKIPPED with planned actions in changes_made.

    Apply mode (apply=True):
        - Empty forbidden root folders: removed.
        - Non-empty forbidden root folders: NOT removed (PARTIAL).
        - Archived files at root: deleted.
        - Duplicate folders: NEVER touched (PARTIAL if present).
        Returns HEALED if all items resolved, PARTIAL if any remain.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_guardian_drift_detection", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_guardian_drift_detection", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_guardian_drift_detection")
    evidence = _parse_evidence(check)
    check_id: str = check["check_id"]

    forbidden_folders: list[str] = [
        f for f in evidence.get("forbidden_folders", []) if isinstance(f, str) and f
    ]
    archived_files: list[str] = [
        p for p in evidence.get("archived_files_at_root", []) if isinstance(p, str) and p
    ]
    duplicate_folders: list[str] = [
        n for n in evidence.get("duplicate_folders", []) if isinstance(n, str) and n
    ]

    if not apply:
        planned: list[str] = []
        for folder in forbidden_folders:
            planned.append(f"would_remove_root_folder:{folder}")
        for path in archived_files:
            planned.append(f"would_remove_archived_file:{path}")
        for name in duplicate_folders:
            planned.append(f"would_resolve_duplicate_folder:{name}")
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

    for folder in sorted(forbidden_folders):
        target = repo_root / folder
        if target.is_dir():
            if not any(target.iterdir()):
                shutil.rmtree(target)
                performed.append(f"removed_root_folder:{folder}")
            else:
                remaining.append(f"skipped_non_empty_folder:{folder}")

    for path in sorted(archived_files):
        target = repo_root / path
        if target.is_file():
            target.unlink()
            performed.append(f"removed_archived_file:{path}")

    for name in sorted(duplicate_folders):
        remaining.append(f"skipped_duplicate_folder:{name}")

    performed.sort()
    remaining.sort()

    if remaining:
        status = HealStatus.PARTIAL
        notes = f"partial: {len(performed)} applied, {len(remaining)} remaining"
    elif performed:
        status = HealStatus.HEALED
        notes = f"healed: {len(performed)} actions applied"
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
