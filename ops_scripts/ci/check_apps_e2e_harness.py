"""[DEPRECATED 2026-05-02] CI gate for the apps_e2e auditability harness.

This gate is kept as a backward-compatible shim. Two-gate certification
splits its responsibility into:

  - check_apps_e2e_bundle_emission.py  — must pass; smoke mode
  - check_apps_e2e_spine_certification.py — informational at first; strict mode

Run:
    python -m ops_scripts.ci.check_apps_e2e_harness

Exit 0 = pass (legacy semantics: existing bundles + matrix freshness),
       2 = harness regression detected.

The shim also emits a DeprecationWarning to stderr to alert callers to
migrate to the two new gates.
"""
from __future__ import annotations

import warnings as _warnings  # noqa: E402

_warnings.warn(
    "check_apps_e2e_harness is deprecated; use check_apps_e2e_bundle_emission "
    "(must-pass) and check_apps_e2e_spine_certification (informational) instead. "
    "See plan apps-e2e-two-gate-certification-d8b3a1.",
    DeprecationWarning,
    stacklevel=2,
)

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.apps_e2e.app_specs import APP_SPECS  # noqa: E402
from tools.certification.apps_e2e.matrix_builder import build_matrix  # noqa: E402
from tools.certification.apps_e2e.paths import MATRIX_PATH, AppCertPaths  # noqa: E402
from tools.certification.apps_e2e.shared_verifier import (  # noqa: E402
    Violation, format_violation, verify_bundle,
)


def _check_bundles() -> list[str]:
    failures: list[str] = []
    for spec in APP_SPECS:
        paths = AppCertPaths(spec.app_name)
        if not paths.proof_bundle.exists():
            continue  # not yet emitted; not a CI failure (matrix will mark not_run)
        try:
            bundle = json.loads(paths.proof_bundle.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{spec.app_name}: bundle unreadable: {exc}")
            continue
        violations: list[Violation] = verify_bundle(bundle, spec)
        if violations:
            for v in violations:
                failures.append(f"{spec.app_name}: {format_violation(v)}")
    return failures


def _check_matrix_freshness() -> list[str]:
    """If the matrix exists on disk, it must agree with build_matrix() now."""
    if not MATRIX_PATH.exists():
        return []
    try:
        persisted = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"matrix unreadable: {exc}"]
    fresh = build_matrix()
    if {r["app_name"] for r in persisted["apps"]} != {r["app_name"] for r in fresh["apps"]}:
        return ["matrix drift: app set differs from registry"]
    persisted_status = {r["app_name"]: r["agentic_core_spine_status"] for r in persisted["apps"]}
    fresh_status = {r["app_name"]: r["agentic_core_spine_status"] for r in fresh["apps"]}
    if persisted_status != fresh_status:
        diffs = [
            f"{k}: persisted={persisted_status[k]} fresh={fresh_status[k]}"
            for k in fresh_status if persisted_status.get(k) != fresh_status[k]
        ]
        return [f"matrix drift: spine_status differs: {diffs}"]
    return []


def main() -> int:
    failures: list[str] = []
    failures.extend(_check_bundles())
    failures.extend(_check_matrix_freshness())
    if failures:
        print("[apps_e2e_harness_gate] FAIL")
        for f in failures:
            print(f"  - {f}")
        return 2
    print(f"[apps_e2e_harness_gate] OK ({len(APP_SPECS)} specs registered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
