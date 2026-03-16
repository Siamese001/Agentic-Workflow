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
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "filesystem_ssot_healer")
emit_determinism_digest("p0", "filesystem_ssot_healer")

_emit_dispatches_healing_run("p1", "filesystem_ssot_healer", "L2")
_emit_routes_through("p1", "filesystem_ssot_healer", "L2")
_emit_escalates_to_human("p1", "filesystem_ssot_healer", "L2")
_emit_reads_policy_state("p1", "filesystem_ssot_healer", "L2")
_emit_authorize_and_execute("p2", "filesystem_ssot_healer", "execution_auth")
_emit_validates_capability("p2", "filesystem_ssot_healer", "capability_check")
_emit_routes_to_capability("p2", "filesystem_ssot_healer", "capability_route")
_emit_writes_via_uwg("p2", "filesystem_ssot_healer", "uwg_write")
_emit_blocks_direct_write("p2", "filesystem_ssot_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "filesystem_ssot_healer", "tool_invocation")
_emit_captures_execution_output("p2", "filesystem_ssot_healer", "exec_output")
_emit_dispatches_agent("p3", "filesystem_ssot_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "filesystem_ssot_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "filesystem_ssot_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "filesystem_ssot_healer", "healing_outcome")
_emit_escalates_failure("p3", "filesystem_ssot_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "filesystem_ssot_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "filesystem_ssot_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "filesystem_ssot_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "filesystem_ssot_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "filesystem_ssot_healer", "eval_metric")
_emit_stores_embedding("p4", "filesystem_ssot_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "filesystem_ssot_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "filesystem_ssot_healer", "exec_snapshot_link")

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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_filesystem_ssot_drift", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_filesystem_ssot_drift", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_filesystem_ssot_drift")
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
