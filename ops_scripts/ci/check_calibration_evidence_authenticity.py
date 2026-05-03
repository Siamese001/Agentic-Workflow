"""CI gate: judge calibration evidence authenticity.

Plan: `.windsurf/plans/judge-spearman-calibration-a7e4c9.md`.
Author-Gate: `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine).

Enforces: `artifacts/calibration/judge_spearman.json` MUST NOT claim
`meets_threshold: true` while ANY result row carries
`is_synthetic_smoke: true`. This prevents the synthetic scaffold from
ever being misread as production-ready calibration evidence.

If the artifact file is missing, the gate is OK (calibration not yet
run). The gate fires only when authenticity violations are present.

Bypass: `CALIBRATION_AUTHENTICITY_BYPASS=1` (logged).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = REPO_ROOT / "artifacts" / "calibration" / "judge_spearman.json"


def check(artifact_path: Path = DEFAULT_ARTIFACT) -> int:
    if os.getenv("CALIBRATION_AUTHENTICITY_BYPASS") == "1":
        print("[check_calibration_evidence_authenticity] BYPASS=1 — gate disabled", file=sys.stderr)
        return 0
    if not artifact_path.is_file():
        print(f"[check_calibration_evidence_authenticity] OK — no artifact at {artifact_path}")
        return 0

    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(
            f"[check_calibration_evidence_authenticity] FAIL — artifact unparseable: {exc}",
            file=sys.stderr,
        )
        return 1

    results = payload.get("results") or []
    if not isinstance(results, list):
        print(
            f"[check_calibration_evidence_authenticity] FAIL — 'results' must be a list",
            file=sys.stderr,
        )
        return 1

    violations: list[str] = []
    any_synthetic = False
    any_meets = False
    for r in results:
        synth = bool(r.get("is_synthetic_smoke"))
        meets = bool(r.get("meets_threshold"))
        any_synthetic = any_synthetic or synth
        any_meets = any_meets or meets
        if synth and meets:
            violations.append(
                f"  - {r.get('judge_id')}: is_synthetic_smoke=true AND meets_threshold=true (forbidden combination)"
            )

    # Also check the rollup flags for consistency.
    rollup_synth = bool(payload.get("any_synthetic_smoke"))
    rollup_meets = bool(payload.get("all_meet_threshold"))
    if rollup_synth and rollup_meets:
        violations.append(
            f"  - rollup: any_synthetic_smoke=true AND all_meet_threshold=true (forbidden combination)"
        )

    if violations:
        print("[check_calibration_evidence_authenticity] FAIL:", file=sys.stderr)
        for v in violations:
            print(v, file=sys.stderr)
        print(
            "\nFix: synthetic calibration runs MUST report meets_threshold=false. "
            "If the calibration module's SYNTHETIC guard was bypassed, restore it. "
            "If real human-labeled corpus exists, flip row tags to RELEASE_GATE "
            "and rerun calibration.\nDoctrine: judge-spearman-calibration-a7e4c9 + "
            "Author-Gate dec_19dedcd1c109ebf25.\n"
            "Bypass: CALIBRATION_AUTHENTICITY_BYPASS=1 (logged).",
            file=sys.stderr,
        )
        return 1

    print(
        f"[check_calibration_evidence_authenticity] OK — {len(results)} judges; "
        f"synthetic_any={any_synthetic} meets_any={any_meets} (no false-claim combination)"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Calibration evidence authenticity gate")
    p.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    args = p.parse_args(argv)
    return check(args.artifact)


if __name__ == "__main__":
    sys.exit(main())
