"""
filesystem_ssot_healer — HEALER_REGISTRY entry for filesystem_ssot_drift.

L2.3 healing subsystem: archives forbidden root folders flagged by
FilesystemSSOTValidatorAgent. Registered in HEALER_REGISTRY under
check_id "filesystem_ssot_drift".
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus

CHECK_ID = "filesystem_ssot_drift"
_ARCHIVE_ROOT = ".healing_backups/filesystem_ssot_violations"
logger = logging.getLogger(__name__)


def heal_filesystem_ssot_drift(
    check: dict, *, repo_root: Path | None = None, apply: bool = False
) -> HealCheckResult:
    """Heal root-level SSOT drift by archiving forbidden root folders.

    Args:
        check: Check dict from FilesystemSSOTValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True archives folders.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    """
    evidence = check.get("evidence", {})
    forbidden = [f for f in evidence.get("forbidden_folders", []) if isinstance(f, str) and f]
    archived_at_root = [f for f in evidence.get("archived_files_at_root", []) if isinstance(f, str) and f]
    duplicate_folders = evidence.get("duplicate_folders", [])
    all_items = sorted(
        [f"forbidden_root_folder:{f}" for f in forbidden]
        + [f"archived_file_at_root:{f}" for f in archived_at_root]
        + [
            "duplicate_folder:{}".format(d.get("name", d) if isinstance(d, dict) else str(d))
            for d in duplicate_folders
        ]
    )
    if not all_items:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.HEALED,
            changes_made=(),
            notes="no filesystem ssot drift detected",
        )
    if not apply:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.SKIPPED,
            changes_made=tuple(f"would_fix:{item}" for item in all_items),
            notes="dry-run: no mutations applied",
        )
    if repo_root is None:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes="apply mode requires repo_root",
            needs_llm_escalation=False,
        )
    repo_root = Path(repo_root).resolve()
    from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

    gk = ArchivalGatekeeper.get_instance(repo_root)
    performed: list[str] = []
    failed: list[str] = []
    for folder in sorted(forbidden):
        src = repo_root / folder
        dst = repo_root / _ARCHIVE_ROOT / folder
        if not src.exists():
            continue
        result = gk.safe_move(src, dst, "FilesystemSSOTHealer", f"root drift: {folder}")
        if result.success:
            performed.append(f"archived_root_folder:{folder}")
        else:
            failed.append(f"failed:{folder}")
            logger.error("[filesystem_ssot_healer] archive failed: %s — %s", folder, result.error)
    if failed and (not performed):
        status = HealStatus.FAILED
    elif failed:
        status = HealStatus.PARTIAL
    else:
        status = HealStatus.HEALED
    return HealCheckResult(
        check_id=CHECK_ID,
        status=status,
        changes_made=tuple(sorted(performed)),
        notes=f"applied={len(performed)} failed={len(failed)}",
    )
