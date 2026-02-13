"""
Architecture Governance Healer — Dry-run only.

Reads guardian evidence from import_compliance and layer_gravity checks.
Both checks are report-only: automated fixes for import violations and
agent relocation require human review due to cascading import breakage.

Apply mode is always SKIPPED with planned actions.
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L2_execution.types.heal_contract import (
    HealCheckResult,
    HealStatus,
)


def _parse_evidence(check: dict) -> dict:
    """Extract and normalise evidence from a check dict."""
    evidence = check.get("evidence", {})
    if not isinstance(evidence, dict):
        return {}
    return evidence


def heal_import_compliance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal import_compliance violations (upward layer imports).

    Import rewiring is inherently risky — changing import statements can
    break runtime behaviour across the codebase. This healer always
    reports planned actions but never applies changes automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (import rewiring requires human review).
    """
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "import_compliance")

    violations = evidence.get("violations", [])
    planned: list[str] = []
    for v in violations:
        path = v.get("path", "unknown")
        src = v.get("source_layer", "?")
        tgt = v.get("target_layer", "?")
        planned.append(f"would_fix_import:{path}:{src}->{tgt}")
    planned.sort()

    return HealCheckResult(
        check_id=check_id,
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned),
        rollback_info=None,
        notes="import rewiring requires human review; dry-run only",
    )


def heal_layer_gravity(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal layer_gravity violations (agents in wrong layers).

    Agent relocation requires moving files AND updating all imports across
    the codebase. This healer always reports planned actions but never
    applies relocations automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (agent relocation requires human review).
    """
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "layer_gravity")

    violations = evidence.get("violations", [])
    planned: list[str] = []
    for v in violations:
        path = v.get("path", "unknown")
        actual = v.get("actual_layer", "?")
        assigned = v.get("assigned_layer", "?")
        planned.append(f"would_relocate_agent:{path}:{actual}->{assigned}")
    planned.sort()

    return HealCheckResult(
        check_id=check_id,
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned),
        rollback_info=None,
        notes="agent relocation requires human review; dry-run only",
    )
