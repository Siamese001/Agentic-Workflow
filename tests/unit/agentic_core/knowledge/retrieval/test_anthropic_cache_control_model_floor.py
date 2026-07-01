"""Model-aware cache-floor tests for anthropic_cache_control (P3 / W2).

Plan: prompt-cache-anthropic-best-practice-c7a1e9 (W2).

Covers DoD-3 (no `cache_control` marker emitted below its model's token floor),
the silent-non-caching-on-Opus fix, and backward compatibility of the legacy
``model=None`` default. Authoritative Anthropic minimums (claude-api ref):
Opus 4.x / Haiku 4.5 = 4096 tokens; Fable 5 / Sonnet 5 = 2048; Sonnet 4.5 = 1024.
"""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    MODEL_CACHE_FLOOR_TOKENS,
    build_messages_payload,
    build_system_blocks,
    build_user_content,
    count_cache_markers,
    floor_tokens_for_model,
    min_cacheable_chars,
)

# _CHARS_PER_TOKEN is 4, so: opus/haiku-4.5 = 16384 chars, sonnet-5/fable = 8192,
# sonnet-4.5 = 4096, default(None/unknown) = 3500.
_OPUS = "claude-opus-4-5"
_SONNET = "claude-sonnet-5"
_HAIKU45 = "claude-haiku-4-5"
_FABLE = "claude-fable-5"


# --------------------------------------------------------------------------- #
# floor_tokens_for_model
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "model, expected",
    [
        ("claude-opus-4-5", 4096),
        ("claude-opus-4-5", 4096),
        ("claude-haiku-4-5", 4096),
        ("claude-sonnet-5", 2048),
        ("claude-fable-5", 2048),
        ("claude-haiku-3-5", 2048),  # generic haiku (not 4.5) → 2048
        ("claude-sonnet-4-5", 1024),
        ("claude-sonnet-3-7", 1024),
    ],
)
def test_floor_tokens_for_known_models(model, expected):
    assert floor_tokens_for_model(model) == expected


def test_floor_tokens_none_and_unknown():
    assert floor_tokens_for_model(None) is None
    assert floor_tokens_for_model("") is None
    assert floor_tokens_for_model("gpt-4o") is None


def test_haiku_4_5_resolves_before_generic_haiku():
    # Regression guard for most-specific-first ordering: haiku-4.5 must be 4096,
    # NOT the generic 2048 that the broader "claude-haiku" entry would give.
    assert floor_tokens_for_model("claude-haiku-4-5") == 4096
    assert floor_tokens_for_model("claude-haiku-3") == 2048


def test_model_floor_table_is_ordered_most_specific_first():
    # The specific model aliases must precede their generic family entries.
    keys = [k for k, _ in MODEL_CACHE_FLOOR_TOKENS]
    assert keys.index("claude-haiku-4-5") < keys.index("claude-haiku")
    assert keys.index("claude-sonnet-5") < keys.index("claude-sonnet")


# --------------------------------------------------------------------------- #
# min_cacheable_chars
# --------------------------------------------------------------------------- #


def test_min_cacheable_chars_model_aware():
    assert min_cacheable_chars(_OPUS) == 16384
    assert min_cacheable_chars(_SONNET) == 8192
    assert min_cacheable_chars(_HAIKU45) == 16384
    assert min_cacheable_chars(_FABLE) == 8192


def test_min_cacheable_chars_default_when_unknown():
    assert min_cacheable_chars(None) == 3500
    assert min_cacheable_chars("some-other-model") == 3500


# --------------------------------------------------------------------------- #
# DoD-3 — no marker below the model's floor (the Opus silent-non-caching fix)
# --------------------------------------------------------------------------- #


def test_opus_strips_marker_below_floor():
    # ~1250 tokens — would be marked under the old 3500-char default, but is
    # below Opus's real 4096-token floor, so it must NOT be marked.
    blocks = build_system_blocks("x" * 5000, model=_OPUS)
    assert "cache_control" not in blocks[0]


def test_opus_keeps_marker_above_floor():
    blocks = build_system_blocks("x" * 17000, model=_OPUS)
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}


def test_floor_is_model_specific_same_block_differs_by_model():
    # A 9000-char block: above Sonnet 5's 8192 floor, below Opus's 16384.
    text = "x" * 9000
    assert "cache_control" in build_system_blocks(text, model=_SONNET)[0]
    assert "cache_control" not in build_system_blocks(text, model=_OPUS)[0]


# --------------------------------------------------------------------------- #
# Backward compatibility — model=None preserves the legacy 3500-char default
# --------------------------------------------------------------------------- #


def test_default_path_unchanged_long_block_cached():
    blocks = build_system_blocks("x" * 4000)  # model omitted
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}


def test_default_path_unchanged_short_block_not_cached():
    blocks = build_system_blocks("x" * 3000)  # below 3500 default
    assert "cache_control" not in blocks[0]


# --------------------------------------------------------------------------- #
# model threads through build_user_content + build_messages_payload
# --------------------------------------------------------------------------- #


def test_user_content_prefix_below_opus_floor_not_marked():
    prefix = "x" * 9000  # below 16384 opus floor
    prompt = prefix + "QUERY"
    blocks = build_user_content(prompt, cache_boundary_hint=len(prefix), model=_OPUS)
    assert len(blocks) == 2
    assert "cache_control" not in blocks[0]  # stripped for opus


def test_messages_payload_threads_model_to_floor():
    system = "x" * 9000  # above sonnet floor, below opus floor
    # Opus: system block below its floor → 0 markers.
    assert count_cache_markers(build_messages_payload("hi", system_prompt=system, model=_OPUS)) == 0
    # Sonnet 5: above its 8192 floor → 1 marker.
    assert count_cache_markers(build_messages_payload("hi", system_prompt=system, model=_SONNET)) == 1
    # Legacy default (no model): above 3500 → 1 marker (unchanged behavior).
    assert count_cache_markers(build_messages_payload("hi", system_prompt=system)) == 1


def test_model_arg_not_written_into_payload():
    payload = build_messages_payload("hi", system_prompt="x" * 17000, model=_OPUS)
    assert "model" not in payload
    assert "max_tokens" not in payload
