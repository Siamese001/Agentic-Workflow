"""
Drift Detection Healer — Plan-only (no repo mutations).

Reads guardian evidence from the drift_detection check and produces
a sorted list of planned remediation actions as strings.

No filesystem writes. No repo scanning. Pure function of input evidence.
"""

from __future__ import annotations

from agentic_core.L2_execution.types.heal_contract import (
    HealCheckResult,
    HealStatus,
)


def heal_guardian_drift_detection(check: dict) -> HealCheckResult:
    """Compute planned actions for guardian_drift_detection (dry-run only).

    Reads evidence fields if present:
    - forbidden_folders: list[str]
    - archived_files_at_root: list[str]
    - duplicate_folders: list[str]

    Returns HealCheckResult with status=SKIPPED and changes_made containing
    sorted planned-action strings. No filesystem mutations.
    """
    evidence = check.get("evidence", {})
    if not isinstance(evidence, dict):
        evidence = {}

    planned_actions: list[str] = []

    for folder in evidence.get("forbidden_folders", []):
        if isinstance(folder, str) and folder:
            planned_actions.append(f"would_remove_root_folder:{folder}")

    for path in evidence.get("archived_files_at_root", []):
        if isinstance(path, str) and path:
            planned_actions.append(f"would_remove_archived_file:{path}")

    for name in evidence.get("duplicate_folders", []):
        if isinstance(name, str) and name:
            planned_actions.append(f"would_resolve_duplicate_folder:{name}")

    planned_actions.sort()

    return HealCheckResult(
        check_id=check["check_id"],
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned_actions),
        rollback_info=None,
        notes="dry-run healer planned actions",
    )
