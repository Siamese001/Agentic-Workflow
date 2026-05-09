"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from agentic_core knowledge retrieval or define RAG payloads.

Original: apps_rg/utils/anthropic_rag_entrypoint.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — C0/RAG imports + AnthropicRagPayload class (runtime authority)

Importing this module raises RuntimeError immediately.
Core C0 owns all RAG/retrieval.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/utils/anthropic_rag_entrypoint.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.utils.anthropic_rag_entrypoint is QUARANTINED. "
    "apps_rg may NOT import from core retrieval. "
    "Core C0 owns all RAG. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
