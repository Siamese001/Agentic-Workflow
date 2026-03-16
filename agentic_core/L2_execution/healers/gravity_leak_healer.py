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

emit_replay_key("p0", "gravity_leak_healer")
emit_determinism_digest("p0", "gravity_leak_healer")

_emit_dispatches_healing_run("p1", "gravity_leak_healer", "L2")
_emit_routes_through("p1", "gravity_leak_healer", "L2")
_emit_escalates_to_human("p1", "gravity_leak_healer", "L2")
_emit_reads_policy_state("p1", "gravity_leak_healer", "L2")
_emit_authorize_and_execute("p2", "gravity_leak_healer", "execution_auth")
_emit_validates_capability("p2", "gravity_leak_healer", "capability_check")
_emit_routes_to_capability("p2", "gravity_leak_healer", "capability_route")
_emit_writes_via_uwg("p2", "gravity_leak_healer", "uwg_write")
_emit_blocks_direct_write("p2", "gravity_leak_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "gravity_leak_healer", "tool_invocation")
_emit_captures_execution_output("p2", "gravity_leak_healer", "exec_output")
_emit_dispatches_agent("p3", "gravity_leak_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "gravity_leak_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "gravity_leak_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "gravity_leak_healer", "healing_outcome")
_emit_escalates_failure("p3", "gravity_leak_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "gravity_leak_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gravity_leak_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "gravity_leak_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "gravity_leak_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gravity_leak_healer", "eval_metric")
_emit_stores_embedding("p4", "gravity_leak_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "gravity_leak_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gravity_leak_healer", "exec_snapshot_link")

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
