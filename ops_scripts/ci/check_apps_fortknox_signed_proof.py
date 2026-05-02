#!/usr/bin/env python3
"""W7 of plan apps-fort-knox-parity-c5d9a3 \u2014 apps_e2e Fort Knox CI gate.

Constitutional \u00a732 (apps_e2e arm). Runs the consolidated W6 generator
against the live apps_e2e Fort Knox surface and asserts every headline
gate passes:

  1. positive_control_status == "PASS"   (canary, APPS-REQ-001)
  2. trust_level \u2208 SIGNED-set
  3. signature_verification_status == "VERIFIED" (live re-verify)
  4. mutation_rejection.summary.accepted == 0 (zero accepts)
  5. blocked == 0 AND not_verified == 0
  6. live_signature_re_verify exit 0

The W6 generator already encodes these as `all_gates_pass`; this gate
re-runs the generator and reads the verdict. Re-running guarantees the
bundle reflects current on-disk state at commit time.

Fail-closed: exit 1 on any FAIL. Fail-open only via
`FORTKNOX_DISCIPLINE_BYPASS=1` (shared with the agentic_core arm).

Advisory rule: `.windsurf/rules/fortknox-certification-discipline.md`
+ plan `.windsurf/plans/apps-fort-knox-parity-c5d9a3.md` \u00a713\u2013\u00a718.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


GENERATOR_REL = "tools/certification/generate_apps_100pct_runtime_proof.py"
BUNDLE_REL = "artifacts/certification/apps_e2e/APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json"


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


def main() -> int:
    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        print("[check_apps_fortknox_signed_proof] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)")
        return 0

    repo = _repo_root()
    generator = repo / GENERATOR_REL
    bundle_path = repo / BUNDLE_REL

    if not generator.exists():
        print(
            f"[check_apps_fortknox_signed_proof] FATAL: generator missing at {generator}",
            file=sys.stderr,
        )
        return 2

    # Re-run the generator so the bundle reflects current on-disk state.
    proc = subprocess.run(
        [sys.executable, str(generator), "--quiet"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
        shell=False,
        timeout=180,
    )
    if proc.returncode not in (0, 2):
        # rc 0 = all gates pass; rc 2 = bundle written but gates failed.
        # Anything else = generator crashed or input missing.
        print(
            f"[check_apps_fortknox_signed_proof] FATAL: generator exit_code={proc.returncode}",
            file=sys.stderr,
        )
        if proc.stderr:
            print(proc.stderr.strip()[-1000:], file=sys.stderr)
        return 1

    if not bundle_path.exists():
        print(
            f"[check_apps_fortknox_signed_proof] FATAL: bundle missing at {bundle_path}",
            file=sys.stderr,
        )
        return 1

    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"[check_apps_fortknox_signed_proof] FATAL: bundle unreadable: {exc}",
            file=sys.stderr,
        )
        return 1

    h = bundle.get("headline_claims", {}) or {}
    failures: list[str] = []

    if not h.get("canary_pass"):
        failures.append(
            f"canary_pass={h.get('canary_pass')!r} (positive_control_status must be PASS)"
        )
    if not h.get("trust_in_signed_set"):
        failures.append(
            f"trust_level={h.get('trust_level')!r} not in SIGNED set"
        )
    if not h.get("signature_verified"):
        failures.append(
            f"signature_verification_status={h.get('signature_verification_status')!r} != VERIFIED"
        )
    if not h.get("live_signature_re_verify_passed"):
        failures.append(
            "live_signature_re_verify_passed=False (verifier exited non-zero)"
        )
    if not h.get("mutation_zero_accepts"):
        failures.append(
            "mutation_rejection.accepted > 0 (validator escaped a tampered scenario)"
        )
    if (h.get("row_blocked") or 0) > 0:
        failures.append(f"row_blocked={h.get('row_blocked')} > 0")
    if (h.get("row_not_verified") or 0) > 0:
        failures.append(f"row_not_verified={h.get('row_not_verified')} > 0")

    if failures or not h.get("all_gates_pass"):
        print(
            "[check_apps_fortknox_signed_proof] FAIL",
            file=sys.stderr,
        )
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        if not failures and not h.get("all_gates_pass"):
            print(
                "  - all_gates_pass=False (no per-gate failure surfaced; "
                "see bundle headline)",
                file=sys.stderr,
            )
        return 1

    print(
        f"[check_apps_fortknox_signed_proof] OK \u2014 "
        f"trust={h.get('trust_level')} "
        f"rows={h.get('row_signed_off')}+{h.get('row_signed_off_with_waiver')}/{h.get('row_total')} "
        f"apps={h.get('n_apps_certified')}+{h.get('n_apps_waived')}/{h.get('n_apps_total')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
