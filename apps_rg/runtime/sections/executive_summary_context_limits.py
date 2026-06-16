"""SSOT char/token limits for executive_summary (context-window-aware).

Char limits are derived from the runtime limit SSOT, not hardcoded.
``available_input_tokens`` and ``apply_executive_summary_token_budget_policy``
are the operator-visible gates.

Derivation for briefing/JD/bullet caps
---------------------------------------
context_window   = resolve_provider_context_window()
available_input  = context_window - output_tokens - reserved_tokens

CHARS_PER_TOKEN_ESTIMATE calibration note
-----------------------------------------
CHARS_PER_TOKEN_ESTIMATE is intentionally conservative so char caps do not
exceed the token budget on token-dense text.

Runtime limits are configured in ``apps_rg/config/provider_profiles.yaml`` under
``runtime_limits``. Environment variables are not an LLM budget source.
"""

from __future__ import annotations

from apps_rg.runtime.section_model_limits import (
    SECTION_MODEL_MAX_MODEL_LEN,
    runtime_limit_float,
    runtime_limit_int,
)

# No preventive char cap when the compiled prompt already fits (token budget is authority).
TARGETING_NO_GAP_MAX_CHARS: int = 10_000_000

DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS: int = runtime_limit_int(
    "executive_summary.scratch_max_output_tokens"
)
DEFAULT_REGEN_MAX_OUTPUT_TOKENS: int = runtime_limit_int(
    "executive_summary.regen_max_output_tokens"
)
HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS: int = runtime_limit_int(
    "executive_summary.hard_cap_scratch_max_output_tokens"
)
RESERVED_SYSTEM_SCHEMA_TOKENS: int = runtime_limit_int(
    "executive_summary.reserved_system_schema_tokens"
)
DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX: float = runtime_limit_float(
    "executive_summary.first_pass_input_utilization_max"
)
CHARS_PER_TOKEN_ESTIMATE: int = runtime_limit_int("executive_summary.chars_per_token_estimate")
ESTIMATE_SAFETY_MULTIPLIER: float = runtime_limit_float(
    "executive_summary.estimate_safety_multiplier"
)

# --- Context-window budget parameters ---
# DERIVED from the single section context-window SSOT. This is NOT an independent literal —
# it tracks the SSOT so there is exactly one place to change the section context window.
_DEFAULT_CONTEXT_WINDOW: int = int(SECTION_MODEL_MAX_MODEL_LEN)
_DEFAULT_OUTPUT_TOKENS: int = DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS
_DEFAULT_RESERVED_TOKENS: int = RESERVED_SYSTEM_SCHEMA_TOKENS

BRIEFING_INPUT_SHARE_FRACTION: float = runtime_limit_float(
    "executive_summary.briefing_input_share_fraction"
)
BULLET_SELECTOR_INPUT_SHARE_FRACTION: float = runtime_limit_float(
    "executive_summary.bullet_selector_input_share_fraction"
)


def _derive_char_cap(share_fraction: float) -> int:
    """Derive a char cap from a fraction of available input tokens."""
    available = _DEFAULT_CONTEXT_WINDOW - _DEFAULT_OUTPUT_TOKENS - _DEFAULT_RESERVED_TOKENS
    tokens = int(available * share_fraction)
    return tokens * CHARS_PER_TOKEN_ESTIMATE


# Ranked briefing section selection (manifested; not silent tail truncate).
BRIEFING_RANKED_SELECTION_MAX_CHARS: int = _derive_char_cap(BRIEFING_INPUT_SHARE_FRACTION)

DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS: int = _derive_char_cap(BULLET_SELECTOR_INPUT_SHARE_FRACTION)
DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS: int = _derive_char_cap(BULLET_SELECTOR_INPUT_SHARE_FRACTION)


def default_provider_context_window() -> int:
    """App-local section context window from provider_profiles.yaml runtime_limits."""
    from apps_rg.runtime.section_model_limits import SECTION_MODEL_MAX_MODEL_LEN

    return int(SECTION_MODEL_MAX_MODEL_LEN)


def resolve_provider_context_window() -> int:
    return default_provider_context_window()


def resolve_scratch_max_output_tokens() -> int:
    n = DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS
    return max(1, min(n, HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS))


def resolve_regen_max_output_tokens() -> int:
    n = DEFAULT_REGEN_MAX_OUTPUT_TOKENS
    scratch_cap = resolve_scratch_max_output_tokens()
    return max(1, min(n, scratch_cap))


def resolve_first_pass_input_utilization_max() -> float:
    """First-pass input cap fraction of ``available_input_tokens`` (fixed 0.95 @ 24k)."""
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


def _derive_char_cap_live(share_fraction: float) -> int:
    """Re-derive char cap at call time using the SSOT context window."""
    ctx = resolve_provider_context_window()
    available = ctx - resolve_scratch_max_output_tokens() - RESERVED_SYSTEM_SCHEMA_TOKENS
    tokens = int(available * share_fraction)
    return tokens * CHARS_PER_TOKEN_ESTIMATE


def resolve_briefing_ranked_selection_max_chars() -> int:
    """Briefing ranked-selection char cap."""
    return _derive_char_cap_live(BRIEFING_INPUT_SHARE_FRACTION)


def resolve_bullet_selector_briefing_max_chars() -> int:
    """Bullet-selector briefing sub-prompt char cap."""
    return _derive_char_cap_live(BULLET_SELECTOR_INPUT_SHARE_FRACTION)


def resolve_bullet_selector_jd_max_chars() -> int:
    """Bullet-selector JD sub-prompt char cap."""
    return _derive_char_cap_live(BULLET_SELECTOR_INPUT_SHARE_FRACTION)


__all__ = [
    "BRIEFING_INPUT_SHARE_FRACTION",
    "BRIEFING_RANKED_SELECTION_MAX_CHARS",
    "BULLET_SELECTOR_INPUT_SHARE_FRACTION",
    "CHARS_PER_TOKEN_ESTIMATE",
    "DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS",
    "DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS",
    "DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX",
    "DEFAULT_REGEN_MAX_OUTPUT_TOKENS",
    "DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS",
    "ESTIMATE_SAFETY_MULTIPLIER",
    "HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS",
    "RESERVED_SYSTEM_SCHEMA_TOKENS",
    "TARGETING_NO_GAP_MAX_CHARS",
    "available_input_tokens",
    "default_provider_context_window",
    "resolve_briefing_ranked_selection_max_chars",
    "resolve_bullet_selector_briefing_max_chars",
    "resolve_bullet_selector_jd_max_chars",
    "resolve_first_pass_input_utilization_max",
    "resolve_provider_context_window",
    "resolve_regen_max_output_tokens",
    "resolve_scratch_max_output_tokens",
]
