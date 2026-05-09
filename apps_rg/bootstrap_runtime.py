"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT define runtime bootstrap, agent contracts, or provider classes.

Original: apps_rg/bootstrap_runtime.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — AgentOutputContract, ProviderValue, Provider classes + bootstrap

Importing this module raises RuntimeError immediately.
Core owns all runtime initialization.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.bootstrap_runtime is QUARANTINED. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
