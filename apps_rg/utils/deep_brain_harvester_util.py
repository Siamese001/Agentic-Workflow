"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from L3 orchestration healers.

Original: apps_rg/utils/deep_brain_harvester_util.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — L3 orchestration healer import (runtime authority)

Importing this module raises RuntimeError immediately.
Core L3 owns all orchestration.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/utils/deep_brain_harvester_util.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.utils.deep_brain_harvester_util is QUARANTINED. "
    "apps_rg may NOT import from L3 orchestration. "
    "Core L3 owns orchestration. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
