"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from L5 runtime gates.

Original: apps_rg/integrations/gates/online_judges.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — L5 runtime gate import (runtime authority)

Importing this module raises RuntimeError immediately.
Core L5 owns all gates.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/integrations/gates/online_judges.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations.gates.online_judges is QUARANTINED. "
    "apps_rg may NOT import from L5 runtime gates. "
    "Core L5 owns all gates. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
