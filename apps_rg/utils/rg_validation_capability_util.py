"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import lifecycle trace contracts.

Original: apps_rg/utils/rg_validation_capability_util.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — lifecycle_trace_contract import (L6 authority)

Importing this module raises RuntimeError immediately.
Core L6 owns all trace contracts.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/utils/rg_validation_capability_util.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.utils.rg_validation_capability_util is QUARANTINED. "
    "apps_rg may NOT import trace contracts. "
    "Core L6 owns all trace contracts. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
