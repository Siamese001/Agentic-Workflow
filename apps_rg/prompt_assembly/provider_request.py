"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT provide runtime artifact conversion functions.

Original: apps_rg/prompt_assembly/provider_request.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — artifact_to_provider_request function (runtime authority)

Importing this module raises RuntimeError immediately.
Core owns all provider request assembly.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.prompt_assembly.provider_request is QUARANTINED. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
