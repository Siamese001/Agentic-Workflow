"""Provider-neutral section model limits and identity for apps_rg generation.

Relocated from the retired ``qwen_vllm_health`` module (Qwen/vLLM removal). The
context-window budget (``SECTION_MODEL_MAX_MODEL_LEN``) preserves the historical
tuned value used by prompt-truncation budgeting; the model identity defaults to the
apps_rg external Claude generation model so prompt-render manifests and X2 model-name
proofs agree with the provider that actually serves section generation.
"""
from __future__ import annotations

import os
from typing import Final

# Tuned prompt-truncation budget (historical value preserved across the Qwen removal).
SECTION_MODEL_MAX_MODEL_LEN: Final[int] = int(os.getenv("APPS_RG_SECTION_MAX_MODEL_LEN", "24576"))

# Canonical generation model identity for apps_rg sections. Matches the external Claude
# generation profile (``provider_profiles.yaml`` -> external_claude_generator) so the X2
# ``x2_model_name_allowed`` proof and prompt-render manifests reference the real provider model.
SECTION_MODEL_ID: Final[str] = os.getenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", "claude-sonnet-4-6")

__all__ = ["SECTION_MODEL_ID", "SECTION_MODEL_MAX_MODEL_LEN"]
