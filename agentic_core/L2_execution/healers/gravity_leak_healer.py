"""
gravity_leak_healer — HEALER_REGISTRY entry for gravity_violations.

L2.3 healing subsystem: fixes layer gravity violations (upward imports,
layer inversions) via GravityLeakRepairAgent.heal_violations(). Consumes
pre-computed violations from GravityValidatorAgent, eliminating the duplicate
internal scan that previously existed in GravityLeakRepairAgent.heal_repository().

Registered in HEALER_REGISTRY under check_id "gravity_violations".
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

CHECK_ID = "gravity_violations"
logger = logging.getLogger(__name__)


def heal_gravity_violations(
    check: dict, *, repo_root: Path | None = None, apply: bool = False
) -> HealCheckResult:
    """Heal layer gravity violations via GravityLeakRepairAgent.heal_violations().

    Consumes pre-computed violations from the check dict (produced by
    GravityValidatorAgent.to_check_dict()), so no duplicate scan occurs.

    Args:
        check: Check dict from GravityValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_gravity_violations", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_gravity_violations", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_gravity_violations")
    evidence = check.get("evidence", {})
    violations = evidence.get("violations", [])
    violations_count = check.get("violations_count", len(violations))
    if not violations_count:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.HEALED,
            changes_made=(),
            notes="no gravity violations detected",
        )
    if not apply:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.SKIPPED,
            changes_made=(f"would_fix:{violations_count}_gravity_violations",),
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
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent

        agent = GravityLeakRepairAgent(project_root=repo_root)
        res = agent.heal_violations(violations, dry_run=False)
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.error("[gravity_leak_healer] heal failed: %s", exc)
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes=f"healer error: {type(exc).__name__}: {exc}",
            needs_llm_escalation=True,
            escalation_hint="failure_type=healer_error",
        )
    violations_found = res.get("violations_found", violations_count)
    violations_fixed = res.get("violations_fixed", 0)
    res_status = res.get("status", "UNKNOWN")
    changes: list[str] = []
    if violations_fixed > 0:
        changes.append(f"gravity_violations_fixed:{violations_fixed}")
    if res_status == "ERROR":
        status = HealStatus.FAILED
    elif violations_fixed < violations_found:
        status = HealStatus.PARTIAL
    else:
        status = HealStatus.HEALED
    return HealCheckResult(
        check_id=CHECK_ID,
        status=status,
        changes_made=tuple(sorted(changes)),
        notes=f"found={violations_found} fixed={violations_fixed}",
    )
