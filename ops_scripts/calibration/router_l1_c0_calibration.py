"""router_l1_c0_calibration.py — Weekly calibration for L1/c0 context router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L1_c0/<YYYY-Www>.md
"""

from __future__ import annotations

import sys

from ops_scripts.calibration._router_calibration_base import (
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
