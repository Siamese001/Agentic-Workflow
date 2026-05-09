"""
QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This directory is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain runtime hop runners, judges, ensembles, or LLM clients.

Any import from this package immediately raises RuntimeError.
Core L2/L3 owns all execution orchestration. apps_rg is ingress-only.

See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19
"""

# AG-RGGOV-8: Immediate RuntimeError on package import
raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations.hops is QUARANTINED. "
    "apps_rg may NOT contain runtime hop runners, judges, ensembles, or LLM clients. "
    "Core L2/L3 owns execution orchestration. "
    "apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
