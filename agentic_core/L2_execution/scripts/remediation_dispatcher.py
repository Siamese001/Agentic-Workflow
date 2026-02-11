"""
Remediation Dispatcher — Minimal L2 PhaseSpec interpreter (skeleton).

Loads an aggregate guardian result, interprets the LEGACY_MIRROR_PLAN,
and produces a CombinedHealResult artifact with all checks SKIPPED
(no healers registered yet).

Side-effect free: only writes the HealResult JSON to the output directory.

CLI:
    python -m agentic_core.L2_execution.scripts.remediation_dispatcher \\
        --guardian-result combined_guardian_result.json \\
        --write-artifacts output_dir \\
        --created-utc 2026-01-01T00:00:00Z
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.types.heal_contract import (
    CombinedHealResult,
    HealCheckResult,
    HealStatus,
)
from agentic_core.L2_execution.types.l2_phase_spec import (
    LEGACY_MIRROR_PLAN,
    L2ExecutionPlan,
)
from agentic_core.L3_orchestration.types.approval_contract import (
    ApprovalBundle,
    ApprovalDecision,
    ApprovalRecord,
)

TOOL_ID = "remediation_dispatcher"
OUTPUT_FILENAME = "combined_heal_result.json"

# ---------------------------------------------------------------------------
# Canonical phase names and phase-to-check_id mapping
# ---------------------------------------------------------------------------

EXPECTED_PHASE_NAMES: tuple[str, ...] = (
    "pre_audit",
    "discovery",
    "reconciliation",
    "alignment",
    "arch_validation",
    "healing",
    "certification",
)

# Explicit mapping: phase_name -> tuple of check_id prefixes.
# A guardian check_id is "mapped" to a phase if it startswith any prefix.
# Empty tuple = no guardians mapped yet (structure-only phase).
PHASE_CHECK_ID_PREFIXES: dict[str, tuple[str, ...]] = {
    "pre_audit": ("guardian_drift_detection",),
    "discovery": ("guardian_location_alignment",),
    "reconciliation": (),
    "alignment": (),
    "arch_validation": (),
    "healing": (),
    "certification": (),
}

NOTE_MAPPED = "no healer registered"
NOTE_UNMAPPED = "unmapped to phase; no healer registered"


# ---------------------------------------------------------------------------
# PhaseSpec validation
# ---------------------------------------------------------------------------


def validate_phase_names(plan: L2ExecutionPlan) -> None:
    """Validate that plan phase names exactly match the expected canonical list.

    Raises ValueError if names differ in count, order, or content.
    """
    actual = tuple(p.name for p in plan.phases)
    if actual != EXPECTED_PHASE_NAMES:
        raise ValueError(
            f"PhaseSpec name integrity violation: expected {list(EXPECTED_PHASE_NAMES)}, got {list(actual)}",
        )


def classify_check_ids(
    check_ids: list[str],
    phase_prefixes: dict[str, tuple[str, ...]] | None = None,
) -> tuple[set[str], set[str]]:
    """Classify check_ids into mapped and unmapped sets.

    A check_id is "mapped" if it startswith any prefix in any phase mapping.

    Returns (mapped, unmapped) sets.
    """
    if phase_prefixes is None:
        phase_prefixes = PHASE_CHECK_ID_PREFIXES

    all_prefixes: list[str] = []
    for prefixes in phase_prefixes.values():
        all_prefixes.extend(prefixes)

    mapped: set[str] = set()
    unmapped: set[str] = set()
    for cid in check_ids:
        if any(cid.startswith(prefix) for prefix in all_prefixes):
            mapped.add(cid)
        else:
            unmapped.add(cid)
    return mapped, unmapped


# ---------------------------------------------------------------------------
# Guardian aggregate parsing
# ---------------------------------------------------------------------------


def extract_check_ids(guardian_aggregate: dict[str, Any]) -> list[str]:
    """Extract check_ids from a guardian aggregate result deterministically.

    Supports the canonical aggregate shape produced by run_all_guardians:
    - top-level "checks" list of dicts, each with "check_id"

    Returns sorted, deduplicated list of check_ids.
    Raises ValueError for unrecognised shapes.
    """
    checks = guardian_aggregate.get("checks")
    if isinstance(checks, list):
        ids: list[str] = []
        for item in checks:
            if isinstance(item, dict) and "check_id" in item:
                ids.append(item["check_id"])
            else:
                raise ValueError(
                    f"Unexpected check item shape: {type(item).__name__}, expected dict with 'check_id'",
                )
        return sorted(set(ids))

    raise ValueError(
        "Unrecognised guardian aggregate shape: expected top-level 'checks' list of dicts with 'check_id'",
    )


# ---------------------------------------------------------------------------
# Approval bundle parsing
# ---------------------------------------------------------------------------


def load_approval_bundle(path: Path) -> ApprovalBundle:
    """Load and return an ApprovalBundle from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    records_raw = data.get("records", [])
    records: list[ApprovalRecord] = []
    for r in records_raw:
        records.append(
            ApprovalRecord(
                phase_name=r["phase_name"],
                guardian_id=r.get("guardian_id"),
                check_ids=tuple(r.get("check_ids", ())),
                decision=ApprovalDecision(r["decision"]),
                approver=r["approver"],
                rationale=r.get("rationale"),
                token=r["token"],
                created_utc=r["created_utc"],
            ),
        )
    return ApprovalBundle(records=tuple(records))


# ---------------------------------------------------------------------------
# Core dispatcher logic
# ---------------------------------------------------------------------------


def run_dispatcher(
    guardian_result_path: Path,
    write_artifacts_dir: Path,
    created_utc: str,
    plan_name: str = "LEGACY_MIRROR_PLAN",
    approval_bundle_path: Path | None = None,
) -> CombinedHealResult:
    """Execute the dispatcher interpreting LEGACY_MIRROR_PLAN PhaseSpec.

    1. Validates PhaseSpec name integrity.
    2. Loads the guardian aggregate and extracts check_ids.
    3. Classifies check_ids as mapped or unmapped via phase prefix mapping.
    4. Iterates phases in order (approval gating + rerun hooks as no-ops).
    5. Produces a CombinedHealResult with all checks SKIPPED.
    6. Validates and writes the result to the output directory.

    Returns the CombinedHealResult.
    """
    # 1. Validate PhaseSpec integrity
    validate_phase_names(LEGACY_MIRROR_PLAN)

    # 2. Load guardian aggregate
    guardian_data = json.loads(guardian_result_path.read_text(encoding="utf-8"))
    check_ids = extract_check_ids(guardian_data)

    # 3. Classify check_ids
    mapped_ids, unmapped_ids = classify_check_ids(check_ids)

    # 4. Iterate phases in PhaseSpec order
    heal_checks: list[HealCheckResult] = []
    for phase in LEGACY_MIRROR_PLAN.phases:
        # --- Approval gating hook (no-op: no phase has approval_required=True) ---
        if phase.approval_required:
            pass  # Future: block until approval token present

        # Select check_ids for this phase
        prefixes = PHASE_CHECK_ID_PREFIXES.get(phase.name, ())
        phase_cids = sorted(cid for cid in check_ids if any(cid.startswith(p) for p in prefixes))

        for cid in phase_cids:
            heal_checks.append(
                HealCheckResult(
                    check_id=cid,
                    status=HealStatus.SKIPPED,
                    changes_made=(),
                    rollback_info=None,
                    notes=NOTE_MAPPED,
                ),
            )

        # --- Rerun guardians hook (no-op: no phase has rerun_guardians) ---
        if phase.rerun_guardians:
            pass  # Future: re-run specified guardians after healing

    # 5. Add unmapped check_ids (coverage preservation)
    for cid in sorted(unmapped_ids):
        heal_checks.append(
            HealCheckResult(
                check_id=cid,
                status=HealStatus.SKIPPED,
                changes_made=(),
                rollback_info=None,
                notes=NOTE_UNMAPPED,
            ),
        )

    # 6. Load optional approval bundle
    approved_tokens: list[str] = []
    if approval_bundle_path is not None:
        bundle = load_approval_bundle(approval_bundle_path)
        for record in bundle.records:
            if record.decision == ApprovalDecision.APPROVED:
                approved_tokens.append(record.token)
    approved_tokens = sorted(set(approved_tokens))

    # 7. Build CombinedHealResult
    result = CombinedHealResult(
        tool_id=TOOL_ID,
        plan_name=plan_name,
        results=tuple(heal_checks),
        approved_by=tuple(approved_tokens),
        created_utc=created_utc,
    )

    # 8. Validate before writing
    errors = result.validate()
    if errors:
        raise ValueError(f"CombinedHealResult validation failed: {errors}")

    # 9. Write artifact
    write_artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = write_artifacts_dir / OUTPUT_FILENAME
    out_path.write_text(result.to_json(), encoding="utf-8")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="L2 Remediation Dispatcher (skeleton)")
    parser.add_argument(
        "--guardian-result",
        required=True,
        help="Path to combined_guardian_result.json",
    )
    parser.add_argument(
        "--approval-bundle",
        default=None,
        help="Path to approval bundle JSON (optional)",
    )
    parser.add_argument(
        "--write-artifacts",
        required=True,
        help="Directory to write combined_heal_result.json",
    )
    parser.add_argument(
        "--created-utc",
        required=True,
        help="ISO-8601 timestamp for the result (deterministic, no auto-now)",
    )
    parser.add_argument(
        "--plan-name",
        default="LEGACY_MIRROR_PLAN",
        help="Execution plan name (default: LEGACY_MIRROR_PLAN)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for future use (no-op in this wave)",
    )
    args = parser.parse_args()

    result = run_dispatcher(
        guardian_result_path=Path(args.guardian_result),
        write_artifacts_dir=Path(args.write_artifacts),
        created_utc=args.created_utc,
        plan_name=args.plan_name,
        approval_bundle_path=Path(args.approval_bundle) if args.approval_bundle else None,
    )

    print(result.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
