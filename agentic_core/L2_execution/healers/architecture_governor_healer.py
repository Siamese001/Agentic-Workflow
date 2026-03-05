"""
architecture_governor_healer — HEALER_REGISTRY entry for architecture_governance.

L2.3 healing subsystem: applies architectural governance fixes (naming,
import compliance, layer gravity) via ArchitectureGovernorAgent. Registered
in HEALER_REGISTRY under check_id "architecture_governance".
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus

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
