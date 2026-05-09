"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import openai, anthropic, or google provider SDKs.

Original: apps_rg/integrations/hops/_llm_client.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Direct provider SDK imports (openai, anthropic, google)

Importing this module raises RuntimeError immediately.
Core L2 owns all provider calls through SovereignLLMGateway.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/integrations/hops/_llm_client.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations.hops._llm_client is QUARANTINED. "
    "apps_rg may NOT import provider SDKs. "
    "Core L2 owns all provider calls. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
