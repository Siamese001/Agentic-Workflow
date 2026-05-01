"""W2 verifier #4 — No artifact stamped by harness.

Iterates all 12 W2 artifacts and FAIL_CLOSED if any envelope's
producer_component matches the harness regex (^tests\\., ^scripts\\.verify_,
^ops_scripts\\.ci\\.verify_, contains "harness"). Also enforces that the
no_harness_stamp_receipt.json artifact self-attests success.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (
    EXIT_HARNESS_ERROR,
    W2_ARTIFACT_FILENAMES,
    fail,
    is_harness_stamp,
    load_envelope,
    passed,
    resolve_artifact_dir,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_integrated_runtime_no_harness_stamp] artifact_dir={art_dir}")

    violations: list[str] = []
    for fn in W2_ARTIFACT_FILENAMES:
        try:
            env = load_envelope(art_dir, fn)
        except FileNotFoundError as exc:
            return fail("ARTIFACT_MISSING", f"{fn}: {exc}")
        producer = env.get("producer_component", "")
        if is_harness_stamp(producer):
            violations.append(f"{fn}:producer={producer!r}")
    if violations:
        return fail("HARNESS_STAMPING_DETECTED", f"{len(violations)}: {violations}")

    # Self-attestation must declare success.
    nh = load_envelope(art_dir, "no_harness_stamp_receipt.json")
    if not nh.get("payload", {}).get("all_artifacts_stamped_by_production"):
        return fail("NO_HARNESS_RECEIPT_NEGATIVE",
                    "no_harness_stamp_receipt.payload.all_artifacts_stamped_by_production is not True")

    return passed(f"all {len(W2_ARTIFACT_FILENAMES)} artifacts stamped by production code only")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
