"""L0 routing calibration harness (Wave W0 — plan l0-routing-calibration-gap-audit-b3c9d4).

Exports:
    ``threshold_sweep`` — PR-curve sweep + optimal-threshold selection.
    ``feature_vector`` — canonical per-path calibration signal contract.
"""

from tools.calibration.feature_vector import (
    CalibrationFixture,
    FixtureRecord,
    PathSignal,
    load_fixture,
)
from tools.calibration.threshold_sweep import (
    PRPoint,
    SweepReport,
    select_optimal_threshold,
    sweep_thresholds,
)

__all__ = [
    "CalibrationFixture",
    "FixtureRecord",
    "PRPoint",
    "PathSignal",
    "SweepReport",
    "load_fixture",
    "select_optimal_threshold",
    "sweep_thresholds",
]
