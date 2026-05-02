"""Gate 2: apps_e2e_spine_certification.

Verifies that every certification_required runnable apps_* package has
`success=true`, no blocking_gaps, full receipt-set hash-verified, and a
recomputed `certification_level` of `SPINE_COMPLETE_CERTIFIED`. Strict mode.

Plan: apps-e2e-two-gate-certification-d8b3a1 §2.2 + §5.3.

Today this gate is EXPECTED to fail until the 5 currently-uncertified
apps (apps_eval, apps_exec, apps_lic, apps_research, apps_rfp) emit real
spine receipts. The CI workflow runs this gate as informational
(`continue-on-error: true`) until critical mass.

Exit codes:
    0 — all certification_required apps are SPINE_COMPLETE_CERTIFIED
    1 — one or more strict-mode violations
    2 — usage error
"""
from __future__ import annotations

import sys

from tools.certification.apps_e2e.verifier_cli import main as _verifier_main


def main(argv: list[str] | None = None) -> int:
    forwarded = list(argv or [])
    return _verifier_main(["--mode", "strict", *forwarded])


if __name__ == "__main__":
    rc = main(sys.argv[1:])
    if rc == 0:
        print("\n[apps_e2e_spine_certification] OK")
    else:
        print("\n[apps_e2e_spine_certification] FAIL — strict-mode violations present")
    sys.exit(rc)
