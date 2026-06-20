"""Regression test for the apps_research -> U0 -> apps_rg briefing handoff."""

from __future__ import annotations

from pathlib import Path

from apps_rg.integrations.managed_research_delegation import ResumeBriefingReady
from apps_rg.runtime.orchestration.canonical_dispatch import _materialize_fallback_brief


def test_materialize_fallback_brief_uses_apps_research_bridge(tmp_path: Path, monkeypatch) -> None:
    class _FakeBridge:
        pass

    def fake_dispatch_resume_research_briefing(request, *, bridge):
        assert bridge.__class__.__name__ == "_FakeBridge"
        assert request.research_authorized is True
        assert request.company_name == "Acme Co"
        assert request.job_title == "SVP IT Strategy"
        return ResumeBriefingReady(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            briefing_text="Generated company brief for Acme.\n",
            research_run_id="research-12345678",
            research_evidence_count=5,
            confidence_score=0.9,
            research_artifact_dir=str(tmp_path),
            result_hash="sha256:deadbeef",
            evidence_lineage=(),
            dispatch_duration_ms=1.0,
        )

    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.canonical_dispatch.find_repo_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "apps_rg.integrations.apps_research_bridge.AppsResearchBridge",
        lambda capability_ref="apps_research.v1": _FakeBridge(),
    )
    monkeypatch.setattr(
        "apps_rg.integrations.managed_research_delegation.dispatch_resume_research_briefing",
        fake_dispatch_resume_research_briefing,
    )

    brief_path = _materialize_fallback_brief(
        target_company="Acme Co",
        target_role="SVP IT Strategy",
        jd_path=None,
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
    )

    brief_file = Path(brief_path)
    assert brief_file.is_file()
    assert brief_file.read_text(encoding="utf-8") == "Generated company brief for Acme.\n"
