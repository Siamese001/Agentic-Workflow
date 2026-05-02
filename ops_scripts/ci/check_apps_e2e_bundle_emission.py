"""Gate 1: apps_e2e_bundle_emission.

Verifies that every runnable apps_* package emits a valid, hash-bound,
run_id-bound proof bundle. Uses verifier_cli in `smoke` mode — schema and
hash-consistency violations fail this gate; honest fail-closed bundles
(success=False with explicit blocking_gaps) DO NOT.

Plan: apps-e2e-two-gate-certification-d8b3a1 §2.1 + §7.

Exit codes:
    0 — all bundles valid (or warn-mode equivalent)
    1 — at least one bundle violates schema/hash invariants
    2 — usage error
"""
from __future__ import annotations

import sys

from tools.certification.apps_e2e.verifier_cli import main as _verifier_main


def main(argv: list[str] | None = None) -> int:
    forwarded = list(argv or [])
    # Force smoke mode regardless of caller arguments.
    return _verifier_main(["--mode", "smoke", *forwarded])


if __name__ == "__main__":
    rc = main(sys.argv[1:])
    if rc == 0:
        print("\n[apps_e2e_bundle_emission] OK")
    else:
        print("\n[apps_e2e_bundle_emission] FAIL")
    sys.exit(rc)
