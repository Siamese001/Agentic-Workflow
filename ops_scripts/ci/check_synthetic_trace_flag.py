"""Spine verifier — synthetic / fixture / mock flag honesty.

Independent re-run of the SSOT synthetic-trace detector against the run
directory. FAIL_CLOSED if the spine proof bundle's flags disagree with
what the detector finds NOW, or if any flag is True while the bundle
declares ``runtime_mode == 'production'``.

The check is deliberately separate from ``verify_spine_proof_bundle``:
that verifier checks the bundle's internal consistency; THIS verifier
re-runs the detector and asserts the bundle did not under-report.

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

from agentic_core.L6_observability.runtime_trace.synthetic_trace_detector import (  # noqa: E402  # guardian: allow-layer-violation -- ADR-096 L6 universally importable; CI gate verifies synthetic-trace flag via L6 detector
    detect_trace_provenance,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[check_synthetic_trace_flag] artifact_dir={art_dir}")

    try:
        bundle = load_payload(art_dir, "agentic_core_spine_proof.json")
    except FileNotFoundError as exc:
        return fail("SPINE_PROOF_MISSING", str(exc))

    runtime_mode = str(bundle.get("runtime_mode", ""))
    bundle_synthetic = bool(bundle.get("synthetic_trace_detected", False))
    bundle_fixture = bool(bundle.get("fixture_mode_detected", False))
    bundle_mock = bool(bundle.get("mock_mode_detected", False))

    # Re-run the detector independently of the bundle's claimed flags.
    auto = detect_trace_provenance(art_dir)

    # Under-reporting: detector finds True but bundle says False.
    if auto.synthetic_trace_detected and not bundle_synthetic:
        return fail(
            "SYNTHETIC_TRACE_UNDER_REPORTED",
            f"detector reported synthetic_trace_detected=True (reasons={list(auto.reasons)}) "
            f"but bundle says False",
        )
    if auto.fixture_mode_detected and not bundle_fixture:
        return fail(
            "FIXTURE_MODE_UNDER_REPORTED",
            f"detector reported fixture_mode_detected=True (reasons={list(auto.reasons)}) "
            f"but bundle says False",
        )
    if auto.mock_mode_detected and not bundle_mock:
        return fail(
            "MOCK_MODE_UNDER_REPORTED",
            f"detector reported mock_mode_detected=True (reasons={list(auto.reasons)}) "
            f"but bundle says False",
        )

    # Production-mode invariant.
    if runtime_mode == "production":
        if bundle_synthetic:
            return fail(
                "PRODUCTION_WITH_SYNTHETIC_TRACE",
                "runtime_mode=production AND synthetic_trace_detected=True is forbidden",
            )
        if bundle_fixture:
            return fail(
                "PRODUCTION_WITH_FIXTURE_MODE",
                "runtime_mode=production AND fixture_mode_detected=True is forbidden",
            )
        if bundle_mock:
            return fail(
                "PRODUCTION_WITH_MOCK_MODE",
                "runtime_mode=production AND mock_mode_detected=True is forbidden",
            )

    return passed(
        f"runtime_mode={runtime_mode!r}; synthetic={bundle_synthetic}, "
        f"fixture={bundle_fixture}, mock={bundle_mock}; "
        f"detector_reasons={list(auto.reasons)[:5]}"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
