"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain runtime authority code.

Original: apps_rg/scripts\_build_brief.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — scripts/ contains runtime authority

Importing this module raises RuntimeError immediately.
Core owns all runtime authority.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/scripts\_build_brief.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.scripts._build_brief is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core owns all runtime. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
