"""router_l6_promo_calibration.py — Weekly calibration for L6/promo router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L6_promo/<YYYY-Www>.md

Hard floor (constitutional §28): verdict=promote requires ALL of
wilson_lower≥0.60, z_score≥1.96, uplift>0, n≥30. Calibration here
tracks how often each candidate clears that bar.
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
    layer="L6",
    router="promo",
    purpose="Flywheel promoter; Wilson + z + uplift evidence floor; promote/rollback.",
    nominal_thresholds={
        "wilson_lower_min": 0.60,
        "z_score_min": 1.96,
        "uplift_min": 0.0,
        "n_min": 30,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
