"""Emit the agentic_core spine proof bundle.

Scaffold-level emitter: enumerates each CoreScenario and records its
expected vs observed status. Today, no scenario runner exists in
agentic_core/L0_routing/composition_root.py for direct invocation
without an apps_* overlay, so every scenario starts as
`status=not_implemented` with an explicit blocking gap.

When agentic_core ships a `composition_root.run_scenario(scenario_id)`
hook (or equivalent), this module wires each scenario through that hook
and collects spine receipts the same way apps_e2e collects them — but
WITHOUT going through any apps_* package.

Usage:
    python -m tools.certification.agentic_core_e2e.run_core_proof
    python -m tools.certification.agentic_core_e2e.run_core_proof --print-table
"""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Any

from tools.certification.agentic_core_e2e import (
    CORE_HARNESS_SCHEMA_VERSION,
    CORE_PROOF_SCHEMA_VERSION,
    CORE_ROUTE_MATRIX_SCHEMA_VERSION,
)
from tools.certification.agentic_core_e2e.hash_utils import (
    REPO_ROOT, git_head, relative_to_repo, utc_now_iso, write_json,
)
from tools.certification.agentic_core_e2e.scenarios import CORE_SCENARIOS, CoreScenario

CORE_CERT_ROOT = REPO_ROOT / "artifacts" / "certification" / "agentic_core_e2e"
CORE_PROOF_PATH = CORE_CERT_ROOT / "agentic_core_spine_proof.json"
CORE_ROUTE_MATRIX_PATH = CORE_CERT_ROOT / "agentic_core_route_matrix.json"


def _try_invoke_scenario(scenario: CoreScenario) -> dict[str, Any]:
    """Attempt to drive scenario via agentic_core directly.

    Searches a documented list of candidate hook locations in order:

      1. agentic_core.L0_routing.composition_root.run_scenario(scenario_id)
      2. agentic_core.composition_root.run_scenario(scenario_id)
      3. agentic_core.L3_orchestration.run_scenario(scenario_id)

    The first that exists wins. If none exist, status=not_implemented
    with the exact list of probed paths so a future implementer knows
    where the hook is expected.
    """
    probed: list[str] = []
    candidates = (
        ("agentic_core.L0_routing.composition_root", "run_scenario"),
        ("agentic_core.composition_root", "run_scenario"),
        ("agentic_core.L3_orchestration", "run_scenario"),
    )
    runner = None
    found_at: str | None = None
    for module_path, attr in candidates:
        probed.append(f"{module_path}.{attr}")
        try:
            mod = __import__(module_path, fromlist=[attr])
        except ImportError:
            continue
        candidate = getattr(mod, attr, None)
        if callable(candidate):
            runner = candidate
            found_at = f"{module_path}.{attr}"
            break

    if runner is None:
        return {
            "status": "not_implemented",
            "reason": (
                "no run_scenario hook found in agentic_core. "
                f"Probed: {probed}. "
                "Add a hook with signature `run_scenario(scenario_id: str) -> dict` "
                "to one of these locations to activate this scenario."
            ),
            "probed_hook_paths": probed,
        }
    try:
        result = runner(scenario.scenario_id)
    except (TypeError, ValueError, RuntimeError, AttributeError, KeyError) as exc:
        return {
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
            "hook_path": found_at,
        }
    if not isinstance(result, dict):
        return {
            "status": "error",
            "reason": "scenario runner returned non-dict",
            "hook_path": found_at,
        }
    # Honor the hook's inner status. A hook that honestly says
    # "not_implemented" must not be treated as "ran". Allowed inner
    # status values: ran | not_implemented | error | skipped.
    inner_status = result.get("status") or "ran"
    if inner_status not in {"ran", "not_implemented", "error", "skipped"}:
        inner_status = "error"
    return {
        "status": inner_status,
        "reason": result.get("reason"),
        "result": result,
        "hook_path": found_at,
    }


def build_core_proof() -> dict[str, Any]:
    commit, dirty = git_head()
    rows: list[dict[str, Any]] = []
    blocking: list[str] = []
    for scenario in CORE_SCENARIOS:
        outcome = _try_invoke_scenario(scenario)
        row = {
            "scenario_id": scenario.scenario_id,
            "description": scenario.description,
            "expected_route_form": scenario.expected_route_form,
            "expects_l3": scenario.expects_l3,
            "expects_c0": scenario.expects_c0,
            "expects_pa": scenario.expects_pa,
            "expects_l2": scenario.expects_l2,
            "expects_uwg": scenario.expects_uwg,
            "expects_l6": scenario.expects_l6,
            "status": outcome.get("status"),
            "reason": outcome.get("reason"),
            "result_summary": outcome.get("result"),
            "hook_path": outcome.get("hook_path"),
            "probed_hook_paths": outcome.get("probed_hook_paths"),
            "pass": outcome.get("status") == "ran",
        }
        rows.append(row)
        if not row["pass"]:
            blocking.append(f"core_scenario_{scenario.scenario_id}_not_executable")

    success = not blocking
    return {
        "proof_schema_version": CORE_PROOF_SCHEMA_VERSION,
        "harness_schema_version": CORE_HARNESS_SCHEMA_VERSION,
        "harness_kind": "agentic_core_spine",
        "generated_at_utc": utc_now_iso(),
        "git_commit": commit,
        "git_dirty": dirty,
        "harness_run_id": f"core-e2e-{uuid.uuid4().hex[:16]}",
        "spine_route_matrix_ref": relative_to_repo(CORE_ROUTE_MATRIX_PATH),
        "scenarios": rows,
        "success": success,
        "blocking_gaps": blocking,
        "harness_pass": True,
        "honest_fail_closed": not success,
        "notes": (
            "Agentic core spine harness scaffold. Scenarios cannot be driven "
            "without agentic_core.composition_root.run_scenario(scenario_id). "
            "When that hook ships, every scenario row will populate result_summary. "
            "This harness is INTENTIONALLY DECOUPLED from the apps_* harness — "
            "neither imports the other. See plan §14."
        ),
    }


def build_core_route_matrix(proof: dict[str, Any]) -> dict[str, Any]:
    commit, _ = git_head()
    return {
        "matrix_schema_version": CORE_ROUTE_MATRIX_SCHEMA_VERSION,
        "generated_at_utc": utc_now_iso(),
        "git_commit": commit,
        "harness_run_id": proof["harness_run_id"],
        "scenario_count": len(proof["scenarios"]),
        "passing": sum(1 for r in proof["scenarios"] if r["pass"]),
        "failing": sum(1 for r in proof["scenarios"] if not r["pass"]),
        "rows": [
            {
                "scenario_id": r["scenario_id"],
                "expected_route_form": r["expected_route_form"],
                "status": r["status"],
                "pass": r["pass"],
            }
            for r in proof["scenarios"]
        ],
    }


def print_table(proof: dict[str, Any]) -> None:
    cols = (
        ("Scenario", "scenario_id", 26),
        ("Form", "expected_route_form", 22),
        ("L3", "expects_l3", 5),
        ("C0", "expects_c0", 5),
        ("PA", "expects_pa", 5),
        ("L2", "expects_l2", 5),
        ("UWG", "expects_uwg", 5),
        ("L6", "expects_l6", 5),
        ("Status", "status", 18),
        ("Pass", "pass", 6),
    )
    header = "  ".join(f"{n:<{w}}" for n, _, w in cols)
    print(header)
    print("-" * len(header))
    for r in proof["scenarios"]:
        cells = []
        for _, k, w in cols:
            v = r.get(k)
            v = "true" if v is True else ("false" if v is False else ("" if v is None else str(v)))
            cells.append(f"{v[:w]:<{w}}")
        print("  ".join(cells))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run_core_proof", add_help=True)
    p.add_argument("--print-table", action="store_true")
    args = p.parse_args(argv)

    CORE_CERT_ROOT.mkdir(parents=True, exist_ok=True)
    proof = build_core_proof()
    matrix = build_core_route_matrix(proof)
    digest, size = write_json(CORE_PROOF_PATH, proof)
    write_json(CORE_ROUTE_MATRIX_PATH, matrix)

    print(f"[core_proof] wrote {relative_to_repo(CORE_PROOF_PATH)} ({size} B, sha256={digest[:12]}…)")
    print(f"[core_proof] success={proof['success']} blocking_gaps={len(proof['blocking_gaps'])}")
    if proof["blocking_gaps"]:
        for g in proof["blocking_gaps"][:5]:
            print(f"             - {g}")
    if args.print_table:
        print()
        print_table(proof)
    return 0


if __name__ == "__main__":
    sys.exit(main())
