"""router_l3_shape_calibration.py — Weekly calibration for L3/shape router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L3_shape/<YYYY-Www>.md
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
    router="shape",
    purpose="Workflow shape router; iter caps 3/7/5; p95 + amplitude + skip telemetry.",
    nominal_thresholds={
        "iter_cap_class_a": 3,
        "iter_cap_class_b": 7,
        "iter_cap_class_c": 5,
        "p95_latency_ms_max": 4000,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
