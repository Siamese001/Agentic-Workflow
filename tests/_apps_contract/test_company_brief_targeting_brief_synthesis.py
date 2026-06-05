"""Regression: CompanyBriefEngine apps_rg targeting brief synthesis path (ac0c64c9aa)."""

from __future__ import annotations

from unittest.mock import patch

from apps_research.engines.company_brief_engine import CompanyBriefEngine


def test_synthesize_populates_apps_rg_targeting_brief_markdown_when_format_enabled() -> None:
    engine = CompanyBriefEngine()
    findings = {f"family_{i}": f"finding {i}" for i in range(12)}
    targeting_md = "=== STRATEGIC MANDATE ===\nVP Agentic AI at ExampleCo\n"
    jd_context = {"output_format": "apps_rg_targeting_brief_v1", "content": "VP Agentic AI role"}

    with patch.object(engine, "_call_llm_plain_markdown", return_value=targeting_md):
        synthesized = engine._synthesize(
            topic="ExampleCo",
            findings=findings,
            jd_facets=[],
            depth="COMPANY_BRIEF_STANDARD",
            jd_context=jd_context,
            jd_anchor=None,
        )

    assert synthesized.get("apps_rg_targeting_brief_markdown") == targeting_md.strip()
    assert synthesized.get("synthesis_template") == "apps_rg_targeting_brief_synthesis_v1"
