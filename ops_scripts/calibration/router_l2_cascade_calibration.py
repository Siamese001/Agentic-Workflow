"""router_l2_cascade_calibration.py — Weekly calibration for L2/cascade router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L2_cascade/<YYYY-Www>.md
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
    layer="L2",
    router="cascade",
    purpose="Cost-aware execution cascade; EU + Brier; 3-provider tier excludes.",
    nominal_thresholds={
        "expected_utility_min": 0.65,
        "brier_max": 0.20,
        "tier_skip_rate_max": 0.05,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
