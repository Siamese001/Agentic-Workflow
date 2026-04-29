"""Runner: no-bypass + sovereignty proof (per 99.8 §6 / 99.6)."""

from __future__ import annotations

import sys

from tqdm import tqdm

from ._validate_common import load_bundle, parse_args


def main(argv: list[str] | None = None) -> int:
    args = parse_args("Validate no-bypass receipts from a proof bundle.", argv)
    bundle = load_bundle(args.proof_bundle)

    failures: list[str] = []
    scenarios = bundle.get("scenarios", [])
    for scenario in tqdm(scenarios, desc="Validating no-bypass", unit="scenario", disable=len(scenarios) < 5):
        sid = scenario["scenario_id"]
        receipts = scenario.get("no_bypass_receipts", [])
        if not receipts:
            failures.append(f"{sid}: no no-bypass receipts")
            continue
        for r in receipts:
            if r.get("proof_status") != "PASS":
                failures.append(f"{sid}: no_bypass={r.get('proof_status')}")
            if r.get("authority_boundary_status") != "OK":
                failures.append(f"{sid}: authority_boundary={r.get('authority_boundary_status')}")
            for v in r.get("violations", []):
                failures.append(f"{sid}: violation={v}")

    if failures:
        for f in failures:
            print(f"[FAIL] {f}", file=sys.stderr)
        if args.strict:
            return 1
        return 0
    print("[PASS] no-bypass validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
