"""Tests for apps_research.outputs.stat_table_renderer (plan §P2.2)."""

from __future__ import annotations

from apps_research.outputs.stat_table_renderer import render


def test_empty_list_returns_placeholder():
    assert "No structured stats available" in render([])


def test_none_returns_placeholder():
    assert "No structured stats available" in render(None)


def test_single_row_well_formed():
    out = render([{"metric": "headcount", "value": "500", "source": "https://x"}])
    assert "| metric | value | source |" in out
    assert "|---|---|---|" in out
    assert "| headcount | 500 | https://x |" in out


def test_multi_row_preserves_order():
    out = render(
        [
            {"metric": "a", "value": "1", "source": "s1"},
            {"metric": "b", "value": "2", "source": "s2"},
        ]
    )
    # Row 'a' must appear before row 'b'.
    a_pos = out.index("| a ")
    b_pos = out.index("| b ")
    assert a_pos < b_pos


def test_missing_keys_render_as_empty_cells():
    out = render([{"metric": "headcount"}])
    assert "| headcount |  |  |" in out


def test_custom_columns_override_default():
    out = render([{"x": "1", "y": "2"}], columns=("x", "y"))
    assert "| x | y |" in out
    assert "| 1 | 2 |" in out
