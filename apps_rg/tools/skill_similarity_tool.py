"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import lifecycle trace contracts.

Original: apps_rg/tools/skill_similarity_tool.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — lifecycle_trace_contract imports (L6 authority)

Importing this module raises RuntimeError immediately.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.tools.skill_similarity_tool is QUARANTINED. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
