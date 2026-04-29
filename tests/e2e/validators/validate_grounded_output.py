"""Runner: groundedness proof (per 99.8 §7 / 99.7)."""

from __future__ import annotations

import sys

from tqdm import tqdm

from ._validate_common import load_bundle, parse_args


def main(argv: list[str] | None = None) -> int:
    args = parse_args("Validate groundedness receipts from a proof bundle.", argv)
    bundle = load_bundle(args.proof_bundle)

    failures: list[str] = []
    scenarios = bundle.get("scenarios", [])
    for scenario in tqdm(
        scenarios, desc="Validating groundedness", unit="scenario", disable=len(scenarios) < 5
    ):
        sid = scenario["scenario_id"]
        receipts = scenario.get("groundedness_receipts", [])
        if not receipts:
            failures.append(f"{sid}: no groundedness receipts")
            continue
        for r in receipts:
            status = r.get("proof_status")
            if status not in {"PASS", "NOT_APPLICABLE", "WEAK_WITH_CAVEATS"}:
                failures.append(f"{sid}: groundedness_status={status}")
            unsupported = r.get("unsupported_claims", [])
            if unsupported:
                failures.append(f"{sid}: unsupported_claims={unsupported}")
            if r.get("prompt_data_boundary_status") not in {"ENFORCED", "NOT_APPLICABLE"}:
                failures.append(f"{sid}: prompt_data_boundary={r.get('prompt_data_boundary_status')}")

    if failures:
        for f in failures:
            print(f"[FAIL] {f}", file=sys.stderr)
        if args.strict:
            return 1
        return 0
    print("[PASS] groundedness validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
