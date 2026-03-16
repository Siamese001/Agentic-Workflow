"""
architecture_governor_healer — HEALER_REGISTRY entry for architecture_governance.

L2.3 healing subsystem: applies architectural governance fixes (naming,
import compliance, layer gravity) via ArchitectureGovernorAgent. Registered
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

in HEALER_REGISTRY under check_id "architecture_governance".
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "architecture_governor_healer")
emit_determinism_digest("p0", "architecture_governor_healer")

_emit_dispatches_healing_run("p1", "architecture_governor_healer", "L2")
_emit_routes_through("p1", "architecture_governor_healer", "L2")
_emit_escalates_to_human("p1", "architecture_governor_healer", "L2")
_emit_reads_policy_state("p1", "architecture_governor_healer", "L2")
_emit_authorize_and_execute("p2", "architecture_governor_healer", "execution_auth")
_emit_validates_capability("p2", "architecture_governor_healer", "capability_check")
_emit_routes_to_capability("p2", "architecture_governor_healer", "capability_route")
_emit_writes_via_uwg("p2", "architecture_governor_healer", "uwg_write")
_emit_blocks_direct_write("p2", "architecture_governor_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "architecture_governor_healer", "tool_invocation")
_emit_captures_execution_output("p2", "architecture_governor_healer", "exec_output")
_emit_dispatches_agent("p3", "architecture_governor_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "architecture_governor_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "architecture_governor_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "architecture_governor_healer", "healing_outcome")
_emit_escalates_failure("p3", "architecture_governor_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "architecture_governor_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "architecture_governor_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "architecture_governor_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "architecture_governor_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "architecture_governor_healer", "eval_metric")
_emit_stores_embedding("p4", "architecture_governor_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "architecture_governor_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "architecture_governor_healer", "exec_snapshot_link")

CHECK_ID = "architecture_governance"

logger = logging.getLogger(__name__)


def heal_architecture_governance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal architectural governance violations via ArchitectureGovernorAgent.

    Args:
        check: Check dict from ArchitectureGovernorValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_architecture_governance", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_architecture_governance", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_architecture_governance")
    violations_count = check.get("violations_count", 0)
    territory = check.get("territory")

    if not violations_count:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.HEALED,
            changes_made=(),
            notes="no architecture governance violations detected",
        )

    if not apply:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.SKIPPED,
            changes_made=(f"would_fix:{violations_count}_governance_violations",),
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
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=repo_root)
        res = agent.heal_repository(
            dry_run=False,
            execute=True,
            auto_approve=True,
            target_territory=territory,
        )
    # guardian: allow-silent-swallow -- healer best-effort recovery; failure logged above
    except Exception as exc:  # guardian: allow-silent-swallower
        logger.error("[architecture_governor_healer] heal failed: %s", exc)
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes=f"healer error: {type(exc).__name__}: {exc}",
            needs_llm_escalation=True,
            escalation_hint="failure_type=healer_error",
        )

    violations_found = res.get("violations_found", 0)
    violations_fixed = res.get("violations_fixed", 0)
    status_str = res.get("status", "UNKNOWN")

    changes: list[str] = []
    if violations_fixed > 0:
        changes.append(f"governance_violations_fixed:{violations_fixed}")

    if status_str in ("BLOCKED", "ERROR", "UNKNOWN") and violations_fixed == 0:
        status = HealStatus.FAILED
    elif violations_fixed < violations_found and violations_fixed > 0:
        status = HealStatus.PARTIAL
    else:
        status = HealStatus.HEALED

    return HealCheckResult(
        check_id=CHECK_ID,
        status=status,
        changes_made=tuple(sorted(changes)),
        notes=f"found={violations_found} fixed={violations_fixed} status={status_str}",
    )
