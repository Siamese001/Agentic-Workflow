"""Regression tests for apps_research brief markdown normalization."""

from __future__ import annotations

import pytest

from apps_research.engines.company_brief_engine import (
    CompanyBriefEngine,
    CompanyBriefUnavailableError,
)
from apps_research.types.apps_rg_targeting_brief_contract import (
    normalize_markdown_brief_text,
    normalize_targeting_brief_text,
    validate_targeting_brief_text,
)

_TARGETING_JD_CONTEXT = {
    "company_name": "Acme Co",
    "output_format": "apps_rg_targeting_brief_v1",
    "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
    "jd_context": {"role": "SVP IT Strategy"},
}

_PASS_X2_RECEIPT = {
    "schema_version": "apps_research.apps_rg_handoff_x2_judge_receipt.v1",
    "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
    "judge_name": "gemini_pro",
    "judge_provider": "gemini_pro",
    "judge_model": "gemini-3.1-pro-preview",
    "threshold": 0.75,
    "model_backed": True,
    "status": "PASS",
    "score": 0.91,
    "verdict": "PASS",
    "provider_status": "MODEL_BACKED_PASS",
}

_VALID_TARGETING_BRIEF = (
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
    "\n=== BUSINESS CONTEXT ===\n"
    "- Operating pressure favors measurable modernization outcomes\n"
)


def test_targeting_normalizer_preserves_jd_dense_bullet_for_rejection() -> None:
    jd = "Lead enterprise data platform strategy for the insurance division."
    draft = (
        "Acme Co (ACME) - SVP IT Strategy targeting brief\n"
        "| SVP IT Strategy | band | Reports to CIO (2026) |\n\n"
        "=== STRATEGIC MANDATE ===\n"
        "- lead enterprise data platform strategy for the insurance division and manage the change while coordinating with architecture and governance teams to keep delivery aligned with the business.\n\n"
        "=== LEADERSHIP ===\n"
        "- The stakeholder map crosses business, technology, and operations.\n\n"
        "=== AI, DATA, PLATFORM, ARCHITECTURE SIGNALS ===\n"
        "- Platform modernization needs to remain measurable and specific.\n"
    )

    normalized = normalize_targeting_brief_text(draft, jd_text=jd)
    validation = validate_targeting_brief_text(normalized, jd_text=jd)

    assert not validation.valid
    assert "jd_restatement_in_bullet" in validation.violations
    assert any(
        str(v).startswith("jd_restatement_in_bullet_text:")
        for v in validation.violations
    )
    assert "lead enterprise data platform strategy" in normalized.lower()
    assert all(len(line) <= 240 for line in normalized.splitlines() if line.strip())


def test_targeting_synthesis_repairs_jd_dense_bullet(monkeypatch) -> None:
    engine = CompanyBriefEngine()
    bad_markdown = (
        "Acme Co (ACME) - SVP IT Strategy targeting brief\n"
        "| SVP IT Strategy | band | Reports to CIO (2026) |\n\n"
        "=== STRATEGIC MANDATE ===\n"
        "- lead enterprise data platform strategy for the insurance division and manage the change while coordinating with architecture and governance teams to keep delivery aligned with the business.\n"
    )
    calls: list[str] = []

    def _fake_llm(prompt: str) -> str:
        calls.append(prompt)
        return _VALID_TARGETING_BRIEF if len(calls) > 1 else bad_markdown

    monkeypatch.setattr(engine, "_call_llm_plain_markdown", _fake_llm)
    monkeypatch.setattr(
        engine,
        "_run_apps_rg_handoff_x2_judge",
        lambda **_kwargs: dict(_PASS_X2_RECEIPT),
    )

    synthesized = engine._synthesize_apps_rg_targeting_brief(
        topic="Acme Co",
        findings={"overview": "Acme is a mid-cap insurer with verified scale."},
        jd_context={
            **_TARGETING_JD_CONTEXT,
            "jd_text": "Lead enterprise data platform strategy for the insurance division.",
        },
        jd_anchor=None,
    )

    assert synthesized["targeting_brief_disposition"] == "SEALED"
    assert len(calls) == 2


def test_consumer_brief_path_normalizes_output(monkeypatch) -> None:
    engine = CompanyBriefEngine()
    long_line = "- " + ("company context and operating pressure " * 12)
    monkeypatch.setattr(
        engine,
        "_call_llm_plain_markdown",
        lambda prompt: (
            "Acme Co briefing\n\n"
            "=== RESEARCH SUMMARY ===\n"
            f"{long_line}\n"
        ),
    )

    synthesized = engine._synthesize_consumer_brief(
        topic="Acme Co",
        findings={"overview": "Acme is a mid-cap insurer with verified scale."},
        jd_context={"company_name": "Acme Co"},
        jd_anchor=None,
        template_id="downstream_research_substrate_v1",
        output_key="downstream_research_substrate_text",
        disposition_key="downstream_research_substrate_disposition",
        block_reason_key="downstream_research_substrate_block_reason",
    )

    assert synthesized.get("downstream_research_substrate_disposition") == "SEALED"
    brief = synthesized["downstream_research_substrate_text"]
    assert brief.strip()
    assert all(len(line) <= 240 for line in brief.splitlines() if line.strip())
    assert normalize_markdown_brief_text(brief, profile="apps_rg") == brief
