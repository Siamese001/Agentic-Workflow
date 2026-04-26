"""run_all_router_calibrations.py — Run all 10 per-router calibration scripts.

Constitutional §28. Generates one fresh weekly report per router under
``docs/reports/calibration/routers/<layer>_<router>/<YYYY-Www>.md``.

Usage:
    python ops_scripts/calibration/run_all_router_calibrations.py
    python ops_scripts/calibration/run_all_router_calibrations.py --json

Exit code:
    0 = all 10 reports generated (regardless of ledger availability)
    2 = at least one router failed to generate (rare; OS or path errors)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Bootstrap: support both `python -m ops_scripts.calibration.run_all_router_calibrations`
# AND `python ops_scripts/calibration/run_all_router_calibrations.py` invocations.
_REPO_ROOT_BOOTSTRAP = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_BOOTSTRAP))

from ops_scripts.calibration._router_calibration_base import (  # noqa: E402
    REPO_ROOT,
    GenerationResult,
    RouterCalibrationSpec,
    generate,
)

# Import each per-router SPEC. Keeping imports explicit (not via __all__ glob)
# so adding a new router is a deliberate one-line edit.
from ops_scripts.calibration.router_l0_bandit_calibration import SPEC as L0_BANDIT
from ops_scripts.calibration.router_l0_r5_calibration import SPEC as L0_R5
from ops_scripts.calibration.router_l1_c0_calibration import SPEC as L1_C0
from ops_scripts.calibration.router_l2_cascade_calibration import SPEC as L2_CASCADE
from ops_scripts.calibration.router_l3_reroute_calibration import SPEC as L3_REROUTE
from ops_scripts.calibration.router_l3_shape_calibration import SPEC as L3_SHAPE
from ops_scripts.calibration.router_l4_uwg_calibration import SPEC as L4_UWG
from ops_scripts.calibration.router_l5_hitl_calibration import SPEC as L5_HITL
from ops_scripts.calibration.router_l6_promo_calibration import SPEC as L6_PROMO
from ops_scripts.calibration.router_l6_regret_calibration import SPEC as L6_REGRET

ALL_SPECS: tuple[RouterCalibrationSpec, ...] = (
    L0_BANDIT, L0_R5,
    L1_C0,
    L2_CASCADE,
    L3_SHAPE, L3_REROUTE,
    L4_UWG,
    L5_HITL,
    L6_PROMO, L6_REGRET,
)


def run_all() -> tuple[list[GenerationResult], list[tuple[str, str]]]:
    """Generate every router's weekly report.

    Returns (successes, failures). ``failures`` is a list of (router_key, error).
    """
    successes: list[GenerationResult] = []
    failures: list[tuple[str, str]] = []
    for spec in ALL_SPECS:
        try:
            successes.append(generate(spec))
        except (OSError, ValueError) as exc:
            failures.append((spec.key, str(exc)))
    return successes, failures


def _print_text(successes: list[GenerationResult], failures: list[tuple[str, str]]) -> None:
    print(f"[router-calibration] Generated {len(successes)}/{len(ALL_SPECS)} reports")
    for r in successes:
        rel = r.output_path.relative_to(REPO_ROOT).as_posix()
        flag = "live" if r.available else "awaiting"
        print(f"  ✓ {r.spec_key}: {rel} ({r.bytes_written}B, {flag})")
    for key, err in failures:
        print(f"  ✗ {key}: {err}")


def _print_json(successes: list[GenerationResult], failures: list[tuple[str, str]]) -> None:
    payload = {
        "successes": [
            {
                "spec_key": r.spec_key,
                "output_path": r.output_path.relative_to(REPO_ROOT).as_posix(),
                "bytes_written": r.bytes_written,
                "available": r.available,
            }
            for r in successes
        ],
        "failures": [{"spec_key": k, "error": e} for k, e in failures],
        "total_specs": len(ALL_SPECS),
    }
    print(json.dumps(payload, indent=2))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = p.parse_args(argv)

    successes, failures = run_all()
    if args.json:
        _print_json(successes, failures)
    else:
        _print_text(successes, failures)
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
