"""Provider-neutral section model limits and identity for apps_rg generation.

Relocated from the retired ``qwen_vllm_health`` module (Qwen/vLLM removal). The
context-window budget (``SECTION_MODEL_MAX_MODEL_LEN``) preserves the historical
tuned value used by prompt-truncation budgeting; the model identity defaults to the
apps_rg external Claude generation model so prompt-render manifests and X2 model-name
proofs agree with the provider that actually serves section generation.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Final

# Tuned prompt-truncation budget (historical value preserved across the Qwen removal).
SECTION_MODEL_MAX_MODEL_LEN: Final[int] = int(os.getenv("APPS_RG_SECTION_MAX_MODEL_LEN", "24576"))

DEFAULT_EXTERNAL_CLAUDE_MODEL: Final[str] = "claude-haiku-4-5"


def external_claude_generation_model(environ: Mapping[str, str] | None = None) -> str:
    """Cost-optimized Claude generation model, preserving operator env override."""
    env = os.environ if environ is None else environ
    configured = str(env.get("APPS_RG_EXTERNAL_CLAUDE_MODEL") or "").strip()
    return configured or DEFAULT_EXTERNAL_CLAUDE_MODEL


# Canonical generation model identity for apps_rg sections. Matches the external Claude
# generation profile (``provider_profiles.yaml`` -> external_claude_generator) so the X2
# ``x2_model_name_allowed`` proof and prompt-render manifests reference the real provider model.
SECTION_MODEL_ID: Final[str] = external_claude_generation_model()

__all__ = [
    "DEFAULT_EXTERNAL_CLAUDE_MODEL",
    "SECTION_MODEL_ID",
    "SECTION_MODEL_MAX_MODEL_LEN",
    "external_claude_generation_model",
]
