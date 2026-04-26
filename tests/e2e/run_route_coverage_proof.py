"""Runner: route coverage proof (per 99.8 §3 and 99.2).

Usage:
    python -m tests.e2e.run_route_coverage_proof --all-routes \
        --emit-proof-bundle artifacts/e2e/routes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .proof.bundle import E2EProofBundle, now_iso, repo_commit, write_bundle
from .proof.contracts import ProofStatus
from .proof.digests import digest, short_id
from .proof.runner import run_scenario
from .proof.scenarios import route_coverage_scenarios
from .proof.validators import validate_route_coverage
from .proof.harness import emit_run


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route-coverage proof runner.")
    parser.add_argument("--all-routes", action="store_true", help="Run every route family.")
    parser.add_argument("--emit-proof-bundle", required=True, help="Output bundle directory.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on coverage gaps.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.all_routes:
        print("[ERROR] --all-routes is required", file=sys.stderr)
        return 2

    scenarios = route_coverage_scenarios()
    outcomes = []
    runs = []
    for sc in scenarios:
        outcome = run_scenario(sc)
        outcomes.append(outcome)
        runs.append((sc, emit_run(sc)))
        status = outcome.scenario_status.value
        print(f"[{status}] {sc.scenario_id} -> {sc.route_id.value}")
        for f in outcome.failures:
            print(f"   - {f}")

    cov_status, cov_fail = validate_route_coverage(runs)
    print(f"[ROUTE_COVERAGE] {cov_status.value}")
    for f in cov_fail:
        print(f"   - {f}")

    overall = (
        ProofStatus.PASS
        if (cov_status == ProofStatus.PASS and all(o.scenario_status == ProofStatus.PASS for o in outcomes))
        else ProofStatus.FAIL
    )

    bundle = E2EProofBundle(
        bundle_id="bundle-" + short_id({"ts": now_iso(), "scope": "route_coverage"}),
        generated_at=now_iso(),
        repo_commit=repo_commit(),
        scenario_set="route_coverage",
        policy_hash="policy:" + short_id("policy.v1"),
        blueprint_hash="blueprint:" + short_id("blueprint.v1"),
        registry_digest=digest({"version": "route_coverage.v1"}),
        tests_run=len(outcomes),
        scenarios=outcomes,
        failure_summary=cov_fail + [f"{o.scenario_id}: {f}" for o in outcomes for f in o.failures],
        acceptance_status=overall,
    )

    bundle_path = write_bundle(bundle, Path(args.emit_proof_bundle))
    print(f"[BUNDLE] {bundle_path}")

    if args.strict and overall != ProofStatus.PASS:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
