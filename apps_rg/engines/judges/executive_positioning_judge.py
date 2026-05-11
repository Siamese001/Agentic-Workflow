"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain runtime authority code.

Original: apps_rg/engines\judges\executive_positioning_judge.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — engines/ contains runtime authority

Importing this module raises RuntimeError immediately.
Core owns all runtime authority.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/engines\judges\executive_positioning_judge.py.ORIGINAL
"""

# DO_NOT_IMPORT_FROM_CORE_RUNTIME
# Machine-checkable sentinel for W2 quarantine-guard tests and CI grep proofs.
# Any agentic_core active runtime module that imports executive_positioning_judge
# as a live runtime authority is a QUARANTINE VIOLATION (AG-RGGOV-8).

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.engines.judges.executive_positioning_judge is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core owns all runtime. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
