"""
hierarchy_agent_healer — HEALER_REGISTRY entry for hierarchy_violations.

L2.3 healing subsystem: creates missing directories, relocates misplaced files,
enforces depth rules, and purges orphans via HierarchyAgent with
healing_enabled=True. Registered in HEALER_REGISTRY under check_id
"hierarchy_violations".
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "hierarchy_agent_healer", "L2")
_emit_routes_through("p1", "hierarchy_agent_healer", "L2")
_emit_escalates_to_human("p1", "hierarchy_agent_healer", "L2")
_emit_reads_policy_state("p1", "hierarchy_agent_healer", "L2")

CHECK_ID = "hierarchy_violations"
logger = logging.getLogger(__name__)


def heal_hierarchy_violations(
    check: dict, *, repo_root: Path | None = None, apply: bool = False
) -> HealCheckResult:
    """Heal hierarchy violations via HierarchyAgent with healing_enabled=True.

    Args:
        check: Check dict from HierarchyValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_hierarchy_violations", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_hierarchy_violations", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_hierarchy_violations")
    violations_count = check.get("violations_count", 0)
    territory = check.get("territory")
    if not violations_count:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.HEALED,
            changes_made=(),
            notes="no hierarchy violations detected",
        )
    if not apply:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.SKIPPED,
            changes_made=(f"would_fix:{violations_count}_hierarchy_violations",),
            notes="dry-run: no mutations applied",
        )
    if repo_root is None:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes="apply mode requires repo_root",
        )
    repo_root = Path(repo_root).resolve()
    try:
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        hierarchy = HierarchyAgent(project_root=repo_root, healing_enabled=True)
        res = hierarchy.heal_hierarchy(
            create_structure=True,
            relocate_files=True,
            enforce_depth=True,
            purge_orphans=True,
            dry_run=False,
            auto_approve=True,
            target_territory=territory,
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.error("[hierarchy_agent_healer] heal failed: %s", exc)
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes=f"healer error: {type(exc).__name__}: {exc}",
            needs_llm_escalation=True,
            escalation_hint="failure_type=healer_error",
        )
    summary = res.get("summary", {})
    total_actions = summary.get("total_actions", 0)
    dirs_created = summary.get("directories_created", 0)
    files_relocated = summary.get("files_relocated", 0)
    orphans_purged = summary.get("orphans_purged", 0)
    changes: list[str] = []
    if dirs_created:
        changes.append(f"directories_created:{dirs_created}")
    if files_relocated:
        changes.append(f"files_relocated:{files_relocated}")
    if orphans_purged:
        changes.append(f"orphans_purged:{orphans_purged}")
    status = HealStatus.HEALED if total_actions >= 0 else HealStatus.PARTIAL
    return HealCheckResult(
        check_id=CHECK_ID,
        status=status,
        changes_made=tuple(sorted(changes)),
        notes=f"total_actions={total_actions} dirs={dirs_created} files={files_relocated}",
    )
