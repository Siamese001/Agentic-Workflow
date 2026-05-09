"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from agentic_core mixins.

Original: apps_rg/utils/rg_core_mixins.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — mixin imports from agentic_core (runtime authority)

Importing this module raises RuntimeError immediately.
Core owns all mixins.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/utils/rg_core_mixins.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.utils.rg_core_mixins is QUARANTINED. "
    "apps_rg may NOT import core mixins. "
    "Core owns all mixins. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
