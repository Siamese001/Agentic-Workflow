"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from agent specs (runtime authority).

Original: apps_rg/config/__init__.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Imports from agent_spec_config (runtime authority)

Importing this module raises RuntimeError immediately.
Core owns all agent configuration.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.config is QUARANTINED. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
