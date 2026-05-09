"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT orchestrate user preferences.

Original: apps_rg/engines/user_preferences_engine.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — L3 orchestration logic (runtime authority)

Importing this module raises RuntimeError immediately.
Core L3 Orchestration owns all workflow orchestration.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/engines/user_preferences_engine.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.engines.user_preferences_engine is QUARANTINED. "
    "apps_rg may NOT orchestrate workflow steps. "
    "Core L3 Orchestration owns workflow orchestration. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
