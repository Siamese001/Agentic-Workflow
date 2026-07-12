"""Canonical provider aliases for the apps_rg governed L2 envelope."""
from __future__ import annotations

from typing import Final


_PROVIDER_ALIASES: Final[dict[str, str]] = {
    "anthropic": "anthropic",
    "claude": "anthropic",
    "external_claude": "anthropic",
    "external_anthropic": "anthropic",
    "openai": "openai",
    "gpt": "openai",
    "azure_openai": "openai",
    "external_openai": "openai",
    "google": "google_gemini",
    "gemini": "google_gemini",
    "google_gemini": "google_gemini",
    "external_gemini": "google_gemini",
    "external_google_gemini": "google_gemini",
    "local_local_model_server": "local_local_model_server",
    "local_model_server": "local_local_model_server",
    "local_vllm": "local_local_model_server",
    "vllm": "local_local_model_server",
    "local": "local_local_model_server",
    "stub": "stub",
    "stub_only": "stub",
    "mock": "stub",
    "test": "stub",
}

_EXTERNAL_CANONICAL: Final[frozenset[str]] = frozenset(
    {"anthropic", "openai", "google_gemini"}
)
_LOCAL_OR_STUB_CANONICAL: Final[frozenset[str]] = frozenset(
    {"local_local_model_server", "stub"}
)


def normalize_apps_rg_provider_alias(value: str) -> str:
    """Return the canonical provider key, preserving unknown values for rejection."""
    raw = str(value or "").strip().lower()
    return _PROVIDER_ALIASES.get(raw, raw)


def is_external_apps_rg_provider(value: str) -> bool:
    return normalize_apps_rg_provider_alias(value) in _EXTERNAL_CANONICAL


def is_local_or_stub_apps_rg_provider(value: str) -> bool:
    return normalize_apps_rg_provider_alias(value) in _LOCAL_OR_STUB_CANONICAL


__all__ = [
    "is_external_apps_rg_provider",
    "is_local_or_stub_apps_rg_provider",
    "normalize_apps_rg_provider_alias",
]
