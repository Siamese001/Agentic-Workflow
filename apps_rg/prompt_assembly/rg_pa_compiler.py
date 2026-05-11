"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/prompt_assembly\rg_pa_compiler.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

# DO_NOT_IMPORT_FROM_CORE_RUNTIME
# Machine-checkable sentinel for W2 quarantine-guard tests and CI grep proofs.
# Any agentic_core active runtime module that imports from apps_rg.prompt_assembly.rg_pa_compiler
# is a QUARANTINE VIOLATION (AG-RGGOV-8).

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.prompt_assembly.rg_pa_compiler is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/prompt_assembly\rg_pa_compiler.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """P6 (W3) — canonical name for the apps_rg prompt-assembly compiler.
# 
# ``anthropic_rag_entrypoint.py`` was created under a misleading name that
# implies C0 corpus retrieval ("RAG").  apps_rg performs NO corpus retrieval;
# the prompt-assembly step builds an Anthropic Messages payload from a
# preloaded PromptEnvelope, which is a "Prompt Assembly" operation (PA), not
# a retrieval step.
# 
# This module is the canonical re-export surface.  All new callers MUST
# import from here.  The original module is preserved unchanged as a compat
# alias — do not edit or delete ``anthropic_rag_entrypoint.py``.
# 
# Plan: apps-rg-canonical-wireup-c8a4f2 W3 P6.
# """
# from __future__ import annotations
# 
# from apps_rg.utils.anthropic_rag_entrypoint import (  # noqa: F401  (re-export)
#     AbstainRecommendedError,
#     AnthropicRagPayload,
#     build_anthropic_rag_payload,
# )
# 
# __all__ = [
#     "AbstainRecommendedError",
#     "AnthropicRagPayload",
#     "build_anthropic_rag_payload",
# ]
# 