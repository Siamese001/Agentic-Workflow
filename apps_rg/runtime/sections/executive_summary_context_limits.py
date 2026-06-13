"""SSOT char/token limits for executive_summary (context-window-aware).

Char limits are derived from the live token budget, not hardcoded.
``available_input_tokens`` and ``apply_executive_summary_token_budget_policy``
are the operator-visible gates.

Derivation for briefing/JD/bullet caps
---------------------------------------
context_window   = resolve_provider_context_window()  [env: APPS_RG_SECTION_MAX_MODEL_LEN
                                                       via section_model_limits.SECTION_MODEL_MAX_MODEL_LEN]
available_input  = context_window - output_tokens - reserved_tokens

Post-Qwen-removal env contract (2026-06-13)
-------------------------------------------
``VLLM_MAX_MODEL_LEN`` is the legacy Qwen container ctx SSOT — it must match the
running container ``--max-model-len`` (used by ``apps_lic`` and ``agentic_core``
healers). apps_rg sections now run on **external Claude** (per
``APPS_RG_EXTERNAL_CLAUDE_MODEL``) with ~200k provider ctx, so the legacy var
must NOT shadow the section budget. The canonical app-local override is
``APPS_RG_SECTION_MAX_MODEL_LEN``; ``resolve_provider_context_window`` reads
``section_model_limits.SECTION_MODEL_MAX_MODEL_LEN`` (env-backed) and ignores
``VLLM_MAX_MODEL_LEN``.

CHARS_PER_TOKEN_ESTIMATE calibration note
-----------------------------------------
Measured Qwen 2.5 tokenizer ratio (English prose, 2026-05-27):
  ~3.5 chars/token (empirical baseline from Brown & Brown briefing + JD inputs).
  Claude BPE tokenizer is similar (~3.5-4 chars/token typical English).
  CHARS_PER_TOKEN_ESTIMATE = 3 is intentionally conservative (floor, not mean)
  so that char caps never exceed true token budget even on token-dense text.
  Do not raise above 3.5 without a measured tokenizer run against live inputs.

ESTIMATE_SAFETY_MULTIPLIER = 1.12 (applied in token-estimation path, not here).

Briefing share (BRIEFING_INPUT_SHARE_FRACTION = 0.15 of available input):
  At ctx=32768, out=4096, reserved=512 → available=28160 → 28160*0.15*3 = 12672 chars
  At ctx=24576, out=2048, reserved=512 → available=22016 → 22016*0.15*3 = 9906 chars

Bullet-selector sub-prompt share (BULLET_SELECTOR_INPUT_SHARE_FRACTION = 0.09):
  At ctx=32768, out=4096, reserved=512 → 28160 * 0.09 * 3 = 7603 chars
  At ctx=24576, out=2048, reserved=512 → 22016 * 0.09 * 3 = 5946 chars

These fractions are tunable constants. The token budget gate is always the final
authority — these caps are a pre-filter for ranked selection only.
The ``resolve_*`` functions re-derive at call time so caps auto-scale when
``APPS_RG_SECTION_MAX_MODEL_LEN`` is set in the environment.
"""

from __future__ import annotations

import os

# No preventive char cap when the compiled prompt already fits (token budget is authority).
TARGETING_NO_GAP_MAX_CHARS: int = 10_000_000

# --- Token budget (Claude era, post-Qwen-removal) — output caps env-overridable ---
# Defaults raised 2048 → 4096 + hard cap 4096 → 8192 (2026-06-13) after W1 exec_summary
# parse-truncation analysis: 2048 output truncates exec_summary JSON. Env override:
# APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS / APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS.
DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS: int = 4_096
DEFAULT_REGEN_MAX_OUTPUT_TOKENS: int = 4_096
HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS: int = 8_192
RESERVED_SYSTEM_SCHEMA_TOKENS: int = 512
DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX: float = 0.95
CHARS_PER_TOKEN_ESTIMATE: int = 3
ESTIMATE_SAFETY_MULTIPLIER: float = 1.12

# --- Context-window budget parameters (must stay in sync with token_budget.py) ---
# Default raised 24576 → 32768 (2026-06-13) — see section_model_limits.SECTION_MODEL_MAX_MODEL_LEN.
_DEFAULT_CONTEXT_WINDOW: int = 32_768
_DEFAULT_OUTPUT_TOKENS: int = DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS
_DEFAULT_RESERVED_TOKENS: int = RESERVED_SYSTEM_SCHEMA_TOKENS

# --- Allocation fractions (tunable — change these, not the derived caps below) ---
# Share of available_input_tokens allocated to briefing ranked selection.
BRIEFING_INPUT_SHARE_FRACTION: float = 0.15
# Share of available_input_tokens allocated to bullet-pool Claude selector sub-prompt.
BULLET_SELECTOR_INPUT_SHARE_FRACTION: float = 0.09


def _derive_char_cap(share_fraction: float) -> int:
    """Derive a char cap from a fraction of available input tokens."""
    available = _DEFAULT_CONTEXT_WINDOW - _DEFAULT_OUTPUT_TOKENS - _DEFAULT_RESERVED_TOKENS
    tokens = int(available * share_fraction)
    return tokens * CHARS_PER_TOKEN_ESTIMATE


# Ranked briefing section selection (manifested; not silent tail truncate).
BRIEFING_RANKED_SELECTION_MAX_CHARS: int = _derive_char_cap(BRIEFING_INPUT_SHARE_FRACTION)

# Bullet-pool Claude selector sub-prompt.
DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS: int = _derive_char_cap(BULLET_SELECTOR_INPUT_SHARE_FRACTION)
DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS: int = _derive_char_cap(BULLET_SELECTOR_INPUT_SHARE_FRACTION)

ENV_SCRATCH_MAX_OUTPUT_TOKENS = "APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS"
ENV_REGEN_MAX_OUTPUT_TOKENS = "APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS"
LEGACY_ENV_SCRATCH_MAX_OUTPUT_TOKENS = "APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS"
LEGACY_ENV_REGEN_MAX_OUTPUT_TOKENS = "APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS"
ENV_VERIFY_CONTEXT_WINDOW = "APPS_RG_EXEC_SUMMARY_VERIFY_VLLM_CONTEXT_WINDOW"


def default_provider_context_window() -> int:
    """App-local section context window; override via ``APPS_RG_SECTION_MAX_MODEL_LEN`` in env."""
    from apps_rg.runtime.section_model_limits import SECTION_MODEL_MAX_MODEL_LEN

    return int(SECTION_MODEL_MAX_MODEL_LEN)


def resolve_provider_context_window() -> int:
    # Post-Qwen-removal (2026-06-13) precedence:
    #   (1) APPS_RG_SECTION_MAX_MODEL_LEN (via section_model_limits.SECTION_MODEL_MAX_MODEL_LEN)
    #       — app-local SSOT; wins when explicitly set by operator/.env.
    #   (2) VLLM_MAX_MODEL_LEN — LEGACY FALLBACK only (Qwen container ctx SSOT used by
    #       apps_lic + agentic_core healers). Kept readable here for backward-compat
    #       with pre-2026-06-13 deployments and tests that constrain ctx via this var;
    #       does NOT shadow (1) if (1) is set.
    #   (3) default_provider_context_window() — section_model_limits default (32768 Claude era).
    if os.environ.get("APPS_RG_SECTION_MAX_MODEL_LEN"):
        return default_provider_context_window()
    raw = os.environ.get("VLLM_MAX_MODEL_LEN", "").strip()
    if raw:
        try:
            return max(4096, int(raw))
        except ValueError:  # guardian: allow-silent-swallow -- legacy env compat fail-soft
            pass
    return default_provider_context_window()


def resolve_scratch_max_output_tokens() -> int:
    raw = os.environ.get(ENV_SCRATCH_MAX_OUTPUT_TOKENS)
    if raw is None:
        raw = os.environ.get(LEGACY_ENV_SCRATCH_MAX_OUTPUT_TOKENS, str(DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS))
    raw = str(raw).strip()
    try:
        n = int(raw)
    except ValueError:
        n = DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS
    return max(1, min(n, HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS))


def resolve_regen_max_output_tokens() -> int:
    raw = os.environ.get(ENV_REGEN_MAX_OUTPUT_TOKENS)
    if raw is None:
        raw = os.environ.get(LEGACY_ENV_REGEN_MAX_OUTPUT_TOKENS, str(DEFAULT_REGEN_MAX_OUTPUT_TOKENS))
    raw = str(raw).strip()
    try:
        n = int(raw)
    except ValueError:
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
    """Re-derive char cap at call time using the live context window (env-aware)."""
    ctx = resolve_provider_context_window()
    available = ctx - DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS - RESERVED_SYSTEM_SCHEMA_TOKENS
    tokens = int(available * share_fraction)
    return tokens * CHARS_PER_TOKEN_ESTIMATE


def resolve_briefing_ranked_selection_max_chars() -> int:
    """Briefing ranked-selection char cap — live, env-aware."""
    return _derive_char_cap_live(BRIEFING_INPUT_SHARE_FRACTION)


def resolve_bullet_selector_briefing_max_chars() -> int:
    """Bullet-selector briefing sub-prompt char cap — live, env-aware."""
    return _derive_char_cap_live(BULLET_SELECTOR_INPUT_SHARE_FRACTION)


def resolve_bullet_selector_jd_max_chars() -> int:
    """Bullet-selector JD sub-prompt char cap — live, env-aware."""
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
    "ENV_REGEN_MAX_OUTPUT_TOKENS",
    "ENV_SCRATCH_MAX_OUTPUT_TOKENS",
    "ENV_VERIFY_CONTEXT_WINDOW",
    "ESTIMATE_SAFETY_MULTIPLIER",
    "HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS",
    "LEGACY_ENV_REGEN_MAX_OUTPUT_TOKENS",
    "LEGACY_ENV_SCRATCH_MAX_OUTPUT_TOKENS",
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
