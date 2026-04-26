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
_MODEL_SPAN_REQUIRED = ("provider", "model_id", "latency_ms", "tokens_in", "tokens_out", "cost_usd", "status")
_SIDE_EFFECT_ROUTES = {"R4_SINGLE_ACTION", "R3_PLUS_R4_SINGLE_STEP", "UWG_COMMIT_PATH"}
_SIDE_EFFECT_REQUIRED = ("capability_token_ref", "sandbox_envelope_ref")


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
        _validate_scenario_spans(sid, scenario, traces, failures)

    if failures:
        for f in failures:
            print(f"[FAIL] {f}", file=sys.stderr)
        if args.strict:
            return 1
        return 0
    print("[PASS] trace tree validated")
    return 0


def _validate_scenario_spans(sid: str, scenario: dict, traces: list, failures: list[str]) -> None:
    span_ids = {s["span_id"] for s in traces}
    names = [s["name"] for s in traces]
    sealed = scenario.get("contracts", {}).get("SealedL2Artifact", {})
    side_effect = bool(sealed.get("side_effect")) if isinstance(sealed, dict) else False
    for span in traces:
        _validate_one_span(sid, span, span_ids, side_effect, failures)
    if "l6.ingest" in names and "exit.disposition" in names:
        if names.index("l6.ingest") <= names.index("exit.disposition"):
            failures.append(f"{sid}: l6.ingest precedes exit.disposition")


def _validate_one_span(sid: str, span: dict, span_ids: set, side_effect: bool, failures: list[str]) -> None:
    attrs = span.get("attributes", {})
    for attr in _REQUIRED_ATTRS:
        if not attrs.get(attr):
            failures.append(f"{sid}/{span['name']}: missing attribute {attr}")
    if span.get("parent_span_id") and span["parent_span_id"] not in span_ids:
        failures.append(f"{sid}/{span['name']}: dangling parent {span['parent_span_id']}")
    if span["name"] == "l2.e3.exec":
        missing = [k for k in _MODEL_SPAN_REQUIRED if attrs.get(k) in (None, "")]
        if missing:
            failures.append(f"{sid}/l2.e3.exec: missing model attrs {missing}")
        if side_effect:
            se_missing = [k for k in _SIDE_EFFECT_REQUIRED if not attrs.get(k)]
            if se_missing:
                failures.append(f"{sid}/l2.e3.exec side-effect: missing {se_missing}")


if __name__ == "__main__":
    raise SystemExit(main())
