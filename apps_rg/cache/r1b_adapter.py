"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from L4 state management.

Original: apps_rg/cache/r1b_adapter.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — L4_state.semantic_cache_manager import (runtime authority)

Importing this module raises RuntimeError immediately.
Core L4 owns all state management.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.cache.r1b_adapter is QUARANTINED. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
