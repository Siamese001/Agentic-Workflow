"""P6 (W3) — canonical name for the apps_rg prompt-assembly compiler.

``anthropic_rag_entrypoint.py`` was created under a misleading name that
implies C0 corpus retrieval ("RAG").  apps_rg performs NO corpus retrieval;
the prompt-assembly step builds an Anthropic Messages payload from a
preloaded PromptEnvelope, which is a "Prompt Assembly" operation (PA), not
a retrieval step.

This module is the canonical re-export surface.  All new callers MUST
import from here.  The original module is preserved unchanged as a compat
alias — do not edit or delete ``anthropic_rag_entrypoint.py``.

Plan: apps-rg-canonical-wireup-c8a4f2 W3 P6.
"""
from __future__ import annotations

from apps_rg.utils.anthropic_rag_entrypoint import (  # noqa: F401  (re-export)
    AbstainRecommendedError,
    AnthropicRagPayload,
    build_anthropic_rag_payload,
)

__all__ = [
    "AbstainRecommendedError",
    "AnthropicRagPayload",
    "build_anthropic_rag_payload",
]
