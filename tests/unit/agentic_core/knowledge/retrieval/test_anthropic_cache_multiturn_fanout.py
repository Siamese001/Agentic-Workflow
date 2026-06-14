"""Multi-turn breakpoints + operator channel + fan-out tests (P7 + P8 / W5).

Plan: prompt-cache-anthropic-best-practice-c7a1e9 (W5).

Covers: 20-block-lookback breakpoint placement (last block + every <=15 blocks,
capped to 4 most-recent, existing markers cleared, inputs not mutated); the
role:"system" operator channel; and the fan-out priming splitter.
"""

from __future__ import annotations

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    append_operator_system_message,
    place_multiturn_breakpoints,
    split_for_cache_priming,
)


def _count_markers(messages) -> int:
    return sum(
        1
        for m in messages
        for b in (m.get("content") or [])
        if isinstance(b, dict) and "cache_control" in b
    )


def _one_message(n_blocks: int):
    return [{"role": "user", "content": [{"type": "text", "text": f"b{i}"} for i in range(n_blocks)]}]


# --------------------------------------------------------------------------- #
# place_multiturn_breakpoints (P7)
# --------------------------------------------------------------------------- #


def test_marks_last_block():
    out = place_multiturn_breakpoints(_one_message(3))
    blocks = out[0]["content"]
    assert "cache_control" in blocks[-1]  # last block of the most-recent turn
    assert _count_markers(out) == 1


def test_intermediate_breakpoints_every_stride():
    out = place_multiturn_breakpoints(_one_message(40), stride=15)
    blocks = out[0]["content"]
    # positions: 39 (last), 24, 9 → 3 markers, each <=15 apart.
    assert "cache_control" in blocks[39]
    assert "cache_control" in blocks[24]
    assert "cache_control" in blocks[9]
    assert "cache_control" not in blocks[0]
    assert _count_markers(out) == 3


def test_caps_to_four_most_recent():
    out = place_multiturn_breakpoints(_one_message(70), stride=15)
    blocks = out[0]["content"]
    assert _count_markers(out) == 4  # capped at Anthropic's 4
    assert "cache_control" in blocks[69]  # most-recent kept
    assert "cache_control" not in blocks[9]  # oldest breakpoint dropped


def test_clears_existing_markers():
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "a", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": "b"},
            ],
        }
    ]
    out = place_multiturn_breakpoints(messages, stride=15)
    blocks = out[0]["content"]
    assert "cache_control" not in blocks[0]  # stale marker cleared
    assert "cache_control" in blocks[1]  # re-placed on the last block
    assert _count_markers(out) == 1


def test_normalizes_string_content():
    out = place_multiturn_breakpoints([{"role": "user", "content": "hello"}])
    assert isinstance(out[0]["content"], list)
    assert out[0]["content"][0]["cache_control"] == {"type": "ephemeral"}


def test_does_not_mutate_input():
    messages = _one_message(3)
    place_multiturn_breakpoints(messages)
    assert all("cache_control" not in b for b in messages[0]["content"])  # original untouched


def test_empty_messages():
    assert place_multiturn_breakpoints([]) == []


def test_1h_ttl_marker():
    out = place_multiturn_breakpoints(_one_message(2), ttl="1h")
    assert out[0]["content"][-1]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}


# --------------------------------------------------------------------------- #
# append_operator_system_message (P7)
# --------------------------------------------------------------------------- #


def test_appends_system_role():
    messages = [{"role": "user", "content": "hi"}]
    out = append_operator_system_message(messages, "Terse mode enabled.")
    assert out[-1] == {"role": "system", "content": "Terse mode enabled."}
    assert out[-2]["role"] == "user"
    assert len(messages) == 1  # input not mutated


def test_empty_instruction_is_noop_copy():
    messages = [{"role": "user", "content": "hi"}]
    out = append_operator_system_message(messages, "")
    assert out == messages
    assert out is not messages


# --------------------------------------------------------------------------- #
# split_for_cache_priming (P8)
# --------------------------------------------------------------------------- #


def test_split_primer_and_rest():
    a, b, c = {"id": 1}, {"id": 2}, {"id": 3}
    primer, rest = split_for_cache_priming([a, b, c])
    assert primer is a
    assert rest == [b, c]


def test_split_single():
    a = {"id": 1}
    primer, rest = split_for_cache_priming([a])
    assert primer is a
    assert rest == []


def test_split_empty():
    primer, rest = split_for_cache_priming([])
    assert primer is None
    assert rest == []
