"""router_l1_c0_calibration.py — Weekly calibration for L1/c0 context router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L1_c0/<YYYY-Www>.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT_BOOTSTRAP = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_BOOTSTRAP))

from ops_scripts.calibration._router_calibration_base import (  # noqa: E402
    RouterCalibrationSpec,
    cli,
)

SPEC = RouterCalibrationSpec(
    layer="L1",
    router="c0",
    purpose="C0 context retrieval router; mode/k/coverage selection feeds bandit posterior.",
    nominal_thresholds={
        "coverage_min": 0.80,
        "k_default": 3,
        "mode_hybrid_share_min": 0.50,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
