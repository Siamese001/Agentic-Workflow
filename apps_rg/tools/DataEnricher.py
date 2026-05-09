"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from L5 safety validators.

Original: apps_rg/tools/DataEnricher.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — L5 validator import (runtime authority)

Importing this module raises RuntimeError immediately.
Core L5 owns all validation.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/tools/DataEnricher.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.tools.DataEnricher is QUARANTINED. "
    "apps_rg may NOT import from L5 validators. "
    "Core L5 owns all validation. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
