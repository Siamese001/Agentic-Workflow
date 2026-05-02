"""Nightly batch driver — emits live proof bundles for every runnable app
and rolls them up into apps_e2e_matrix.json.

Each app's `python -m <app>` is bounded by SUBPROCESS_TIMEOUT_SECONDS
(900 s ceiling). Failures are recorded in the bundle (honest fail-closed)
and never crash the harness — every spec gets a bundle, even if its app
crashes.

Usage:
    python -m tools.certification.apps_e2e.nightly_run
    python -m tools.certification.apps_e2e.nightly_run --skip apps_lic apps_research
    python -m tools.certification.apps_e2e.nightly_run --dry-run

Exit codes:
    0 — every spec produced a bundle (each bundle's `success` field
        independently reports whether the app routed through the spine)
    2 — harness-level failure (e.g. matrix generator crashed)
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Sequence

from tools.certification.apps_e2e.app_specs import APP_SPECS
from tools.certification.apps_e2e.emit_proof_bundle import emit_one
from tools.certification.apps_e2e.matrix_builder import build_matrix, print_table
from tools.certification.apps_e2e.hash_utils import (
    relative_to_repo, write_json,
)
from tools.certification.apps_e2e.paths import MATRIX_PATH


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nightly_run", add_help=True)
    parser.add_argument("--dry-run", action="store_true",
                        help="skip subprocess; emit bundle from on-disk artifacts")
    parser.add_argument("--skip", nargs="*", default=[],
                        help="apps_<name> values to omit from this run")
    parser.add_argument("--include-skeleton", action="store_true",
                        help="also emit bundles for non-runnable AppSpecs")
    args = parser.parse_args(argv)

    skip = set(args.skip or [])
    started = time.time()
    print(f"[nightly] started_at={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started))}")
    per_app_durations: list[tuple[str, float, bool]] = []

    for spec in APP_SPECS:
        if spec.app_name in skip:
            print(f"[nightly] SKIP {spec.app_name} (--skip)")
            continue
        if not spec.runnable and not args.include_skeleton:
            print(f"[nightly] SKIP {spec.app_name} (skeleton-only; pass --include-skeleton to include)")
            continue
        t0 = time.time()
        try:
            _, bundle = emit_one(spec, dry_run=args.dry_run)
            success = bool(bundle.get("success"))
        except (OSError, ValueError, RuntimeError) as exc:  # harness-level error
            print(f"[nightly] ERROR {spec.app_name}: {type(exc).__name__}: {exc}")
            success = False
        per_app_durations.append((spec.app_name, time.time() - t0, success))

    # Build matrix
    print()
    print("[nightly] building all-apps matrix")
    try:
        matrix = build_matrix()
        write_json(MATRIX_PATH, matrix)
        print(f"[nightly] wrote {relative_to_repo(MATRIX_PATH)}")
        print()
        print_table(matrix)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[nightly] FATAL: matrix builder crashed: {type(exc).__name__}: {exc}")
        return 2

    # Per-app duration report
    print()
    print("[nightly] per-app durations:")
    for name, dur, ok in per_app_durations:
        flag = "OK" if ok else "FAIL"
        print(f"  {name:<24} {dur:7.1f}s  {flag}")
    total = time.time() - started
    print(f"[nightly] total_wall_clock={total:.1f}s "
          f"({sum(1 for _,_,o in per_app_durations if o)}/{len(per_app_durations)} success)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
