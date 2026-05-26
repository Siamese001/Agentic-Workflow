"""SSOT defaults and resolvers for executive_summary 24k context limits."""

from __future__ import annotations

import importlib

import pytest

from apps_rg.runtime.sections import executive_summary_context_limits as limits
from apps_rg.runtime.sections.executive_summary_context_limits import (
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
    assert DEFAULT_BULLET_SELECTOR_BRIEFING_MAX_CHARS == 6_000
    assert DEFAULT_BULLET_SELECTOR_JD_MAX_CHARS == 6_000


def test_24k_token_defaults() -> None:
    assert DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS == 2048
    assert DEFAULT_REGEN_MAX_OUTPUT_TOKENS == 2048
    assert HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS == 4096
    assert RESERVED_SYSTEM_SCHEMA_TOKENS == 512
    assert DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX == 0.92


def test_available_input_tokens_formula() -> None:
    assert available_input_tokens(24576, 2048) == 22016


def test_resolve_provider_context_window_matches_l0(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VLLM_MAX_MODEL_LEN", raising=False)
    from agentic_core.L0_routing.config import model_registry

    importlib.reload(model_registry)
    importlib.reload(limits)
    assert resolve_provider_context_window() == model_registry.QWEN_LOCAL_MAX_MODEL_LEN


def test_regen_output_capped_by_scratch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS", "1024")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS", "3000")
    importlib.reload(limits)
    assert limits.resolve_scratch_max_output_tokens() == 1024
    assert limits.resolve_regen_max_output_tokens() == 1024
