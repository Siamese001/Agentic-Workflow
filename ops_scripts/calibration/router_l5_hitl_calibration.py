"""router_l5_hitl_calibration.py — Weekly calibration for L5/hitl router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L5_hitl/<YYYY-Www>.md

Note: this is the runtime HITL exit-control router (per ADR-023), NOT the
developer-loop Author-Gate. Calibration tracks per-reason FP rate + escape
rate; demotes pii_leak when FP > threshold.
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
    layer="L5",
    router="hitl",
    purpose="Runtime HITL exit-control (ADR-023); per-reason FP rate + escape rate.",
    nominal_thresholds={
        "fp_rate_max": 0.05,
        "escape_rate_max": 0.01,
        "pii_leak_demote_threshold": 0.02,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
