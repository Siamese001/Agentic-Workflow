"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from L0, L1, L2, L3 core layers.

Original: apps_rg/utils/rg_agent_base_util.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Multiple core layer imports (runtime authority)

Importing this module raises RuntimeError immediately.
Core owns all agent base utilities.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/utils/rg_agent_base_util.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.utils.rg_agent_base_util is QUARANTINED. "
    "apps_rg may NOT import from core layers. "
    "Core owns agent base utilities. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
