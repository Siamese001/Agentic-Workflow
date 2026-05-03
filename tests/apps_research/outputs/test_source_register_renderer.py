"""Tests for apps_research.outputs.source_register_renderer (plan §P2.1)."""

from __future__ import annotations

from apps_research.outputs.source_register_renderer import render


def test_empty_register_returns_placeholder():
    out = render({"source_register": []})
    assert "No sources recorded" in out


def test_three_urls_produce_numbered_references():
    brief = {
        "source_register": [
            {"url": "https://a.example"},
            {"url": "https://b.example"},
            {"url": "https://c.example"},
        ]
    }
    out = render(brief)
    assert "[1]: https://a.example" in out
    assert "[2]: https://b.example" in out
    assert "[3]: https://c.example" in out


def test_dedup_preserves_first_seen_order():
    brief = {
        "source_register": [
            {"url": "https://a.example"},
            {"url": "https://b.example"},
            {"url": "https://a.example"},  # dup
        ]
    }
    out = render(brief)
    assert out.count("[1]: https://a.example") == 1
    assert out.count("[2]: https://b.example") == 1
    assert "[3]:" not in out


def test_diff_stable_output():
    """Same input always produces byte-identical output (plan §P2.1 acceptance)."""
    brief = {"source_register": [{"url": "https://x"}, {"url": "https://y"}]}
    assert render(brief) == render(brief)


def test_plain_string_entries_supported():
    out = render({"source_register": ["https://plain.example"]})
    assert "[1]: https://plain.example" in out


def test_none_register_handled():
    out = render({"source_register": None})
    assert "No sources recorded" in out
