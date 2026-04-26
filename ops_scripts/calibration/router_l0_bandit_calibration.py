"""router_l0_bandit_calibration.py — Weekly calibration for L0/bandit router.

Constitutional §28. Rule: closed-loop-router-enforcement.md.
Output: docs/reports/calibration/routers/L0_bandit/<YYYY-Www>.md
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
    layer="L0",
    router="bandit",
    purpose="Thompson-sampled namespace bandit; per-NS posterior α/β replay.",
    nominal_thresholds={
        "min_decisions_per_ns": 30,
        "posterior_min_alpha": 1.0,
        "posterior_min_beta": 1.0,
        "thompson_samples_per_call": 5000,
    },
)


if __name__ == "__main__":
    sys.exit(cli(SPEC, sys.argv[1:]))
