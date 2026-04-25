"""CI gate — L1PlanContract schema drift check (ADR-043).

Verifies that the canonical v1 and v2 contract classes in
``agentic_core/L1_cognition/types/plan_contract_types.py`` carry exactly the
fields mandated by ``agentic_process_mapping_v33.md`` §2 + ADR-043.

Fails closed on missing fields.  Also surfaces (warning, not failure) any
code site that still instantiates the v1 ``L1PlanContract`` so migration
progress to ``L1PlanContractV2`` can be tracked during the 90-day window.

Run:
    python ops_scripts/ci/check_l1_plan_contract_fields.py

Exit codes:
    0 — schema OK, migration tracker printed
    1 — schema drift (missing required field on v1 or v2)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "agentic_core" / "L1_cognition" / "types" / "plan_contract_types.py"

# Canonical v1 fields (frozen at ADR-043 baseline).
V1_REQUIRED_FIELDS = (
    "plan_id",
    "request_id",
    "policy_hash",
    "reasoning_mode",
    "grounding_required",
    "confidence_score",
    "steps",
)

# Canonical v2 fields per ADR-043 §Decision.
V2_REQUIRED_FIELDS = (
    "plan_id",
    "request_id",
    "policy_hash",
    "proposed_route",
    "reasoning_mode",
    "query_spec",
    "task_spec",
    "route_risk",
    "confidence_score",
    "grounding_required",
    "declared_assumptions",
    "unresolved_gaps",
    "published_rationale",
    "planner_telemetry",
)


def _load_contract_fields() -> tuple[set[str], set[str]]:
    """Import the module and read the field names off both dataclasses."""
    sys.path.insert(0, str(REPO_ROOT))
    # The module imports many lifecycle emitters; that is fine at CI time.
    from agentic_core.L1_cognition.types.plan_contract_types import (  # noqa: PLC0415
        L1PlanContract,
        L1PlanContractV2,
    )

    v1 = {f for f in L1PlanContract.__dataclass_fields__ if not f.startswith("_")}
    v2 = {f for f in L1PlanContractV2.__dataclass_fields__ if not f.startswith("_")}
    return v1, v2


def _count_v1_instantiations() -> int:
    """Count v1 direct instantiation sites via ripgrep (best-effort)."""
    try:
        out = subprocess.run(
            [
                "rg",
                "-n",
                r"L1PlanContract\s*\(",
                "--glob",
                "!tests/**",
                "--glob",
                "!**/plan_contract_types.py",
                str(REPO_ROOT),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if out.returncode not in (0, 1):  # 1 = no matches, still OK
            return -1
        return len([ln for ln in out.stdout.splitlines() if ln.strip()])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return -1


def main() -> int:
    print(f"[check_l1_plan_contract_fields] contract file: {CONTRACT_PATH}")
    if not CONTRACT_PATH.is_file():
        print(f"ERROR: contract file not found: {CONTRACT_PATH}", file=sys.stderr)
        return 1

    v1_actual, v2_actual = _load_contract_fields()

    v1_missing = set(V1_REQUIRED_FIELDS) - v1_actual
    v2_missing = set(V2_REQUIRED_FIELDS) - v2_actual

    failed = False
    if v1_missing:
        print(
            f"ERROR: L1PlanContract v1 missing required fields: {sorted(v1_missing)}",
            file=sys.stderr,
        )
        failed = True
    else:
        print(f"OK: L1PlanContract v1 has all {len(V1_REQUIRED_FIELDS)} required fields.")

    if v2_missing:
        print(
            f"ERROR: L1PlanContractV2 missing required fields: {sorted(v2_missing)}",
            file=sys.stderr,
        )
        failed = True
    else:
        print(f"OK: L1PlanContractV2 has all {len(V2_REQUIRED_FIELDS)} required fields.")

    # Migration tracker (warning only).
    remaining = _count_v1_instantiations()
    if remaining < 0:
        print("WARN: could not count v1 instantiations (ripgrep unavailable).")
    else:
        print(
            f"MIGRATION: {remaining} non-test site(s) still instantiate v1 L1PlanContract "
            f"(v2 target — see ADR-043)."
        )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
