"""Shared constants and helpers for core v10.7."""
from __future__ import annotations

LEGACY_MODEL_ALIASES = {
    "gemini-2.5-pro": "gemini-pro",
    "gemini-2.5-flash": "gemini-flash",
}

LEGACY_MODEL_REVERSE = {alias: original for original, alias in LEGACY_MODEL_ALIASES.items()}


def legacy_model_alias(model_name: str) -> str:
    """Return the canonical alias for legacy Gemini model names."""

    return LEGACY_MODEL_ALIASES.get(model_name, model_name)


def canonical_model_name(model_name: str) -> str:
    """Map aliased model names back to the canonical identifier."""

    return LEGACY_MODEL_REVERSE.get(model_name, model_name)


__all__ = [
    "LEGACY_MODEL_ALIASES",
    "LEGACY_MODEL_REVERSE",
    "legacy_model_alias",
    "canonical_model_name",
]
