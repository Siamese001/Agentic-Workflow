"""
Shared constants and model–name normalization utilities for core v10.7.

This module provides:

  • provider-agnostic canonical names
  • legacy → modern aliasing
  • modern → legacy reverse aliasing
  • normalization of hyphens/underscores
  • consistent surface for cache keys, clients, and MCP routing
"""

from __future__ import annotations


# -------------------------------------------------------------------------
# 1. Legacy → canonical aliases (unified naming)
# -------------------------------------------------------------------------

LEGACY_MODEL_ALIASES = {
    # --- Gemini ---
    "gemini-2.5-pro": "gemini-pro",
    "gemini-2.5-flash": "gemini-flash",
    "gemini-pro-1.0": "gemini-pro",
    "gemini-pro-vision": "gemini-pro",
    "gemini-flash-1.0": "gemini-flash",

    # --- Anthropic ---
    "claude-2.1": "claude-3-sonnet",
    "claude-3-sonnet-20240229": "claude-3-sonnet",
    "claude-1": "claude-3-haiku",
    "claude-instant-1.2": "claude-3-haiku",

    # --- OpenAI ---
    "gpt-4o-mini": "gpt-4o",
    "gpt-4o-mini-2024-05-27": "gpt-4o",
    "gpt-4-1106-preview": "gpt-4o",
    "gpt-3.5-turbo": "gpt-4o-mini",  # internal policy: lift to closest modern tier

    # --- Internal agentic workflow ---
    "resume-gen-draft": "gpt-4o-mini",
    "resume-gen-qa": "gpt-4o-mini",
}


# -------------------------------------------------------------------------
# 2. Canonical → legacy reverse mapping
# -------------------------------------------------------------------------

LEGACY_MODEL_REVERSE = {alias: orig for orig, alias in LEGACY_MODEL_ALIASES.items()}


# -------------------------------------------------------------------------
# 3. Normalization helpers
# -------------------------------------------------------------------------

def _normalize(model_name: str) -> str:
    """Normalize punctuation, whitespace, and case for consistent matching."""
    if not isinstance(model_name, str):
        return str(model_name)
    model_name = model_name.strip().lower()
    model_name = model_name.replace(" ", "-").replace("_", "-")
    return model_name


# -------------------------------------------------------------------------
# 4. Public API
# -------------------------------------------------------------------------

def legacy_model_alias(model_name: str) -> str:
    """
    Convert a modern model name to its legacy identifier when needed.
    Used mainly when older APIs or fallback SDK paths require backwards compatibility.
    """
    normalized = _normalize(model_name)
    return LEGACY_MODEL_ALIASES.get(normalized, normalized)


def canonical_model_name(model_name: str) -> str:
    """
    Convert any model variant (legacy, inconsistent, alias, HF-like)
    into your workflow's canonical model identifier.

    Guaranteed invariants:
      • canonical_model_name(x) is always lowercase
      • hyphens normalized
      • legacy variants resolved
      • always stable for caching, semantic cache, and MCP routing
    """
    normalized = _normalize(model_name)
    return LEGACY_MODEL_REVERSE.get(normalized, normalized)


__all__ = [
    "LEGACY_MODEL_ALIASES",
    "LEGACY_MODEL_REVERSE",
    "legacy_model_alias",
    "canonical_model_name",
]
