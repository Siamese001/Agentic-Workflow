"""SSOT defaults and resolvers for executive_summary context limits."""

from __future__ import annotations

import pytest

from apps_rg.runtime.sections import executive_summary_context_limits as limits
from apps_rg.runtime.sections.executive_summary_briefing import prepare_briefing_for_executive_summary
from apps_rg.runtime.sections.executive_summary_context_limits import (
    _DEFAULT_CONTEXT_WINDOW,
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

# The expected available-input budget, derived from the SAME SSOT the source derives from
# (section context window − output − reserved). No hardcoded ctx literal — if the SSOT
# (SECTION_MODEL_MAX_MODEL_LEN) changes, these tests track it automatically.
_EXPECTED_AVAILABLE_INPUT = (
    _DEFAULT_CONTEXT_WINDOW - DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS - RESERVED_SYSTEM_SCHEMA_TOKENS
)


def test_targeting_no_gap_max_chars_is_large() -> None:
    assert TARGETING_NO_GAP_MAX_CHARS >= 1_000_000


def test_bullet_selector_char_defaults() -> None:
    from apps_rg.runtime.sections.executive_summary_context_limits import (
        BULLET_SELECTOR_INPUT_SHARE_FRACTION,
        CHARS_PER_TOKEN_ESTIMATE,
    )
    # Derived from the section-ctx SSOT (not a hardcoded ctx literal): available = ctx − out − reserved.
    available = _EXPECTED_AVAILABLE_INPUT
    expected = int(available * BULLET_SELECTOR_INPUT_SHARE_FRACTION) * CHARS_PER_TOKEN_ESTIMATE
    assert DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS == expected
    assert DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS == expected


def test_briefing_ranked_selection_uses_dedicated_cap() -> None:
    from apps_rg.runtime.sections.executive_summary_context_limits import (
        BRIEFING_INPUT_SHARE_FRACTION,
        CHARS_PER_TOKEN_ESTIMATE,
    )
    available = _EXPECTED_AVAILABLE_INPUT
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
    # Pure-formula checks with EXPLICIT inputs (not the SSOT default): available = ctx − out − reserved.
    assert available_input_tokens(32768, 4096) == 28160
    assert available_input_tokens(24576, 2048) == 22016
    # And the formula applied to the actual section-ctx SSOT matches the derived budget.
    assert (
        available_input_tokens(_DEFAULT_CONTEXT_WINDOW, DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS)
        == _EXPECTED_AVAILABLE_INPUT
    )


def test_resolve_provider_context_window_uses_yaml_ssot(monkeypatch: pytest.MonkeyPatch) -> None:
    """Env context variables must not override the YAML runtime limit."""
    monkeypatch.setenv("VLLM_MAX_MODEL_LEN", "24576")
    monkeypatch.setenv("APPS_RG_SECTION_MAX_MODEL_LEN", "32768")
    assert limits.resolve_provider_context_window() == _DEFAULT_CONTEXT_WINDOW


def test_regen_output_capped_by_scratch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS", "1024")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS", "3000")
    assert limits.resolve_scratch_max_output_tokens() == DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS
    assert limits.resolve_regen_max_output_tokens() == DEFAULT_REGEN_MAX_OUTPUT_TOKENS


def test_legacy_qwen_output_envs_are_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS", "1536")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS", "1024")
    assert limits.resolve_scratch_max_output_tokens() == DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS
    assert limits.resolve_regen_max_output_tokens() == DEFAULT_REGEN_MAX_OUTPUT_TOKENS
