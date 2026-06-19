"""apps_research targeting-brief grounding fail-closed + hop population tests."""

from __future__ import annotations

import re

from apps_research.engines.company_brief_engine import CompanyBriefEngine
from apps_research.prompt_assembly.apps_rg_targeting_brief import (
    load_targeting_brief_prompt_template,
)

_TARGETING_JD_CONTEXT = {
    "company_name": "Acme Co",
    "output_format": "apps_rg_targeting_brief_v1",
    "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
    "jd_context": {"role": "SVP IT Strategy"},
}


def test_prompt_template_required_format_at_most_17_bullets() -> None:
    text = load_targeting_brief_prompt_template()
    # Count only the REQUIRED FORMAT section's literal "- " example bullets.
    fmt = text.split("REQUIRED FORMAT", 1)[-1].split("VERIFIED RESEARCH NOTES", 1)[0]
    bullets = [ln for ln in fmt.splitlines() if ln.startswith("- ")]
    assert len(bullets) <= 17, f"required format has {len(bullets)} bullets"


_VALID_MD = (
    "Acme Co (ACME) - SVP IT Strategy targeting brief\n"
    "| SVP IT Strategy | band | Reports to CIO (2026) |\n\n"
    "=== STRATEGIC MANDATE ===\n"
    "- Verified mid-cap insurer scaling distribution channels\n"
    "- Role anchors platform consolidation across books\n"
    "- Cloud-core migration shifts spend to data services\n\n"
    "=== LEADERSHIP ===\n"
    "- CEO drives acquisitive growth with integration focus\n"
    "- CIO mandate: unify policy systems on one platform\n\n"
    "=== TECH & AI PLATFORM ===\n"
    "- Mainframe-to-cloud core underway across units\n"
    "- Peers investing in agentic underwriting assistance\n"
)


def test_synthesis_fails_closed_without_research() -> None:
    # No grounded research → the targeting synthesis must NOT emit markdown and
    # must carry a BLOCKED/DEGRADED/REJECTED disposition (no successful stub).
    engine = CompanyBriefEngine()
    synthesized = engine._synthesize_apps_rg_targeting_brief(
        topic="Acme Co",
        findings={},  # no grounding
        jd_context=_TARGETING_JD_CONTEXT,
        jd_anchor=None,
    )
    assert "apps_rg_targeting_brief_markdown" not in synthesized
    assert synthesized.get("targeting_brief_disposition") in {"BLOCKED", "DEGRADED", "REJECTED"}
    assert synthesized.get("targeting_brief_block_reason")


def test_synthesis_fails_closed_on_gate_fail() -> None:
    # Even with research, a failing C0 support gate must block the brief.
    engine = CompanyBriefEngine()
    synthesized = engine._synthesize_apps_rg_targeting_brief(
        topic="Acme Co",
        findings={"overview": "Acme is a mid-cap insurer with verified scale."},
        jd_context=_TARGETING_JD_CONTEXT,
        jd_anchor=None,
        gate_verdict="FAIL",
        gate_reason="insufficient_sources",
    )
    assert "apps_rg_targeting_brief_markdown" not in synthesized
    assert synthesized.get("targeting_brief_disposition") == "BLOCKED"


def test_synthesis_seals_valid_markdown(monkeypatch) -> None:
    engine = CompanyBriefEngine()
    monkeypatch.setattr(engine, "_call_llm_plain_markdown", lambda prompt: _VALID_MD)
    synthesized = engine._synthesize_apps_rg_targeting_brief(
        topic="Acme Co",
        findings={"overview": "Acme is a mid-cap insurer with verified scale."},
        jd_context=_TARGETING_JD_CONTEXT,
        jd_anchor=None,
    )
    assert synthesized.get("targeting_brief_disposition") == "SEALED"
    md = synthesized["apps_rg_targeting_brief_markdown"]
    assert md.strip()
    assert len(re.findall(r"(?m)^- ", md)) <= 17
    sidecar = synthesized["apps_rg_targeting_brief_sidecar"]
    assert sidecar["generation_model"] == "gpt-5.4-mini"
    assert sidecar["generation_token_budget"] == 4096
    assert sidecar["judge_model"] == "gemini-3.1-pro-preview"
    assert sidecar["judge_name"] == "gemini-pro-3.1-preview"


def test_synthesis_rejects_invalid_markdown(monkeypatch) -> None:
    engine = CompanyBriefEngine()
    monkeypatch.setattr(
        engine, "_call_llm_plain_markdown", lambda prompt: '{"company": "Acme"}'
    )
    synthesized = engine._synthesize_apps_rg_targeting_brief(
        topic="Acme Co",
        findings={"overview": "Acme is a mid-cap insurer with verified scale."},
        jd_context=_TARGETING_JD_CONTEXT,
        jd_anchor=None,
    )
    assert "apps_rg_targeting_brief_markdown" not in synthesized
    assert synthesized.get("targeting_brief_disposition") == "REJECTED"


def test_hop_company_brief_adapter_populates_company_brief_key(monkeypatch) -> None:
    # The hop adapter must map execute(context)->{"company_brief": <dict>} and
    # identify the company from company_name, not the JD role. We stub the
    # underlying engine to avoid the (unrelated) seal-step infra wrapper.
    import apps_research.engines.company_brief_engine as cbe_mod
    from apps_research.engines.hop_company_brief_engine import HopCompanyBriefEngine
    from apps_research.types.research_types import ResearchRequest

    captured: dict = {}

    class _FakeEngine:
        def execute(self, engine_input):
            captured.update(engine_input)
            return {
                "company": engine_input["topic"],
                "company_brief_text": _VALID_MD,
                "targeting_brief_disposition": "SEALED",
            }

    monkeypatch.setattr(cbe_mod, "CompanyBriefEngine", _FakeEngine)

    req = ResearchRequest(
        topic="ignored topic",
        mode="brief",
        depth_profile="COMPANY_BRIEF_STANDARD",
        jd_context={"company_name": "Acme Co", "output_format": "apps_rg_targeting_brief_v1"},
    )
    out = HopCompanyBriefEngine().execute({"research_request": req})
    assert "company_brief" in out
    assert out["company_brief"]["company"] == "Acme Co"
    assert out["company_brief"]["company_brief_text"].strip()
    # Topic passed to the engine is the company_name, not the request.topic.
    assert captured["topic"] == "Acme Co"


def test_synthesis_uses_company_name_not_jd_role() -> None:
    # company_name drives identification; jd_context.role must not become topic.
    engine = CompanyBriefEngine()
    synthesized = engine._synthesize_apps_rg_targeting_brief(
        topic="Acme Co company briefing for SVP IT Strategy",  # polluted topic
        findings={},
        jd_context={"company_name": "Acme Co", **_TARGETING_JD_CONTEXT},
        jd_anchor=None,
    )
    # The stub synthesis tagline is built from company_name, not the topic.
    assert "Acme Co" in synthesized.get("tagline", "")
    assert "briefing for SVP" not in synthesized.get("tagline", "")
