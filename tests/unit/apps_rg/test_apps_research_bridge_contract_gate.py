"""apps-test-model: APP CONTRACT.

apps_rg bridge fail-closed contract gate + delegation tests.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from apps_rg.integrations.apps_research_bridge import (
    AppsResearchBridge,
    MockAppsResearchBridge,
    ResearchResult,
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
    assert result.apps_research_handoff_envelope is not None
    assert (
        result.apps_research_handoff_envelope["schema_version"]
        == "apps_research.apps_rg_handoff.v2"
    )
    assert (
        result.apps_research_handoff_envelope["exit_authorization"]["x3_code"]
        == "X3D_ALLOW_FINISH"
    )


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


class _StaticBridge:
    def __init__(self, result: ResearchResult) -> None:
        self._result = result

    def fetch(self, **_kwargs) -> ResearchResult:
        return self._result


def _persist_mock_result(tmp_path: Path) -> ResearchResult:
    # Exercise the real producer publisher so the positive fixture includes the
    # atomically committed v2 manifest, marker, U0 receipt, and explicit digests.
    return _fetch(
        MockAppsResearchBridge(
            confidence_score=0.9,
            artifact_runs_root=tmp_path / "apps_research",
        )
    )


def test_delegation_fails_closed_without_persisted_briefing() -> None:
    req = RequestForResumeBriefing(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        company_name="Acme Co",
        job_title="SVP IT Strategy",
        research_authorized=True,
    )
    in_memory_only = replace(
        _fetch(MockAppsResearchBridge(confidence_score=0.9)),
        research_artifact_dir="",
        briefing_artifact_path="",
    )
    outcome = dispatch_resume_research_briefing(req, bridge=_StaticBridge(in_memory_only))
    assert isinstance(outcome, ResearchDispatchFailure)
    assert outcome.r5_reason_code == "APPS_RESEARCH_ARTIFACT_MISSING"
    assert "research_artifact_dir" in outcome.detail


def test_delegation_returns_ready_with_persisted_brief(tmp_path: Path) -> None:
    req = RequestForResumeBriefing(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        company_name="Acme Co",
        job_title="SVP IT Strategy",
        research_authorized=True,
    )
    persisted = _persist_mock_result(tmp_path)

    outcome = dispatch_resume_research_briefing(req, bridge=_StaticBridge(persisted))

    assert isinstance(outcome, ResumeBriefingReady)
    assert outcome.briefing_text.strip()
    assert Path(outcome.research_briefing_path).is_file()
    assert Path(outcome.research_artifact_dir).is_dir()
    assert outcome.apps_research_handoff_envelope["schema_version"] == (
        "apps_research.apps_rg_handoff.v2"
    )
    assert set(outcome.apps_research_handoff_envelope["mandatory_gate_receipts"]) == {
        "G5",
        "G6",
        "G7",
        "G21",
        "G24",
        "G26",
    }


@pytest.mark.parametrize(
    "tamper",
    (
        "missing_company_brief",
        "changed_briefing_text",
        "escaped_envelope_path",
        "malformed_envelope",
    ),
)
def test_delegation_rejects_tampered_producer_bundle(
    tmp_path: Path,
    tamper: str,
) -> None:
    persisted = _persist_mock_result(tmp_path)
    run_dir = Path(persisted.research_artifact_dir)
    envelope_path = run_dir / "apps_research_apps_rg_handoff_v2.json"
    if tamper == "missing_company_brief":
        (run_dir / "company_brief.json").unlink()
    elif tamper == "changed_briefing_text":
        Path(persisted.briefing_artifact_path).write_text(
            "Tampered briefing text.\n", encoding="utf-8"
        )
    elif tamper == "escaped_envelope_path":
        envelope = dict(persisted.apps_research_handoff_envelope or {})
        envelope["artifact_manifest"]["artifacts"][0]["artifact_ref"] = str(
            (tmp_path / "outside.md").resolve()
        )
        envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
        persisted = replace(persisted, apps_research_handoff_envelope=envelope)
    else:
        envelope_path.write_text("{not-json", encoding="utf-8")
    req = RequestForResumeBriefing(
        request_id="req-tamper",
        run_id="run-tamper",
        trace_id="trace-tamper",
        company_name="Acme Co",
        job_title="SVP IT Strategy",
        research_authorized=True,
    )

    outcome = dispatch_resume_research_briefing(req, bridge=_StaticBridge(persisted))

    assert isinstance(outcome, ResearchDispatchFailure)
    assert outcome.r5_reason_code == "APPS_RESEARCH_ARTIFACT_MISSING"


def test_delegation_fails_closed_without_handoff_envelope() -> None:
    bridge = MockAppsResearchBridge(confidence_score=0.9)
    bridge._mock_sidecar = lambda _brief: {}  # type: ignore[method-assign]
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
    assert outcome.r5_reason_code == "APPS_RESEARCH_BLOCKED"
    assert "missing_apps_research_handoff_v2" in outcome.detail


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
