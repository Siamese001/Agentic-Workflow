"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/engines\judges\__init__.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.engines\judges\__init__ is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/engines\judges\__init__.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """apps_rg LLM-judge registry.
# 
# STUB: real judge implementations are deferred to a calibration-backed
# plan. This package exists to satisfy the `NO_UNIMPL_JUDGES` gate check
# under ``ops_scripts/ci/check_app_domain_harness_parity.py`` — each judge
# module is importable and declares ``IS_STUB = True`` so consumers can
# distinguish stubs from real judges at runtime.
# """
# 
# from apps_rg.engines.judges.executive_positioning_judge import (
#     ExecutivePositioningJudge,
#     IS_STUB as executive_positioning_judge_is_stub,
# )
# 
# __all__ = [
#     "ExecutivePositioningJudge",
#     "executive_positioning_judge_is_stub",
# ]
# 