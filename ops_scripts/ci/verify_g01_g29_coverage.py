"""Spine verifier — G01..G29 coverage in the runtime gate verdict bundle.

Policy:
    1. If ``runtime_gate_verdict_bundle.json.payload.full_suite == True``,
       every gate ID from G01 through G29 MUST be present and have a
       ``result`` in {PASS, FAIL, NOT_APPLICABLE, HITL}. ``UNKNOWN`` on
       the allow-path is always fail-closed. ``NOT_APPLICABLE`` requires
       a non-empty ``na_reason``.
    2. If ``full_suite != True`` (cache-reuse / structural paths),
       coverage is legitimately partial; the verifier PASSes with an
       observation and does not fail-close on missing gates.

The R1B cache-reuse path does NOT invoke the full cascade; ``full_suite``
stays False. A future full-cascade entrypoint will flip it to True, at
which point this verifier becomes the mandatory coverage gate.

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

FULL_GATE_IDS: tuple[str, ...] = tuple(f"G{i:02d}" for i in range(1, 30))

ALLOWED_RESULTS: frozenset[str] = frozenset({
    "PASS", "FAIL", "NOT_APPLICABLE", "HITL", "UNKNOWN",
})

FAIL_CLOSED_RESULTS: frozenset[str] = frozenset({"UNKNOWN"})


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_g01_g29_coverage] artifact_dir={art_dir}")

    try:
        gate = load_payload(art_dir, "runtime_gate_verdict_bundle.json")
    except FileNotFoundError as exc:
        return fail("GATE_BUNDLE_MISSING", str(exc))

    full_suite = bool(gate.get("full_suite", False))
    if not full_suite:
        return passed(
            "runtime_gate_verdict_bundle.full_suite=False (R1B / structural); "
            "partial coverage is legitimate; G01..G29 enforcement deferred "
            "to full-cascade entrypoints"
        )

    # Full suite declared — enforce coverage.
    verdicts = gate.get("verdicts") or gate.get("gate_verdicts") or []
    if not isinstance(verdicts, list):
        return fail(
            "GATE_VERDICTS_SHAPE_INVALID",
            f"verdicts must be a list; got {type(verdicts).__name__}",
        )

    by_gate_id: dict[str, dict] = {}
    for v in verdicts:
        if not isinstance(v, dict):
            continue
        gid = str(v.get("gate_id", ""))
        if gid:
            by_gate_id[gid] = v

    missing_ids = [gid for gid in FULL_GATE_IDS if gid not in by_gate_id]
    if missing_ids:
        return fail(
            "G01_G29_COVERAGE_GAP",
            f"full_suite=True but {len(missing_ids)} gates missing: {missing_ids}",
        )

    # Per-gate shape checks.
    bad: list[str] = []
    for gid in FULL_GATE_IDS:
        v = by_gate_id[gid]
        result = str(v.get("result", ""))
        if result not in ALLOWED_RESULTS:
            bad.append(f"{gid}:result={result!r}")
            continue
        if result in FAIL_CLOSED_RESULTS:
            return fail(
                "GATE_UNKNOWN_TREATED_AS_NON_FAIL",
                f"{gid}.result=UNKNOWN must fail-close — not implicitly pass",
            )
        if result == "NOT_APPLICABLE":
            na_reason = v.get("na_reason") or v.get("not_applicable_reason")
            if not na_reason:
                return fail(
                    "GATE_NOT_APPLICABLE_WITHOUT_REASON",
                    f"{gid}.result=NOT_APPLICABLE requires non-empty na_reason",
                )
    if bad:
        return fail(
            "GATE_RESULT_INVALID",
            f"{len(bad)}: {bad[:5]}",
        )

    return passed(
        f"full_suite=True; all 29 gates (G01..G29) present and shape-valid"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
