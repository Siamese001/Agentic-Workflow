"""router_l0_r5_calibration.py — Weekly calibration for L0/r5 reason-router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L0_r5/<YYYY-Www>.md
"""

from __future__ import annotations

import sys

from ops_scripts.calibration._router_calibration_base import (
    RouterCalibrationSpec,
    cli,
)

SPEC = RouterCalibrationSpec(
    layer="L0",
    router="r5",
    purpose="R5 reason-code router; Brier score per reason; demotes toxicity_flagged.",
    nominal_thresholds={
        "brier_max": 0.15,
        "min_decisions_per_reason": 20,
        "demote_fp_rate_max": 0.10,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
