"""apps_research targeting-brief grounding fail-closed + hop population tests."""

from __future__ import annotations

import re

import pytest

from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import JudgeResponse
from apps_research.engines.company_brief_engine import (
    CompanyBriefEngine,
    CompanyBriefUnavailableError,
)
from apps_research.integrations.apps_rg_handoff import (
    run_apps_rg_handoff_x2_judge,
    x2_judge_receipt_passes,
)
from apps_research.prompt_assembly.apps_rg_targeting_brief import (
    load_targeting_brief_prompt_template,
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
    # No grounded research → the targeting synthesis must fail immediately.
    engine = CompanyBriefEngine()
    with pytest.raises(
        CompanyBriefUnavailableError,
        match="apps_rg targeting brief blocked",
    ):
        engine._synthesize_apps_rg_targeting_brief(
            topic="Acme Co",
            findings={},  # no grounding
            jd_context=_TARGETING_JD_CONTEXT,
            jd_anchor=None,
        )


def test_synthesis_fails_closed_on_gate_fail() -> None:
    # Even with research, a failing C0 support gate must block the brief.
    engine = CompanyBriefEngine()
    with pytest.raises(
        CompanyBriefUnavailableError,
        match="apps_rg targeting brief blocked",
    ):
        engine._synthesize_apps_rg_targeting_brief(
            topic="Acme Co",
            findings={"overview": "Acme is a mid-cap insurer with verified scale."},
            jd_context=_TARGETING_JD_CONTEXT,
            jd_anchor=None,
            gate_verdict="FAIL",
            gate_reason="insufficient_sources",
        )


def test_synthesis_seals_valid_markdown(monkeypatch) -> None:
    engine = CompanyBriefEngine()
    monkeypatch.setattr(engine, "_call_llm_plain_markdown", lambda prompt: _VALID_MD)
    monkeypatch.setattr(
        engine,
        "_run_apps_rg_handoff_x2_judge",
        lambda **_kwargs: dict(_PASS_X2_RECEIPT),
    )
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
    assert sidecar["generation_provider"] == "external_openai"
    assert sidecar["generation_model"] == "gpt-5.4-mini-2026-03-17"
    assert sidecar["x2_judge_receipt"]["model_backed"] is True


def test_synthesis_fails_closed_on_missing_model_backed_x2(monkeypatch) -> None:
    engine = CompanyBriefEngine()
    monkeypatch.setattr(engine, "_call_llm_plain_markdown", lambda prompt: _VALID_MD)
    monkeypatch.setattr(
        engine,
        "_run_apps_rg_handoff_x2_judge",
        lambda **_kwargs: {
            **_PASS_X2_RECEIPT,
            "status": "FAIL",
            "score": 0.10,
            "provider_status": "MODEL_BACKED_FAIL",
        },
    )
    monkeypatch.setattr(
        engine,
        "_persist_x2_blocked_receipt",
        lambda **_kwargs: "artifact://x2-blocked",
    )
    with pytest.raises(
        CompanyBriefUnavailableError,
        match=rf"X2 judge failed.*{re.escape('diagnostic_ref=artifact://x2-blocked')}",
    ):
        engine._synthesize_apps_rg_targeting_brief(
            topic="Acme Co",
            findings={"overview": "Acme is a mid-cap insurer with verified scale."},
            jd_context=_TARGETING_JD_CONTEXT,
            jd_anchor=None,
        )


def test_synthesis_rejects_invalid_markdown(monkeypatch) -> None:
    engine = CompanyBriefEngine()
    monkeypatch.setattr(
        engine, "_call_llm_plain_markdown", lambda prompt: '{"company": "Acme"}'
    )
    with pytest.raises(
        CompanyBriefUnavailableError,
        match="apps_rg targeting brief rejected",
    ):
        engine._synthesize_apps_rg_targeting_brief(
            topic="Acme Co",
            findings={"overview": "Acme is a mid-cap insurer with verified scale."},
            jd_context=_TARGETING_JD_CONTEXT,
            jd_anchor=None,
        )


class _FlakySerializationJudge:
    def __init__(self) -> None:
        self.calls = 0

    def judge(self, _dimension, _context):
        self.calls += 1
        if self.calls == 1:
            raise GraderError("incomplete JSON object in judge response: '{\"verdict\"'")
        return JudgeResponse(score=0.91, abstain=False, reasoning="clean retry")


class _SemanticFailJudge:
    def __init__(self) -> None:
        self.calls = 0

    def judge(self, _dimension, _context):
        self.calls += 1
        return JudgeResponse(score=0.2, abstain=False, reasoning="insufficient support")


def test_apps_rg_x2_judge_retries_serialization_error_once() -> None:
    judge = _FlakySerializationJudge()

    receipt = run_apps_rg_handoff_x2_judge(
        brief_text=_VALID_MD,
        jd_text="Lead partner architecture.",
        research_notes="Acme has verified partner motion.",
        source_register=[{"family": "overview", "has_content": True}],
        judge=judge,
    )

    assert judge.calls == 2
    assert receipt["status"] == "PASS"
    assert receipt["attempt_count"] == 2
    assert receipt["retry_count"] == 1
    assert receipt["retryable_provider_error"] is True
    assert x2_judge_receipt_passes(receipt)


def test_apps_rg_x2_judge_does_not_retry_semantic_fail() -> None:
    judge = _SemanticFailJudge()

    receipt = run_apps_rg_handoff_x2_judge(
        brief_text=_VALID_MD,
        jd_text="Lead partner architecture.",
        research_notes="Acme has verified partner motion.",
        source_register=[{"family": "overview", "has_content": True}],
        judge=judge,
    )

    assert judge.calls == 1
    assert receipt["status"] == "FAIL"
    assert receipt["provider_status"] == "MODEL_BACKED_FAIL"
    assert receipt["model_backed"] is True
    assert receipt["retry_count"] == 0
    assert not x2_judge_receipt_passes(receipt)


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


def test_company_brief_text_extraction_recovers_nested_targeting_markdown() -> None:
    from apps_research.integrations.governed_research_run import (
        _company_brief_text_from_fec,
    )

    fec_ctx = {
        "research_artifact": {
            "nested": {
                "company_brief": {
                    "apps_rg_targeting_brief_markdown": _VALID_MD,
                    "apps_rg_targeting_brief_sidecar": {"handoff_eligible": True},
                }
            }
        }
    }

    assert _company_brief_text_from_fec(fec_ctx) == _VALID_MD.strip()


def test_synthesis_uses_company_name_not_jd_role() -> None:
    # company_name drives identification; jd_context.role must not become topic.
    engine = CompanyBriefEngine()
    with pytest.raises(
        CompanyBriefUnavailableError,
        match="apps_rg targeting brief blocked",
    ):
        engine._synthesize_apps_rg_targeting_brief(
            topic="Acme Co company briefing for SVP IT Strategy",  # polluted topic
            findings={},
            jd_context={"company_name": "Acme Co", **_TARGETING_JD_CONTEXT},
            jd_anchor=None,
        )
