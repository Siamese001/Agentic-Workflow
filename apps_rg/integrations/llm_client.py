"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain LLM client integrations or provider calls.

Original: apps_rg/integrations/llm_client.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Direct LLM client (provider authority)

Importing this module raises RuntimeError immediately.
Core L2 Execution owns all provider calls through SovereignLLMGateway.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/integrations/llm_client.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations.llm_client is QUARANTINED. "
    "apps_rg may NOT make provider calls. "
    "Core L2 Execution owns provider calls. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
