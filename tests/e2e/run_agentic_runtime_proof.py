"""Runner: full E2E proof suite (per 99.8 §RECOMMENDED COMMAND SURFACES #1, #2).

Usage:
    python -m tests.e2e.run_agentic_runtime_proof --scenario-set all \
        --emit-proof-bundle artifacts/e2e/latest

    python -m tests.e2e.run_agentic_runtime_proof --scenario GP-001 \
        --emit-proof-bundle artifacts/e2e/gp_001
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .proof.bundle import E2EProofBundle, now_iso, repo_commit, write_bundle
from .proof.contracts import ProofStatus
from .proof.digests import digest, short_id
from .proof.runner import run_scenario
from .proof.scenarios import GOLDEN_PATH_ID, all_scenarios, by_ids


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the agentic runtime proof harness.")
    parser.add_argument(
        "--scenario-set",
        choices=["all", "golden", "routes"],
        default=None,
        help="Run a named scenario set.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        help="Run a specific scenario id (may be repeated).",
    )
    parser.add_argument(
        "--emit-proof-bundle",
        required=True,
        help="Directory to emit the proof bundle into.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any scenario fails.",
    )
    return parser.parse_args(argv)


def select_scenarios(args: argparse.Namespace) -> list:
    if args.scenario:
        return by_ids(args.scenario)
    if args.scenario_set == "golden":
        return by_ids([GOLDEN_PATH_ID])
    if args.scenario_set == "routes":
        return [s for s in all_scenarios() if s.scenario_id.startswith("RC-")]
    # default = all
    return all_scenarios()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    scenarios = select_scenarios(args)
    if not scenarios:
        print("[ERROR] no scenarios selected", file=sys.stderr)
        return 2

    outcomes = []
    for sc in scenarios:
        outcome = run_scenario(sc)
        outcomes.append(outcome)
        status_marker = (
            "PASS" if outcome.scenario_status == ProofStatus.PASS else outcome.scenario_status.value
        )
        print(f"[{status_marker}] {sc.scenario_id} ({sc.route_id.value})")
        for f in outcome.failures:
            print(f"   - {f}")

    overall = (
        ProofStatus.PASS
        if all(o.scenario_status == ProofStatus.PASS for o in outcomes)
        else ProofStatus.PARTIAL
        if any(o.scenario_status == ProofStatus.PASS for o in outcomes)
        else ProofStatus.FAIL
    )

    bundle = E2EProofBundle(
        bundle_id="bundle-" + short_id({"ts": now_iso(), "scenarios": [o.scenario_id for o in outcomes]}),
        generated_at=now_iso(),
        repo_commit=repo_commit(),
        scenario_set=args.scenario_set or ("custom" if args.scenario else "all"),
        policy_hash="policy:" + short_id("policy.v1"),
        blueprint_hash="blueprint:" + short_id("blueprint.v1"),
        registry_digest=digest({"version": "harness.v1"}),
        tests_run=len(outcomes),
        scenarios=outcomes,
        failure_summary=[f"{o.scenario_id}: {f}" for o in outcomes for f in o.failures],
        acceptance_status=overall,
    )

    bundle_path = write_bundle(bundle, Path(args.emit_proof_bundle))
    print(f"[BUNDLE] {bundle_path}")
    print(f"[OVERALL] {overall.value}")

    if args.strict and overall != ProofStatus.PASS:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
