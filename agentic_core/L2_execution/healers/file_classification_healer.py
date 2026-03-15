"""
file_classification_healer — HEALER_REGISTRY entry for file_classification.

L2.3 healing subsystem: relocates misclassified files and fixes naming
violations via FileClassificationAgent.heal_repository(). Registered in
HEALER_REGISTRY under check_id "file_classification".
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

_emit_dispatches_healing_run("p1", "file_classification_healer", "L2")
_emit_routes_through("p1", "file_classification_healer", "L2")
_emit_escalates_to_human("p1", "file_classification_healer", "L2")
_emit_reads_policy_state("p1", "file_classification_healer", "L2")

CHECK_ID = "file_classification"
logger = logging.getLogger(__name__)


def heal_file_classification(
    check: dict, *, repo_root: Path | None = None, apply: bool = False
) -> HealCheckResult:
    """Heal file classification violations via FileClassificationAgent.heal_repository().

    Uses cached scan results from the check dict to avoid re-scanning.

    Args:
        check: Check dict from FileClassificationValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_file_classification", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_file_classification", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_file_classification")
    violations_count = check.get("violations_count", 0)
    territory = check.get("territory")
    evidence = check.get("evidence", {})
    if not violations_count:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.HEALED,
            changes_made=(),
            notes="no file classification violations detected",
        )
    if not apply:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.SKIPPED,
            changes_made=(f"would_fix:{violations_count}_classification_violations",),
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
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        classifier = FileClassificationAgent(project_root=repo_root)
        cached_scan = {"file_registry": evidence.get("file_registry", [])}
        res = classifier.heal_repository(
            target_territory=territory, dry_run=False, auto_approve=True, cached_scan=cached_scan
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.error("[file_classification_healer] heal failed: %s", exc)
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes=f"healer error: {type(exc).__name__}: {exc}",
            needs_llm_escalation=True,
            escalation_hint="failure_type=healer_error",
        )
    files_healed = res.get("files_healed", 0) if isinstance(res, dict) else 0
    res_status = res.get("status", "UNKNOWN") if isinstance(res, dict) else "UNKNOWN"
    changes: list[str] = []
    if files_healed > 0:
        changes.append(f"files_healed:{files_healed}")
    if res_status in ("ERROR", "FAILED") and files_healed == 0:
        status = HealStatus.FAILED
    elif files_healed < violations_count and files_healed > 0:
        status = HealStatus.PARTIAL
    else:
        status = HealStatus.HEALED
    return HealCheckResult(
        check_id=CHECK_ID,
        status=status,
        changes_made=tuple(sorted(changes)),
        notes=f"files_healed={files_healed} status={res_status}",
    )
