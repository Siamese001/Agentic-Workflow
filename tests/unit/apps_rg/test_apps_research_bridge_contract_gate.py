"""apps_rg bridge fail-closed contract gate + delegation tests."""

from __future__ import annotations

from apps_rg.integrations.apps_research_bridge import (
    AppsResearchBridge,
    MockAppsResearchBridge,
)
from apps_rg.integrations.managed_research_delegation import (
    RequestForResumeBriefing,
    ResearchDispatchFailure,
    ResumeBriefingReady,
    dispatch_resume_research_briefing,
)


def _fetch(bridge: AppsResearchBridge):
    return bridge.fetch(
        company_name="Acme Co",
        job_title="SVP IT Strategy",
        capability_ref="apps_research.v1",
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
    )


def test_mock_bridge_default_brief_passes_contract_gate() -> None:
    result = _fetch(MockAppsResearchBridge(confidence_score=0.9))
    assert not result.is_blocked
    assert result.company_brief_text.strip()
    assert result.briefing_sidecar["handoff_eligible"] is True


def test_bridge_rejects_missing_brief_text() -> None:
    bridge = MockAppsResearchBridge(confidence_score=0.9, company_brief_text=" ")
    # company_brief_text=" " is whitespace → falls back to default valid brief;
    # force genuinely empty by overriding the mock raw output.
    bridge._mock_brief = ""
    result = _fetch(bridge)
    assert result.is_blocked
    assert "missing_company_brief_text" in result.block_reason
    assert result.company_brief_text == ""


def test_bridge_rejects_contract_invalid_brief() -> None:
    bridge = MockAppsResearchBridge(confidence_score=0.9)
    bridge._mock_brief = '{"company": "Acme", "brief": "not markdown"}'
    result = _fetch(bridge)
    assert result.is_blocked
    assert "contract_invalid_company_brief_text" in result.block_reason
    assert result.company_brief_text == ""


def test_delegation_returns_ready_with_valid_brief() -> None:
    req = RequestForResumeBriefing(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        company_name="Acme Co",
        job_title="SVP IT Strategy",
        research_authorized=True,
    )
    outcome = dispatch_resume_research_briefing(
        req, bridge=MockAppsResearchBridge(confidence_score=0.9)
    )
    assert isinstance(outcome, ResumeBriefingReady)
    assert outcome.briefing_text.strip()
    assert outcome.briefing_sidecar["handoff_eligible"] is True


def test_delegation_fails_closed_on_blocked_brief() -> None:
    bridge = MockAppsResearchBridge(confidence_score=0.9)
    bridge._mock_brief = ""
    req = RequestForResumeBriefing(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        company_name="Acme Co",
        job_title="SVP IT Strategy",
        research_authorized=True,
    )
    outcome = dispatch_resume_research_briefing(req, bridge=bridge)
    assert isinstance(outcome, ResearchDispatchFailure)
    assert outcome.r5_reason_code in {"APPS_RESEARCH_BLOCKED", "APPS_RESEARCH_EMPTY"}
