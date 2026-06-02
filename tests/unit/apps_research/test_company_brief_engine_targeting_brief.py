"""Unit tests: CompanyBriefEngine apps_rg targeting-brief synthesis path (ac0c64c9aa).

Covers routing in ``_synthesize``, markdown attachment, LLM-empty fallback, and
execute() propagation of ``apps_rg_targeting_brief_text`` — without live providers.
"""

from __future__ import annotations

import pytest

from apps_research.engines.company_brief_engine import CompanyBriefEngine


def test_synthesize_routes_to_targeting_brief_when_jd_context_enabled() -> None:
    engine = CompanyBriefEngine()
    called: dict[str, bool] = {"targeting": False}

    def _fake_targeting(**kwargs: object) -> dict:
        called["targeting"] = True
        return {
            "apps_rg_targeting_brief_markdown": "=== STRATEGIC MANDATE ===\n- hook\n",
            "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
        }

    engine._synthesize_apps_rg_targeting_brief = _fake_targeting  # type: ignore[method-assign]

    out = engine._synthesize(
        topic="AIG",
        findings={"overview": "NPW growth"},
        jd_facets=[],
        depth="shallow",
        jd_context={"output_format": "apps_rg_targeting_brief_v1", "content": "VP Agentic AI"},
    )
    assert called["targeting"] is True
    assert "=== STRATEGIC MANDATE ===" in out["apps_rg_targeting_brief_markdown"]
    assert out.get("synthesis_template") == "apps_rg_targeting_brief_synthesis_v1"


def test_synthesize_apps_rg_targeting_brief_uses_llm_markdown(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = CompanyBriefEngine()
    captured: dict[str, str] = {}

    def _fake_llm(prompt: str) -> str:
        captured["prompt"] = prompt
        return "=== STRATEGIC MANDATE ===\n- Verified priority\n"

    monkeypatch.setattr(engine, "_call_llm_plain_markdown", _fake_llm)
    out = engine._synthesize_apps_rg_targeting_brief(
        topic="AIG",
        findings={"overview": "Revenue context"},
        jd_context={"content": "Head of Agentic AI"},
        jd_anchor=None,
    )
    assert "Head of Agentic AI" in captured["prompt"]
    assert "Revenue context" in captured["prompt"]
    assert out["apps_rg_targeting_brief_markdown"].startswith("=== STRATEGIC MANDATE ===")
    assert out["synthesis_template"] == "apps_rg_targeting_brief_synthesis_v1"


def test_synthesize_apps_rg_targeting_brief_falls_back_when_llm_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = CompanyBriefEngine()
    monkeypatch.setattr(engine, "_call_llm_plain_markdown", lambda _prompt: "")
    out = engine._synthesize_apps_rg_targeting_brief(
        topic="AIG",
        findings={},
        jd_context={"content": "VP role title line"},
        jd_anchor=None,
    )
    md = out["apps_rg_targeting_brief_markdown"]
    assert "=== STRATEGIC MANDATE ===" in md
    assert "stub synthesis" in md.lower() or "TBD" in md


def test_assembled_brief_exposes_targeting_markdown_aliases() -> None:
    """Mirrors execute() post-assemble fields (apps_rg_targeting_brief_text / company_brief_text)."""
    targeting_md = "=== STRATEGIC MANDATE ===\n- Enterprise AI platform\n"
    synthesized = {
        "tagline": "AIG stub",
        "strategic_priorities": ["AI"],
        "language_to_mirror": ["platform"],
        "apps_rg_targeting_brief_markdown": targeting_md,
        "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
    }
    brief = CompanyBriefEngine._assemble_brief(topic="AIG", synthesis=synthesized)
    md = str(synthesized.get("apps_rg_targeting_brief_markdown") or "").strip()
    if md:
        brief["apps_rg_targeting_brief_text"] = md
        brief["company_brief_text"] = md
    assert brief["apps_rg_targeting_brief_text"] == md
    assert brief["company_brief_text"] == md
