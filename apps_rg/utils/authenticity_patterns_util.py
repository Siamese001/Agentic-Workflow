"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT define authenticity pattern utilities with runtime logic.

Original: apps_rg/utils/authenticity_patterns_util.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Utility with embedded runtime examples (runtime authority)

Importing this module raises RuntimeError immediately.
Core utilities own helper functions.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/utils/authenticity_patterns_util.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.utils.authenticity_patterns_util is QUARANTINED. "
    "apps_rg may NOT define runtime utilities. "
    "Core utilities own helper functions. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
