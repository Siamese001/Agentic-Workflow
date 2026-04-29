"""Runner: replay proof (per 99.8 §5 / 99.5).

Reads ReplayComparisonReceipt entries from each scenario in a bundle and
asserts replay_status is PASS or EXPLAINED_VARIANCE.
"""

from __future__ import annotations

import sys

from tqdm import tqdm

from ._validate_common import load_bundle, parse_args


def main(argv: list[str] | None = None) -> int:
    args = parse_args("Validate deterministic replay receipts from a proof bundle.", argv)
    bundle = load_bundle(args.proof_bundle)

    failures: list[str] = []
    scenarios = bundle.get("scenarios", [])
    for scenario in tqdm(scenarios, desc="Validating replay", unit="scenario", disable=len(scenarios) < 5):
        sid = scenario["scenario_id"]
        receipts = scenario.get("replay_receipts", [])
        if not receipts:
            failures.append(f"{sid}: no replay receipts")
            continue
        for r in receipts:
            status = r.get("replay_status")
            if status not in {"PASS", "EXPLAINED_VARIANCE"}:
                failures.append(f"{sid}: replay_status={status}")
            for key in ("route_digest_match", "execution_digest_match", "exit_digest_match"):
                if r.get(key) is False:
                    failures.append(f"{sid}: {key}=False")

    if failures:
        for f in failures:
            print(f"[FAIL] {f}", file=sys.stderr)
        if args.strict:
            return 1
        return 0
    print("[PASS] replay validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
