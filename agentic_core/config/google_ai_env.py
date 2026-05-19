"""Canonical Google AI environment variable resolution (SSOT).

Canonical names (use in ``.env``):

- ``GOOGLE_API_KEY``
- ``GOOGLE_AI_MODEL`` (flash / fast tier)
- ``GOOGLE_AI_PRO_MODEL`` (pro / reasoning tier)
- ``GOOGLE_AI_MAX_OUTPUT_TOKENS``

Deprecated aliases (read-only fallback, do not set in new ``.env`` files):

- ``GEMINI_API_KEY``, ``GEMINI_MODEL``, ``GEMINI_PRO_MODEL``, ``GEMINI_MAX_OUTPUT_TOKENS``
"""

from __future__ import annotations

import os
from typing import Final, Mapping

GOOGLE_API_KEY: Final[str] = "GOOGLE_API_KEY"
GEMINI_API_KEY_LEGACY: Final[str] = "GEMINI_API_KEY"

GOOGLE_AI_MODEL: Final[str] = "GOOGLE_AI_MODEL"
GEMINI_MODEL_LEGACY: Final[str] = "GEMINI_MODEL"

GOOGLE_AI_PRO_MODEL: Final[str] = "GOOGLE_AI_PRO_MODEL"
GEMINI_PRO_MODEL_LEGACY: Final[str] = "GEMINI_PRO_MODEL"

GOOGLE_AI_MAX_OUTPUT_TOKENS: Final[str] = "GOOGLE_AI_MAX_OUTPUT_TOKENS"
GEMINI_MAX_OUTPUT_TOKENS_LEGACY: Final[str] = "GEMINI_MAX_OUTPUT_TOKENS"

# Healing-only override (asymmetric from judge panel); legacy name retained as fallback.
HEALING_GOOGLE_AI_PRO_MODEL: Final[str] = "HEALING_GOOGLE_AI_PRO_MODEL"
HEALING_GEMINI_PRO_MODEL_LEGACY: Final[str] = "HEALING_GEMINI_MODEL"


def _env_map(environ: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def resolve_env_str(
    environ: Mapping[str, str] | None,
    *keys: str,
    default: str = "",
) -> tuple[str, str]:
    """Return ``(value, winning_key)`` for the first non-empty key in *keys*."""
    env = _env_map(environ)
    for key in keys:
        raw = str(env.get(key) or "").strip()
        if raw:
            return raw, key
    return default, ""


def google_api_key(environ: Mapping[str, str] | None = None) -> tuple[str, str]:
    return resolve_env_str(environ, GOOGLE_API_KEY, GEMINI_API_KEY_LEGACY)


def google_ai_flash_model_id(
    environ: Mapping[str, str] | None = None,
    *,
    default: str = "gemini-3-flash-preview",
) -> tuple[str, str]:
    return resolve_env_str(
        environ,
        GOOGLE_AI_MODEL,
        GEMINI_MODEL_LEGACY,
        "GEMINI_FLASH_MODEL",  # legacy healing override name
        default=default,
    )


def google_ai_pro_model_id(
    environ: Mapping[str, str] | None = None,
    *,
    default: str = "gemini-3.1-pro-preview",
) -> tuple[str, str]:
    return resolve_env_str(
        environ,
        GOOGLE_AI_PRO_MODEL,
        GEMINI_PRO_MODEL_LEGACY,
        default=default,
    )


def google_ai_max_output_tokens(
    environ: Mapping[str, str] | None = None,
    *,
    default: int = 4096,
) -> int:
    raw, _ = resolve_env_str(
        environ,
        GOOGLE_AI_MAX_OUTPUT_TOKENS,
        GEMINI_MAX_OUTPUT_TOKENS_LEGACY,
        default=str(default),
    )
    try:
        return int(raw)
    except ValueError:
        return default


def healing_google_ai_pro_model_id(
    environ: Mapping[str, str] | None = None,
    *,
    registry_default: str,
) -> tuple[str, str]:
    return resolve_env_str(
        environ,
        HEALING_GOOGLE_AI_PRO_MODEL,
        HEALING_GEMINI_PRO_MODEL_LEGACY,
        default=registry_default,
    )


__all__ = [
    "GEMINI_API_KEY_LEGACY",
    "GEMINI_MAX_OUTPUT_TOKENS_LEGACY",
    "GEMINI_MODEL_LEGACY",
    "GEMINI_PRO_MODEL_LEGACY",
    "GOOGLE_AI_MAX_OUTPUT_TOKENS",
    "GOOGLE_AI_MODEL",
    "GOOGLE_AI_PRO_MODEL",
    "GOOGLE_API_KEY",
    "HEALING_GEMINI_PRO_MODEL_LEGACY",
    "HEALING_GOOGLE_AI_PRO_MODEL",
    "google_ai_flash_model_id",
    "google_ai_max_output_tokens",
    "google_ai_pro_model_id",
    "google_api_key",
    "healing_google_ai_pro_model_id",
    "resolve_env_str",
]
