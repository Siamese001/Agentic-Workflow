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
from agentic_core.L2_execution.types.healer_registry import HEALER_REGISTRY
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
    "reconciliation": ("guardian_classification_compliance",),
    "alignment": ("guardian_hierarchy_compliance",),
    "arch_validation": ("guardian_architecture_governance",),
    "healing": (),
    "certification": (),
}

NOTE_MAPPED = "no healer registered"
NOTE_UNMAPPED = "unmapped to phase; no healer registered"

# Dispatcher-local override: which phases require L3 approval.
# Does NOT modify LEGACY_MIRROR_PLAN; evaluated at dispatch time.
PHASE_APPROVAL_REQUIRED_OVERRIDES: dict[str, bool] = {}


SANDBOX_SENTINEL = ".ssot_sandbox"


class ApprovalGatingError(Exception):
    """Raised when a phase requires approval but none was provided."""


class MutationGuardError(Exception):
    """Raised when apply mode is used without sandbox or explicit override."""


def mutation_allowed(repo_root: Path, allow_override: bool) -> bool:
    """Check if mutations are permitted in the given repo root.

    Mutations allowed iff:
    - repo_root contains the sandbox sentinel file, OR
    - allow_override is True (--allow-repo-mutation)
    """
    if allow_override:
        return True
    return (repo_root / SANDBOX_SENTINEL).is_file()


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


def approvals_satisfy_phase(
    bundle: ApprovalBundle | None,
    phase_name: str,
) -> bool:
    """Check whether the approval bundle satisfies gating for a phase.

    Returns True iff bundle contains at least one record where:
    - record.phase_name == phase_name
    - record.decision == APPROVED
    - record.token is non-empty
    """
    if bundle is None:
        return False
    for record in bundle.records:
        if record.phase_name == phase_name and record.decision == ApprovalDecision.APPROVED and record.token:
            return True
    return False


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


def extract_checks_by_id(guardian_aggregate: dict[str, Any]) -> dict[str, dict]:
    """Build a lookup from check_id to full check dict.

    For duplicate check_ids, the first occurrence wins.
    """
    result: dict[str, dict] = {}
    for item in guardian_aggregate.get("checks", []):
        if isinstance(item, dict) and "check_id" in item:
            cid = item["check_id"]
            if cid not in result:
                result[cid] = item
    return result


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
# Healer invocation
# ---------------------------------------------------------------------------


def _invoke_healer(
    check_id: str,
    check_dict: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Invoke a registered healer safely, converting errors to FAILED results.

    Passes repo_root and apply as keyword arguments to healers that accept them.
    Returns the healer's HealCheckResult on success, or a FAILED result
    containing the exception class name on error.
    """
    healer_fn = HEALER_REGISTRY[check_id]
    try:
        return healer_fn(check_dict, repo_root=repo_root, apply=apply)
    # guardian: allow-silent-swallow
    except Exception as exc:
        return HealCheckResult(
            check_id=check_id,
            status=HealStatus.FAILED,
            changes_made=(),
            rollback_info=None,
            notes=f"healer error: {type(exc).__name__}: {exc}",
        )


# ---------------------------------------------------------------------------
# Core dispatcher logic
# ---------------------------------------------------------------------------


def run_dispatcher(
    guardian_result_path: Path,
    write_artifacts_dir: Path,
    created_utc: str,
    plan_name: str = "LEGACY_MIRROR_PLAN",
    approval_bundle_path: Path | None = None,
    *,
    apply: bool = False,
    repo_root: Path | None = None,
    allow_repo_mutation: bool = False,
) -> CombinedHealResult:
    """Execute the dispatcher interpreting LEGACY_MIRROR_PLAN PhaseSpec.

    1. Validates PhaseSpec name integrity.
    2. Enforces mutation guard if apply mode requested.
    3. Loads the guardian aggregate and extracts check_ids.
    4. Loads optional ApprovalBundle (needed before phase iteration for gating).
    5. Classifies check_ids as mapped or unmapped via phase prefix mapping.
    6. Iterates phases in order, enforcing approval gating.
    7. Produces a CombinedHealResult.
    8. Validates and writes the result to the output directory.

    Returns the CombinedHealResult.
    Raises ApprovalGatingError if a phase requires approval and none is provided.
    Raises MutationGuardError if apply without sandbox or override.
    """
    # 1. Validate PhaseSpec integrity
    validate_phase_names(LEGACY_MIRROR_PLAN)

    # 2. Mutation guard
    if apply:
        if repo_root is None:
            raise MutationGuardError(
                "--apply requires --repo-root to identify the target repository",
            )
        if not mutation_allowed(repo_root, allow_repo_mutation):
            raise MutationGuardError(
                f"Mutation refused: repo at '{repo_root}' is not a sandbox "
                f"(missing {SANDBOX_SENTINEL}) and --allow-repo-mutation not set",
            )

    # 3. Load guardian aggregate
    guardian_data = json.loads(guardian_result_path.read_text(encoding="utf-8"))
    check_ids = extract_check_ids(guardian_data)
    checks_by_id = extract_checks_by_id(guardian_data)

    # 4. Load optional approval bundle (before phase iteration for gating)
    bundle: ApprovalBundle | None = None
    approved_tokens: list[str] = []
    if approval_bundle_path is not None:
        bundle = load_approval_bundle(approval_bundle_path)
        for record in bundle.records:
            if record.decision == ApprovalDecision.APPROVED:
                approved_tokens.append(record.token)
    approved_tokens = sorted(set(approved_tokens))

    # 5. Classify check_ids
    mapped_ids, unmapped_ids = classify_check_ids(check_ids)

    # 6. Iterate phases in PhaseSpec order
    heal_checks: list[HealCheckResult] = []
    for phase in LEGACY_MIRROR_PLAN.phases:
        # Select check_ids for this phase
        prefixes = PHASE_CHECK_ID_PREFIXES.get(phase.name, ())
        phase_cids = sorted(cid for cid in check_ids if any(cid.startswith(p) for p in prefixes))

        # --- Approval gating enforcement ---
        phase_requires_approval = PHASE_APPROVAL_REQUIRED_OVERRIDES.get(
            phase.name,
            phase.approval_required,
        )
        if phase_requires_approval and phase_cids:
            if not approvals_satisfy_phase(bundle, phase.name):
                raise ApprovalGatingError(
                    f"Phase '{phase.name}' requires L3 approval but no matching "
                    f"APPROVED record found in ApprovalBundle for phase_name='{phase.name}'",
                )

        for cid in phase_cids:
            if cid in HEALER_REGISTRY:
                check_dict = checks_by_id.get(cid, {"check_id": cid})
                heal_checks.append(
                    _invoke_healer(cid, check_dict, repo_root=repo_root, apply=apply),
                )
            else:
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

    # 7. Add unmapped check_ids (coverage preservation)
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

    # 8. Build CombinedHealResult
    result = CombinedHealResult(
        tool_id=TOOL_ID,
        plan_name=plan_name,
        results=tuple(heal_checks),
        approved_by=tuple(approved_tokens),
        created_utc=created_utc,
    )

    # 9. Validate before writing
    errors = result.validate()
    if errors:
        raise ValueError(f"CombinedHealResult validation failed: {errors}")

    # 10. Write artifact
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
        "--apply",
        action="store_true",
        help="Enable mutating healers (default: dry-run only)",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Path to repository root (required if --apply)",
    )
    parser.add_argument(
        "--allow-repo-mutation",
        action="store_true",
        help="Allow mutations on non-sandbox repos (use with caution)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for future use (no-op in this wave)",
    )
    args = parser.parse_args()

    try:
        result = run_dispatcher(
            guardian_result_path=Path(args.guardian_result),
            write_artifacts_dir=Path(args.write_artifacts),
            created_utc=args.created_utc,
            plan_name=args.plan_name,
            approval_bundle_path=Path(args.approval_bundle) if args.approval_bundle else None,
            apply=args.apply,
            repo_root=Path(args.repo_root) if args.repo_root else None,
            allow_repo_mutation=args.allow_repo_mutation,
        )
    except MutationGuardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    except ApprovalGatingError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(result.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
