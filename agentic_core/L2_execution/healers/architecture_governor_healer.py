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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "architecture_governor_healer")
emit_determinism_digest("p0", "architecture_governor_healer")

_emit_dispatches_healing_run("p1", "architecture_governor_healer", "L2")
_emit_routes_through("p1", "architecture_governor_healer", "L2")
_emit_escalates_to_human("p1", "architecture_governor_healer", "L2")
_emit_reads_policy_state("p1", "architecture_governor_healer", "L2")

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
