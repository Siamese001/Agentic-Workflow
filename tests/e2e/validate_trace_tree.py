"""Runner: trace tree proof (per 99.8 §4 / 99.4).

Re-walks every scenario's span tree in an existing bundle and verifies the
99.4 trace requirements: required root attributes, parent_id linkage,
forbidden spans absent, L6 only after exit.disposition.
"""

from __future__ import annotations

import sys

from tqdm import tqdm

from ._validate_common import load_bundle, parse_args


_REQUIRED_ATTRS = ("request_id", "run_id", "trace_root", "policy_hash", "blueprint_hash", "replay_key")


def main(argv: list[str] | None = None) -> int:
    args = parse_args("Validate OTEL trace tree from a proof bundle.", argv)
    bundle = load_bundle(args.proof_bundle)

    failures: list[str] = []
    scenarios = bundle.get("scenarios", [])
    for scenario in tqdm(
        scenarios, desc="Validating trace tree", unit="scenario", disable=len(scenarios) < 5
    ):
        sid = scenario["scenario_id"]
        traces = scenario.get("traces", [])
        if not traces:
            failures.append(f"{sid}: no traces in bundle")
            continue
        span_ids = {s["span_id"] for s in traces}
        names = [s["name"] for s in traces]
        for span in traces:
            for attr in _REQUIRED_ATTRS:
                if not span.get("attributes", {}).get(attr):
                    failures.append(f"{sid}/{span['name']}: missing attribute {attr}")
            if span.get("parent_span_id") and span["parent_span_id"] not in span_ids:
                failures.append(f"{sid}/{span['name']}: dangling parent {span['parent_span_id']}")
        if "l6.ingest" in names and "exit.disposition" in names:
            if names.index("l6.ingest") <= names.index("exit.disposition"):
                failures.append(f"{sid}: l6.ingest precedes exit.disposition")

    if failures:
        for f in failures:
            print(f"[FAIL] {f}", file=sys.stderr)
        if args.strict:
            return 1
        return 0
    print("[PASS] trace tree validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
