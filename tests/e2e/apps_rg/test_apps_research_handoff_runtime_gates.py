"""Deterministic cross-app proof: apps_research Exit-authorized brief reaches apps_rg U0."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps_rg.integrations.apps_research_bridge import MockAppsResearchBridge
from apps_rg.integrations.managed_research_delegation import (
    RequestForResumeBriefing,
    ResumeBriefingReady,
    dispatch_resume_research_briefing,
)
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg


def test_exit_authorized_briefing_reaches_apps_rg_u0(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_ENFORCE_CANONICAL_RESEARCH_EXIT_IN_TESTS", "1")

    jd_text = "Lead partner solution architecture and enterprise Claude adoption."
    bridge = MockAppsResearchBridge(
        confidence_score=0.91,
        artifact_runs_root=tmp_path / "producer_runs",
    )
    request = RequestForResumeBriefing(
        request_id="req-cross-app",
        run_id="rg-run-cross-app",
        trace_id="trace-cross-app",
        company_name="Anthropic",
        job_title="Manager Applied AI Architecture Partnerships",
        research_authorized=True,
        job_description_text=jd_text,
    )

    outcome = dispatch_resume_research_briefing(request, bridge=bridge)

    assert isinstance(outcome, ResumeBriefingReady)
    briefing_path = Path(outcome.research_briefing_path)
    assert briefing_path.is_file()
    assert (
        outcome.apps_research_handoff_envelope["exit_authorization"]["x3_code"]
        == "X3D_ALLOW_FINISH"
    )
    assert outcome.apps_research_handoff_envelope["schema_version"] == (
        "apps_research.apps_rg_handoff.v2"
    )

    ingress = SimpleNamespace(
        app_payload={
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "target_company": "Anthropic",
            "target_role": "Manager Applied AI Architecture Partnerships",
            "target_level": "Manager",
            "source_resume_text": "Candidate resume text.",
            "job_description_text": jd_text,
            "briefing_artifact_ref": str(briefing_path),
            "manual_brief_path": str(briefing_path),
            "auto_research_internal": True,
            "research_via": "apps_research",
            "user_constraints": {},
            "output_preferences": {},
        },
        request_id=request.request_id,
        run_id=request.run_id,
        trace_id=request.trace_id,
        tenant_id=request.tenant_id,
        app_id="apps_rg",
    )

    validated = u0_validate_apps_rg(ingress, allow_missing_profiles=True)

    assert validated.app_payload["briefing_artifact_ref"] == str(briefing_path)
    assert validated.app_payload["manual_brief_path"] == str(briefing_path)
    assert validated.app_payload["target_company"] == "Anthropic"
    assert validated.app_payload["target_role"] == (
        "Manager Applied AI Architecture Partnerships"
    )
