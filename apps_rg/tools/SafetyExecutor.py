"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT define executor classes.

Original: apps_rg/tools/SafetyExecutor.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — SafetyExecutor class (runtime authority)

Importing this module raises RuntimeError immediately.
Core L2 owns all executors.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.tools.SafetyExecutor is QUARANTINED. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
