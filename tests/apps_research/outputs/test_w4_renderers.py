"""Tests for W4 renderers (plan §P4.1-P4.3)."""

from __future__ import annotations

from apps_research.outputs.long_form_renderer import render as render_long_form
from apps_research.outputs.pe_value_creation_renderer import (
    render as render_pe_bundle,
)
from apps_research.outputs.timeline_renderer import render as render_timeline


# ---------- P4.1 long_form_renderer ----------


def test_long_form_has_at_least_five_h2_sections():
    brief = {
        "company": "Blend360",
        "summary": ["summary line"],
        "strategic_priorities": ["p1", "p2"],
        "customer_profile": ["c1"],
        "capabilities": ["cap1"],
        "market_position": ["m1"],
        "leadership": ["l1"],
        "risks": ["r1"],
        "source_register": [{"url": "https://x"}, {"url": "https://y"}],
    }
    out = render_long_form(brief)
    h2_count = out.count("\n## ")
    assert h2_count >= 5


def test_long_form_includes_sources_footer():
    brief = {
        "company": "Blend360",
        "source_register": [{"url": "https://a"}, {"url": "https://b"}],
    }
    out = render_long_form(brief)
    assert "[1]: https://a" in out
    assert "[2]: https://b" in out


def test_long_form_title_uses_company():
    out = render_long_form({"company": "Blend360"})
    assert out.startswith("# Blend360")


# ---------- P4.2 timeline_renderer ----------


def test_timeline_sorts_events_ascending_by_year():
    events = [
        {"year": 2022, "event": "Series B", "source_url": "https://b"},
        {"year": 2015, "event": "Founded", "source_url": "https://f"},
        {"year": 2019, "event": "Series A", "source_url": "https://a"},
    ]
    out = render_timeline(events, company="Blend360")
    pos_2015 = out.index("2015")
    pos_2019 = out.index("2019")
    pos_2022 = out.index("2022")
    assert pos_2015 < pos_2019 < pos_2022


def test_timeline_empty_placeholder():
    out = render_timeline([])
    assert "No historical events recorded" in out


def test_timeline_events_include_source_links():
    events = [{"year": 2020, "event": "E", "source_url": "https://x"}]
    out = render_timeline(events)
    assert "([source](https://x))" in out


# ---------- P4.3 pe_value_creation_renderer ----------


def test_pe_bundle_has_thesis_levers_risks():
    bundle = {
        "thesis": "Thesis paragraph goes here.",
        "levers": [
            {"text": "Expand enterprise sales", "source_url": "https://l1"},
            {"text": "Invest in agentic AI capabilities", "source_url": "https://l2"},
            {"text": "Grow MSP partner channel", "source_url": "https://l3"},
        ],
        "risks": [
            {"text": "Talent retention", "source_url": "https://r1"},
            {"text": "Commoditization of GenAI consulting", "source_url": "https://r2"},
            {"text": "Margin compression", "source_url": "https://r3"},
        ],
        "source_register": [{"url": "https://l1"}, {"url": "https://r1"}],
    }
    out = render_pe_bundle(bundle, company="Blend360")
    assert "## Thesis" in out
    assert "Thesis paragraph goes here." in out
    # ≥3 levers — each numbered
    assert "1. Expand enterprise sales" in out
    assert "2. Invest in agentic AI capabilities" in out
    assert "3. Grow MSP partner channel" in out
    # ≥3 risks
    assert "1. Talent retention" in out
    assert "2. Commoditization of GenAI consulting" in out
    assert "3. Margin compression" in out


def test_pe_bundle_no_thesis_placeholder():
    out = render_pe_bundle({"levers": [], "risks": []})
    assert "No thesis recorded" in out
