"""Unit tests for anthropic_cache_control helpers."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    CACHE_TTL_1H,
    CACHE_TTL_5M,
    build_messages_payload,
    build_system_blocks,
    build_user_content,
    count_cache_markers,
)

# Long text that meets the >=3500 char cacheable threshold
_LONG = "x" * 4000
_SHORT = "short prompt"


# ---------------------------------------------------------------------------
# build_system_blocks
# ---------------------------------------------------------------------------


def test_system_block_with_cache_for_long_prompt():
    blocks = build_system_blocks(_LONG)
    assert len(blocks) == 1
    assert blocks[0]["type"] == "text"
    assert blocks[0]["text"] == _LONG
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}


def test_system_block_1h_ttl_marker():
    blocks = build_system_blocks(_LONG, ttl=CACHE_TTL_1H)
    assert blocks[0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}


def test_system_block_skips_cache_for_short_prompt():
    blocks = build_system_blocks(_SHORT)
    assert len(blocks) == 1
    assert "cache_control" not in blocks[0]


def test_system_block_cache_disabled_produces_plain_block():
    blocks = build_system_blocks(_LONG, cache=False)
    assert "cache_control" not in blocks[0]


def test_system_block_empty_returns_empty_list():
    assert build_system_blocks("") == []
    assert build_system_blocks("   \n\t ") == []


def test_system_block_strips_whitespace():
    blocks = build_system_blocks("  hello  ")
    assert blocks[0]["text"] == "hello"


# ---------------------------------------------------------------------------
# build_user_content
# ---------------------------------------------------------------------------


def test_user_content_no_boundary_single_block_no_cache():
    blocks = build_user_content("short prompt body")
    assert blocks == [{"type": "text", "text": "short prompt body"}]


def test_user_content_with_boundary_splits_into_two_blocks():
    prompt = _LONG + "QUERY_SUFFIX_HERE"
    boundary = len(_LONG)
    blocks = build_user_content(prompt, cache_boundary_hint=boundary)
    assert len(blocks) == 2
    assert blocks[0]["text"] == _LONG
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}
    assert blocks[1]["text"] == "QUERY_SUFFIX_HERE"
    assert "cache_control" not in blocks[1]


def test_user_content_boundary_at_zero_treated_as_no_boundary():
    blocks = build_user_content("some prompt", cache_boundary_hint=0)
    assert len(blocks) == 1
    assert "cache_control" not in blocks[0]


def test_user_content_boundary_at_end_treated_as_no_boundary():
    prompt = "abc"
    blocks = build_user_content(prompt, cache_boundary_hint=len(prompt))
    assert len(blocks) == 1


def test_user_content_negative_boundary_treated_as_no_boundary():
    blocks = build_user_content("abc", cache_boundary_hint=-1)
    assert len(blocks) == 1


def test_user_content_short_prefix_splits_without_cache_marker():
    prompt = "abc" + "QUERY"  # prefix < threshold
    blocks = build_user_content(prompt, cache_boundary_hint=3)
    assert len(blocks) == 2
    assert "cache_control" not in blocks[0]  # too short to cache
    assert blocks[0]["text"] == "abc"
    assert blocks[1]["text"] == "QUERY"


def test_user_content_empty_suffix_reverts_to_single_block():
    # Boundary puts everything in prefix, suffix is empty
    prompt = _LONG
    blocks = build_user_content(prompt, cache_boundary_hint=len(_LONG))
    assert len(blocks) == 1  # collapsed back to single block


def test_user_content_whitespace_only_suffix_reverts_to_single_block():
    prompt = _LONG + "   \n\t"
    blocks = build_user_content(prompt, cache_boundary_hint=len(_LONG))
    assert len(blocks) == 1


def test_user_content_cache_prefix_false_produces_plain_split():
    prompt = _LONG + "QUERY"
    blocks = build_user_content(
        prompt, cache_boundary_hint=len(_LONG), cache_prefix=False
    )
    assert len(blocks) == 2
    assert "cache_control" not in blocks[0]


def test_user_content_1h_ttl_applied_to_prefix():
    prompt = _LONG + "Q"
    blocks = build_user_content(
        prompt, cache_boundary_hint=len(_LONG), ttl=CACHE_TTL_1H
    )
    assert blocks[0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}


def test_user_content_empty_prompt_returns_empty_list():
    assert build_user_content("") == []


# ---------------------------------------------------------------------------
# build_messages_payload
# ---------------------------------------------------------------------------


def test_payload_includes_system_when_non_empty():
    payload = build_messages_payload(
        user_prompt="hi",
        system_prompt=_LONG,
    )
    assert "system" in payload
    assert payload["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert payload["messages"][0]["role"] == "user"


def test_payload_omits_system_when_empty():
    payload = build_messages_payload(user_prompt="hi", system_prompt="")
    assert "system" not in payload
    assert payload["messages"][0]["role"] == "user"


def test_payload_has_no_model_or_max_tokens_keys():
    payload = build_messages_payload(user_prompt="hi", system_prompt=_LONG)
    # These belong to the caller, not this helper
    assert "model" not in payload
    assert "max_tokens" not in payload


def test_payload_with_boundary_produces_two_user_blocks():
    prompt = _LONG + "QUERY"
    payload = build_messages_payload(
        user_prompt=prompt,
        cache_boundary_hint=len(_LONG),
    )
    content = payload["messages"][0]["content"]
    assert len(content) == 2
    assert content[0]["cache_control"] == {"type": "ephemeral"}


# ---------------------------------------------------------------------------
# count_cache_markers
# ---------------------------------------------------------------------------


def test_count_markers_empty_payload():
    assert count_cache_markers({}) == 0
    assert count_cache_markers({"system": [], "messages": []}) == 0


def test_count_markers_system_only():
    payload = build_messages_payload(user_prompt="short", system_prompt=_LONG)
    assert count_cache_markers(payload) == 1


def test_count_markers_system_and_user_prefix():
    prompt = _LONG + "QUERY"
    payload = build_messages_payload(
        user_prompt=prompt,
        system_prompt=_LONG,
        cache_boundary_hint=len(_LONG),
    )
    assert count_cache_markers(payload) == 2


def test_count_markers_zero_when_both_below_threshold():
    payload = build_messages_payload(user_prompt="short q", system_prompt="short s")
    assert count_cache_markers(payload) == 0


# ---------------------------------------------------------------------------
# Parametrized sanity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ttl", [CACHE_TTL_5M, CACHE_TTL_1H])
def test_all_ttls_produce_valid_ephemeral_markers(ttl):
    blocks = build_system_blocks(_LONG, ttl=ttl)
    marker = blocks[0]["cache_control"]
    assert marker["type"] == "ephemeral"
    if ttl == CACHE_TTL_1H:
        assert marker.get("ttl") == "1h"
    else:
        # 5m is the default — absence of ttl key is equivalent
        assert "ttl" not in marker
