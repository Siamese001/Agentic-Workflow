"""SSOT char/token limits for executive_summary @ 24k (VLLM_MAX_MODEL_LEN=24576).

Char limits are code constants only — not env-overridable. ``available_input_tokens`` and
``apply_executive_summary_token_budget_policy`` are the operator-visible gates.
"""

from __future__ import annotations

import os

# No preventive char cap when the compiled prompt already fits (token budget is authority).
TARGETING_NO_GAP_MAX_CHARS: int = 10_000_000

# Bullet-pool Claude selector sub-prompt (code constant).
DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS: int = 6_000
DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS: int = 6_000

# --- Token budget (Qwen / vLLM) — output caps env-overridable; first-pass 92% is fixed ---
DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS: int = 2048
DEFAULT_REGEN_MAX_OUTPUT_TOKENS: int = 2048
HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS: int = 4096
RESERVED_SYSTEM_SCHEMA_TOKENS: int = 512
DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX: float = 0.92
CHARS_PER_TOKEN_ESTIMATE: int = 3
ESTIMATE_SAFETY_MULTIPLIER: float = 1.12

ENV_SCRATCH_MAX_OUTPUT_TOKENS = "APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS"
ENV_REGEN_MAX_OUTPUT_TOKENS = "APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS"
ENV_VERIFY_CONTEXT_WINDOW = "APPS_RG_EXEC_SUMMARY_VERIFY_VLLM_CONTEXT_WINDOW"


def default_provider_context_window() -> int:
    """L0 SSOT (``QWEN_LOCAL_MAX_MODEL_LEN``); override via ``VLLM_MAX_MODEL_LEN`` in env."""
    from agentic_core.L0_routing.config.model_registry import QWEN_LOCAL_MAX_MODEL_LEN

    return int(QWEN_LOCAL_MAX_MODEL_LEN)


def resolve_provider_context_window() -> int:
    raw = os.environ.get("VLLM_MAX_MODEL_LEN", "").strip()
    if raw:
        try:
            return max(4096, int(raw))
        except ValueError:
            pass
    return default_provider_context_window()


def resolve_scratch_max_output_tokens() -> int:
    raw = os.environ.get(ENV_SCRATCH_MAX_OUTPUT_TOKENS, str(DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS)).strip()
    try:
        n = int(raw)
    except ValueError:
        n = DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS
    return max(1, min(n, HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS))


def resolve_regen_max_output_tokens() -> int:
    raw = os.environ.get(ENV_REGEN_MAX_OUTPUT_TOKENS, str(DEFAULT_REGEN_MAX_OUTPUT_TOKENS)).strip()
    try:
        n = int(raw)
    except ValueError:
        n = DEFAULT_REGEN_MAX_OUTPUT_TOKENS
    scratch_cap = resolve_scratch_max_output_tokens()
    return max(1, min(n, scratch_cap))


def resolve_first_pass_input_utilization_max() -> float:
    """First-pass input cap fraction of ``available_input_tokens`` (fixed 0.92 @ 24k)."""
    return DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX


def available_input_tokens(
    provider_context_window: int,
    requested_max_output_tokens: int,
    *,
    reserved_system_schema_tokens: int = RESERVED_SYSTEM_SCHEMA_TOKENS,
) -> int:
    return max(
        0,
        int(provider_context_window) - int(requested_max_output_tokens) - int(reserved_system_schema_tokens),
    )


def resolve_bullet_selector_briefing_max_chars() -> int:
    return DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS


def resolve_bullet_selector_jd_max_chars() -> int:
    return DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS


__all__ = [
    "CHARS_PER_TOKEN_ESTIMATE",
    "DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS",
    "DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS",
    "DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX",
    "DEFAULT_REGEN_MAX_OUTPUT_TOKENS",
    "DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS",
    "ENV_REGEN_MAX_OUTPUT_TOKENS",
    "ENV_SCRATCH_MAX_OUTPUT_TOKENS",
    "ENV_VERIFY_CONTEXT_WINDOW",
    "ESTIMATE_SAFETY_MULTIPLIER",
    "HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS",
    "RESERVED_SYSTEM_SCHEMA_TOKENS",
    "TARGETING_NO_GAP_MAX_CHARS",
    "available_input_tokens",
    "default_provider_context_window",
    "resolve_bullet_selector_briefing_max_chars",
    "resolve_bullet_selector_jd_max_chars",
    "resolve_first_pass_input_utilization_max",
    "resolve_provider_context_window",
    "resolve_regen_max_output_tokens",
    "resolve_scratch_max_output_tokens",
]
