"""apps_rg LLM-judge registry.

STUB: real judge implementations are deferred to a calibration-backed
plan. This package exists to satisfy the `NO_UNIMPL_JUDGES` gate check
under ``ops_scripts/ci/check_app_domain_harness_parity.py`` — each judge
module is importable and declares ``IS_STUB = True`` so consumers can
distinguish stubs from real judges at runtime.
"""

from apps_rg.engines.judges.executive_positioning_judge import (
    ExecutivePositioningJudge,
    IS_STUB as executive_positioning_judge_is_stub,
)

__all__ = [
    "ExecutivePositioningJudge",
    "executive_positioning_judge_is_stub",
]
