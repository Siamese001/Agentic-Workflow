"""router_l3_reroute_calibration.py — Weekly calibration for L3/reroute router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L3_reroute/<YYYY-Www>.md
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
    layer="L3",
    router="reroute",
    purpose="Reroute governance; ceiling + disagreement + cert; blocks d2,d4 on alarm.",
    nominal_thresholds={
        "ceiling_band_max": 0.85,
        "disagree_count_max": 2,
        "cert_required_share_min": 0.95,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
