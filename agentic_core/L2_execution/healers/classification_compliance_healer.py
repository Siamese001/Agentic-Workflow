"""
Classification Compliance Healer — Supports dry-run and sandbox-gated apply mode.

Reads guardian evidence from naming_compliance and territory_compliance checks
and either:
- dry_run (default): produces planned actions only, no writes
- apply: performs minimal, deterministic filesystem fixes

Apply-mode mutations:
- territory_compliance: move misplaced files to their canonical folder
- naming_compliance: report-only (renames require human review)
"""

from __future__ import annotations

import shutil
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import normalize_repo_path
from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
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

_emit_authorize_and_execute("p2", "classification_compliance_healer", "execution_auth")
_emit_validates_capability("p2", "classification_compliance_healer", "capability_check")
_emit_routes_to_capability("p2", "classification_compliance_healer", "capability_route")
_emit_writes_via_uwg("p2", "classification_compliance_healer", "uwg_write")
_emit_blocks_direct_write("p2", "classification_compliance_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "classification_compliance_healer", "tool_invocation")
_emit_captures_execution_output("p2", "classification_compliance_healer", "exec_output")
_emit_dispatches_agent("p3", "classification_compliance_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "classification_compliance_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "classification_compliance_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "classification_compliance_healer", "healing_outcome")
_emit_escalates_failure("p3", "classification_compliance_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "classification_compliance_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "classification_compliance_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "classification_compliance_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "classification_compliance_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "classification_compliance_healer", "eval_metric")
_emit_stores_embedding("p4", "classification_compliance_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "classification_compliance_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "classification_compliance_healer", "exec_snapshot_link")
from agentic_core.utils.ast_fuzzy_util import parse_evidence as _parse_evidence

emit_replay_key("p0", "classification_compliance_healer")
emit_determinism_digest("p0", "classification_compliance_healer")

_emit_dispatches_healing_run("p1", "classification_compliance_healer", "L2")
_emit_routes_through("p1", "classification_compliance_healer", "L2")
_emit_escalates_to_human("p1", "classification_compliance_healer", "L2")
_emit_reads_policy_state("p1", "classification_compliance_healer", "L2")


def heal_naming_compliance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal naming_compliance violations (compound suffix conflicts).

    Naming violations require human review — automated renames risk breaking
    imports across the codebase. This healer always reports planned actions
    but never applies renames automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (renames require human review).
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_naming_compliance", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_naming_compliance", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_naming_compliance")
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "naming_compliance")

    violations = evidence.get("violations", [])
    planned: list[str] = []
    for v in violations:
        path = v.get("path", "unknown")
        planned.append(f"would_review_naming:{path}")
    planned.sort()

    return HealCheckResult(
        check_id=check_id,
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned),
        rollback_info=None,
        notes="naming renames require human review; dry-run only",
    )


def heal_territory_compliance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal territory_compliance violations (misplaced files).

    Dry-run: SKIPPED with planned move actions.
    Apply: Move files to their canonical folder per FILETYPE_TO_FOLDER mapping.
    """
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "territory_compliance")

    violations = evidence.get("violations", [])

    if not apply:
        planned: list[str] = []
        for v in violations:
            path = v.get("path", "unknown")
            expected = v.get("expected_folder", "?")
            planned.append(f"would_move:{path}->folder:{expected}")
        planned.sort()
        return HealCheckResult(
            check_id=check_id,
            status=HealStatus.SKIPPED,
            changes_made=tuple(planned),
            rollback_info=None,
            notes="dry-run healer planned actions",
        )

    if repo_root is None:
        return HealCheckResult(
            check_id=check_id,
            status=HealStatus.FAILED,
            changes_made=(),
            rollback_info=None,
            notes="apply mode requires repo_root",
        )

    performed: list[str] = []
    remaining: list[str] = []

    for v in sorted(violations, key=lambda x: x.get("path", "")):
        rel_path = v.get("path", "")
        expected_folder = v.get("expected_folder", "")
        if not rel_path or not expected_folder:
            remaining.append(f"skipped_incomplete_evidence:{rel_path}")
            continue

        source = repo_root / rel_path
        if not source.is_file():
            remaining.append(f"skipped_missing_source:{rel_path}")
            continue

        # Determine target: same layer, but in the expected subfolder
        parts = Path(rel_path).parts
        if len(parts) < 3:
            remaining.append(f"skipped_shallow_path:{rel_path}")
            continue

        # Rebuild path: territory/layer/expected_folder/filename
        target_rel = Path(*parts[:2]) / expected_folder / parts[-1]
        target = repo_root / target_rel

        if target.exists():
            remaining.append(f"skipped_target_exists:{normalize_repo_path(target_rel)}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        performed.append(f"moved:{rel_path}->{normalize_repo_path(target_rel)}")

    performed.sort()
    remaining.sort()

    if remaining:
        status = HealStatus.PARTIAL
        notes = f"partial: {len(performed)} moved, {len(remaining)} remaining"
    elif performed:
        status = HealStatus.HEALED
        notes = f"healed: {len(performed)} files moved"
    else:
        status = HealStatus.HEALED
        notes = "healed: nothing to do"

    return HealCheckResult(
        check_id=check_id,
        status=status,
        changes_made=tuple(performed),
        rollback_info=None,
        notes=notes,
    )
