"""SSOT defaults and resolvers for executive_summary Claude-era context limits.

Defaults raised 2026-06-13 post-Qwen-removal: ctx 24576→32768, output 2048→4096,
hard cap 4096→8192; ctx raised again 2026-06-15 32768→131072 (kill the Qwen token-cap
class — VLLM_MAX_MODEL_LEN must not lower the section ctx). The legacy 24576/2048 numbers
belonged to Qwen 32B-AWQ; the section now generates on external Claude (~200k provider ctx).
"""

from __future__ import annotations

import importlib

import pytest

from apps_rg.runtime.sections import executive_summary_context_limits as limits
from apps_rg.runtime.sections.executive_summary_briefing import prepare_briefing_for_executive_summary
from apps_rg.runtime.sections.executive_summary_context_limits import (
    BRIEFING_RANKED_SELECTION_MAX_CHARS,
    DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS,
    DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS,
    DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX,
    DEFAULT_REGEN_MAX_OUTPUT_TOKENS,
    DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS,
    HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS,
    RESERVED_SYSTEM_SCHEMA_TOKENS,
    TARGETING_NO_GAP_MAX_CHARS,
    available_input_tokens,
    resolve_provider_context_window,
    resolve_regen_max_output_tokens,
    resolve_scratch_max_output_tokens,
)


def test_targeting_no_gap_max_chars_is_large() -> None:
    assert TARGETING_NO_GAP_MAX_CHARS >= 1_000_000


def test_bullet_selector_char_defaults() -> None:
    from apps_rg.runtime.sections.executive_summary_context_limits import (
        BULLET_SELECTOR_INPUT_SHARE_FRACTION,
        CHARS_PER_TOKEN_ESTIMATE,
    )
    # Claude-era defaults: ctx=131072 (raised 2026-06-15, kill Qwen cap), output=4096, reserved=512.
    available = 131_072 - 4_096 - 512
    expected = int(available * BULLET_SELECTOR_INPUT_SHARE_FRACTION) * CHARS_PER_TOKEN_ESTIMATE
    assert DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS == expected
    assert DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS == expected


def test_briefing_ranked_selection_uses_dedicated_cap() -> None:
    from apps_rg.runtime.sections.executive_summary_context_limits import (
        BRIEFING_INPUT_SHARE_FRACTION,
        CHARS_PER_TOKEN_ESTIMATE,
    )
    available = 131_072 - 4_096 - 512
    expected = int(available * BRIEFING_INPUT_SHARE_FRACTION) * CHARS_PER_TOKEN_ESTIMATE
    assert BRIEFING_RANKED_SELECTION_MAX_CHARS == expected
    # Brief must exceed the (now Claude-era 128k-derived) ranked-selection cap to trigger truncation.
    reps = (expected // 30) + 2000  # comfortably over BRIEFING_RANKED_SELECTION_MAX_CHARS
    long_brief = "## Target priorities\n" + ("regulated modernization emphasis. " * reps)
    long_brief += "\n## Secondary notes\n" + ("additional context tail. " * reps)
    _, receipt = prepare_briefing_for_executive_summary(long_brief)
    assert receipt["briefing_original_chars"] > receipt["briefing_included_chars"]
    assert receipt["truncation_or_selection_reason"] == "ranked_section_selection"


def test_claude_era_token_defaults() -> None:
    """Post-Qwen-removal Claude-era defaults (2026-06-13)."""
    assert DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS == 4096
    assert DEFAULT_REGEN_MAX_OUTPUT_TOKENS == 4096
    assert HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS == 8192
    assert RESERVED_SYSTEM_SCHEMA_TOKENS == 512
    assert DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX == 0.95


def test_available_input_tokens_formula() -> None:
    # Claude-era defaults: ctx=32768, output=4096, reserved=512 → available=28160.
    assert available_input_tokens(32768, 4096) == 28160
    # Legacy formula still computable for back-compat (Qwen-era values).
    assert available_input_tokens(24576, 2048) == 22016


def test_resolve_provider_context_window_uses_app_local_ssot(monkeypatch: pytest.MonkeyPatch) -> None:
    """Post-Qwen-removal (2026-06-13): the section ctx SSOT is APPS_RG_SECTION_MAX_MODEL_LEN
    via section_model_limits.SECTION_MODEL_MAX_MODEL_LEN. VLLM_MAX_MODEL_LEN is the Qwen
    container ctx SSOT and MUST NOT leak into the apps_rg section budget."""
    # VLLM_MAX_MODEL_LEN being set to a small Qwen value must NOT cap section ctx.
    monkeypatch.setenv("VLLM_MAX_MODEL_LEN", "24576")
    monkeypatch.setenv("APPS_RG_SECTION_MAX_MODEL_LEN", "32768")
    from apps_rg.runtime import section_model_limits

    importlib.reload(section_model_limits)
    importlib.reload(limits)
    # Resolver returns app-local SSOT, ignoring the (smaller) Qwen container var.
    assert limits.resolve_provider_context_window() == 32768
    assert section_model_limits.SECTION_MODEL_MAX_MODEL_LEN == 32768


def test_regen_output_capped_by_scratch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS", "1024")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS", "3000")
    importlib.reload(limits)
    assert limits.resolve_scratch_max_output_tokens() == 1024
    assert limits.resolve_regen_max_output_tokens() == 1024


def test_legacy_qwen_output_envs_remain_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS", "1536")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS", "1024")
    importlib.reload(limits)
    assert limits.resolve_scratch_max_output_tokens() == 1536
    assert limits.resolve_regen_max_output_tokens() == 1024
