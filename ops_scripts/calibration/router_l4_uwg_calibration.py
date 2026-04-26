"""router_l4_uwg_calibration.py — Weekly calibration for L4/uwg router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L4_uwg/<YYYY-Www>.md
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
    layer="L4",
    router="uwg",
    purpose="Unified write gateway router; class + miss + atomic; 2nd-judge gate.",
    nominal_thresholds={
        "atomic_share_min": 0.99,
        "miss_count_max": 0,
        "second_judge_fire_share_min": 0.50,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
