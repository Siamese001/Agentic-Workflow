"""Tests for apps_shared.chunking (plan §P3.2)."""

from __future__ import annotations

import pytest

from apps_shared.chunking import chunk_text


def test_empty_input_returns_empty():
    assert chunk_text("") == []


def test_short_input_returns_single_chunk():
    out = chunk_text("one two three", chunk_tokens=512, overlap_tokens=50)
    assert len(out) == 1
    assert out[0] == "one two three"


def test_long_input_produces_multiple_chunks():
    words = [f"word{i}" for i in range(2000)]
    text = " ".join(words)
    out = chunk_text(text, chunk_tokens=512, overlap_tokens=50)
    assert len(out) >= 3


def test_chunks_respect_max_size():
    words = [f"w{i}" for i in range(1500)]
    text = " ".join(words)
    out = chunk_text(text, chunk_tokens=256, overlap_tokens=25)
    # Whitespace fallback uses 1 word = 1 token; with tiktoken token counts
    # differ but each chunk_text(...) call is internally consistent — we
    # assert re-chunking the first chunk yields exactly that same chunk.
    for c in out:
        assert chunk_text(c, chunk_tokens=256, overlap_tokens=25) == [c]


def test_overlap_present_between_adjacent_chunks():
    words = [f"w{i}" for i in range(1500)]
    text = " ".join(words)
    out = chunk_text(text, chunk_tokens=200, overlap_tokens=50)
    # At least the first two chunks must share some overlap tokens (whitespace fallback).
    first_tail = out[0].split()[-50:]
    second_head = out[1].split()[:50]
    overlap = set(first_tail) & set(second_head)
    assert len(overlap) >= 1


def test_invalid_args_raise():
    with pytest.raises(ValueError):
        chunk_text("x", chunk_tokens=0, overlap_tokens=0)
    with pytest.raises(ValueError):
        chunk_text("x", chunk_tokens=50, overlap_tokens=50)
    with pytest.raises(ValueError):
        chunk_text("x", chunk_tokens=50, overlap_tokens=-1)
