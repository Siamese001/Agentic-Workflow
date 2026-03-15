"""
Architecture Governance Healer — Dry-run only.

Reads guardian evidence from import_compliance and layer_gravity checks.
Both checks are report-only: automated fixes for import violations and
agent relocation require human review due to cascading import breakage.

Apply mode is always SKIPPED with planned actions.
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
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
from agentic_core.utils.ast_fuzzy_util import parse_evidence as _parse_evidence

_emit_dispatches_healing_run("p1", "architecture_governance_healer", "L2")
_emit_routes_through("p1", "architecture_governance_healer", "L2")
_emit_escalates_to_human("p1", "architecture_governance_healer", "L2")
_emit_reads_policy_state("p1", "architecture_governance_healer", "L2")


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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_import_compliance", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_import_compliance", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_import_compliance")
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
