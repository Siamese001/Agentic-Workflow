"""Prompt / completion budget helpers for apps_rg local vLLM lane.

Mirrors ``optimized_vllm_client`` truncation and max_token clamping so we can
fail-closed *before* invocation when schema tail would be destroyed or when
completion headroom is too small for rg_output-shaped JSON.
"""
from __future__ import annotations

from dataclasses import dataclass

from apps_rg.runtime.qwen_vllm_health import QWEN_LOCAL_MAX_MODEL_LEN

# Must match optimized_vllm_client._truncate_prompt_for_context (line ~51: max_chars = max_prompt_tokens * 2).
# _CHARS_PER_TOKEN_EST = 2 is intentionally lower than the SSOT constant (CHARS_PER_TOKEN_ESTIMATE = 3
# in executive_summary_context_limits) because this mirrors the actual vLLM client truncation ratio,
# not the ranked-selection pre-filter. Keeping both in sync with the client is the correctness contract.
_TRUNC_RESERVE = 128
_TRUNC_MIN_PROMPT_TOKENS = 256
_CHARS_PER_TOKEN_EST = 2
# Minimum prefix room so S0/D0/I0 governance headers are not squeezed to zero
_MIN_PREFIX_CHARS = 1800
# Heuristic: full rg_output JSON typically needs substantial completion budget
_MIN_COMPLETION_TOKENS_FOR_FULL_RESUME = 2048

R0_SLOT_MARKER = "<!-- SLOT: R0 -->"


@dataclass(frozen=True)
class PromptBudgetError(Exception):
    """Fail-closed budget guard — maps to E3 decisive codes."""

    code: str
    message: str


def completion_budget_for_truncation(requested_max_tokens: int) -> int:
    """Match ``completion_target`` in ``OptimizedVLLMClient._call_single``."""
    return max(256, min(int(requested_max_tokens), 4096))


def prompt_char_limit_for_context(*, completion_budget: int) -> tuple[int, int]:
    """Return (max_prompt_chars, max_prompt_tokens) before client truncation."""
    max_prompt_tokens = int(QWEN_LOCAL_MAX_MODEL_LEN) - int(completion_budget) - _TRUNC_RESERVE
    if max_prompt_tokens < _TRUNC_MIN_PROMPT_TOKENS:
        max_prompt_tokens = _TRUNC_MIN_PROMPT_TOKENS
    max_chars = max_prompt_tokens * _CHARS_PER_TOKEN_EST
    return max_chars, max_prompt_tokens


def clamp_completion_tokens(*, prompt: str, requested_max_tokens: int) -> int:
    """Copy of ``optimized_vllm_client._clamp_completion_tokens`` (keep in sync)."""
    est_prompt_tokens = max(1, len(prompt) // _CHARS_PER_TOKEN_EST)
    reserve = 96
    room = int(QWEN_LOCAL_MAX_MODEL_LEN) - est_prompt_tokens - reserve
    if room < 1:
        return 1
    return max(1, min(int(requested_max_tokens), int(room)))


def pack_prompt_keep_schema_suffix(
    prompt: str,
    *,
    max_total_chars: int,
) -> tuple[str, dict]:
    """Truncate **prefix** evidence so R0–tail survives vLLM head-only truncation.

    vLLM client keeps ``prompt[:max_chars]`` — with schema slots last, naive
    truncation drops R0. Pre-trimming prefix yields a prompt whose leading
    segment already fits the budget while preserving the tail verbatim.
    """
    meta: dict = {
        "prompt_packed": False,
        "removed_prefix_chars": 0,
        "max_total_chars": max_total_chars,
        "r0_marker_found": R0_SLOT_MARKER in prompt,
    }
    if len(prompt) <= max_total_chars:
        return prompt, meta

    idx = prompt.find(R0_SLOT_MARKER)
    if idx < 0:
        # No marker — cannot protect schema; head truncation will be arbitrary.
        packed = prompt[:max_total_chars]
        meta["prompt_packed"] = True
        meta["pack_mode"] = "head_only_no_r0_marker"
        meta["removed_prefix_chars"] = len(prompt) - len(packed)
        return packed, meta

    suffix = prompt[idx:]
    if len(suffix) > max_total_chars:
        raise PromptBudgetError(
            "E3_PROMPT_BUDGET_SCHEMA_TRUNCATION",
            "R0+tail segment exceeds vLLM prompt char budget — cannot preserve schema instructions",
        )

    room_prefix = max_total_chars - len(suffix)
    if room_prefix < _MIN_PREFIX_CHARS:
        raise PromptBudgetError(
            "E3_PROMPT_BUDGET_SCHEMA_TRUNCATION",
            f"Insufficient prefix budget after reserving R0 tail "
            f"(room_prefix={room_prefix}, min={_MIN_PREFIX_CHARS})",
        )

    prefix = prompt[:idx]
    if len(prefix) <= room_prefix:
        return prompt[: max_total_chars], meta

    trimmed = prefix[:room_prefix].rstrip()
    notice = "\n\n[# APPS_RG_EVIDENCE_TRUNCATED_FOR_CONTEXT_BUDGET]\n"
    packed = trimmed + notice + suffix
    if len(packed) > max_total_chars:
        overflow = len(packed) - max_total_chars
        trimmed = trimmed[: max(0, len(trimmed) - overflow)].rstrip()
        packed = trimmed + notice + suffix
    meta["prompt_packed"] = True
    meta["pack_mode"] = "prefix_trim_keep_r0_suffix"
    meta["removed_prefix_chars"] = max(0, len(prefix) - len(trimmed))
    return packed, meta


def assert_completion_budget(
    packed_prompt: str,
    *,
    requested_max_tokens: int,
    min_completion_tokens: int = _MIN_COMPLETION_TOKENS_FOR_FULL_RESUME,
) -> tuple[int, dict]:
    """Ensure clamped completion budget is viable for full JSON résumé."""
    eff = clamp_completion_tokens(
        prompt=packed_prompt,
        requested_max_tokens=requested_max_tokens,
    )
    meta = {
        "requested_max_tokens": int(requested_max_tokens),
        "effective_max_tokens": eff,
        "min_completion_tokens_required": min_completion_tokens,
    }
    if eff < min_completion_tokens:
        raise PromptBudgetError(
            "E3_OUTPUT_BUDGET_TOO_SMALL",
            f"effective max_tokens after clamp={eff} < required {min_completion_tokens} "
            f"(prompt_chars={len(packed_prompt)}, max_model_len={QWEN_LOCAL_MAX_MODEL_LEN})",
        )
    return eff, meta


def prepare_prompt_for_local_vllm(
    prompt: str,
    *,
    requested_max_tokens: int,
) -> tuple[str, dict]:
    """Pack + validate budgets; return prompt suitable for ProviderRequest."""
    cb = completion_budget_for_truncation(requested_max_tokens)
    lim_chars, lim_tok = prompt_char_limit_for_context(completion_budget=cb)
    packed, pack_meta = pack_prompt_keep_schema_suffix(prompt, max_total_chars=lim_chars)
    eff_tok, comp_meta = assert_completion_budget(
        packed,
        requested_max_tokens=requested_max_tokens,
    )
    merged = {
        "max_model_len": int(QWEN_LOCAL_MAX_MODEL_LEN),
        "completion_budget_for_truncation": cb,
        "max_prompt_tokens_estimate": lim_tok,
        "max_prompt_chars_budget": lim_chars,
        "input_prompt_chars_pre_pack": len(prompt),
        "input_prompt_chars_post_pack": len(packed),
        "pre_pack_would_truncate_vllm": len(prompt) > lim_chars,
        "pack_meta": pack_meta,
        "completion_meta": comp_meta,
        "effective_max_tokens": eff_tok,
    }
    return packed, merged


__all__ = [
    "PromptBudgetError",
    "R0_SLOT_MARKER",
    "completion_budget_for_truncation",
    "prepare_prompt_for_local_vllm",
    "prompt_char_limit_for_context",
    "clamp_completion_tokens",
    "pack_prompt_keep_schema_suffix",
]
