"""router_l6_regret_calibration.py — Weekly calibration for L6/regret router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L6_regret/<YYYY-Www>.md

Hard floor (constitutional §28): every regret cycle MUST emit non-empty
by_layer_json. A cycle without per-layer attribution teaches nothing.
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
    router="regret",
    purpose="Regret accounting; per-decision + by-layer attribution; top offender feed.",
    nominal_thresholds={
        "by_layer_json_required": 1.0,
        "regret_value_max_per_cycle": 0.30,
        "min_decisions_per_cycle": 10,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
