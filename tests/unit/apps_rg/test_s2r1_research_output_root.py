"""S2R1 Apps Research output-root wiring at the pre-lane boundary."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.integrations.managed_research_delegation import ResearchDispatchFailure
from apps_rg.runtime.dispatch.spine_stage_receipts import (
    FILENAME_RESEARCH_BRIDGE_REQUEST,
    FILENAME_RESEARCH_BRIDGE_RESPONSE,
)
from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch


def _route() -> SimpleNamespace:
    return SimpleNamespace(
        request_id="req-s2r1",
        run_id="run-s2r1",
        trace_id="trace-s2r1",
        route_id=orch.ROUTE_FAMILY_R3R4,
        route_family=orch.ROUTE_FAMILY_R3R4,
        execution_form="MANAGED_WORKFLOW",
        l3_required=True,
        grounding_required=True,
        route_profile_ref="test://s2r1",
        reason_codes=(),
    )


def test_configured_run_output_root_reaches_bridge(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.integrations import managed_research_delegation as delegation

    captured: dict[str, Path] = {}
    bridge = object()

    def bridge_factory(*, artifact_runs_root: Path) -> object:
        captured["root"] = artifact_runs_root
        return bridge

    def block_dispatch(request: object, *, bridge: object) -> ResearchDispatchFailure:
        del request, bridge
        return ResearchDispatchFailure(
            request_id="req-s2r1",
            run_id="run-s2r1",
            trace_id="trace-s2r1",
            r5_reason_code="APPS_RESEARCH_BLOCKED",
            detail="focused publication failure",
            dispatch_duration_ms=1.0,
        )

    monkeypatch.setattr(orch, "_research_bridge", bridge_factory)
    monkeypatch.setattr(delegation, "dispatch_resume_research_briefing", block_dispatch)
    run_root = tmp_path / "active_s2_run"

    ok, reason, brief_path = orch._run_r3r4_research_hop(
        route=_route(),
        validated_request=SimpleNamespace(tenant_id="default"),
        artifact_dir=run_root,
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        job_description_text="Lead partner solution architecture for Claude.",
    )

    expected = (run_root / "apps_research" / "runs").resolve()
    assert not ok
    assert reason == "APPS_RESEARCH_BLOCKED"
    assert brief_path == ""
    assert captured["root"] == expected
    assert expected.is_dir()
    request = json.loads((run_root / FILENAME_RESEARCH_BRIDGE_REQUEST).read_text())
    assert request["artifact_runs_root"] == str(expected)


def test_publication_failure_stops_before_delegated_briefing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.integrations import managed_research_delegation as delegation

    monkeypatch.setattr(orch, "_research_bridge", lambda *, artifact_runs_root: object())
    monkeypatch.setattr(
        delegation,
        "dispatch_resume_research_briefing",
        lambda *_args, **_kwargs: ResearchDispatchFailure(
            request_id="req-s2r1",
            run_id="run-s2r1",
            trace_id="trace-s2r1",
            r5_reason_code="APPS_RESEARCH_BLOCKED",
            detail="PermissionError",
            dispatch_duration_ms=1.0,
        ),
    )
    run_root = tmp_path / "blocked_run"

    ok, _, _ = orch._run_r3r4_research_hop(
        route=_route(),
        validated_request=SimpleNamespace(tenant_id="default"),
        artifact_dir=run_root,
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
    )

    assert not ok
    assert not (run_root / "delegated_briefing.md").exists()
    response = json.loads((run_root / FILENAME_RESEARCH_BRIDGE_RESPONSE).read_text())
    assert response["outcome"] == "ResearchDispatchFailure"


def test_successful_publication_allows_research_stage_to_continue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    run_root = tmp_path / "successful_run"

    ok, reason, brief_path = orch._run_r3r4_research_hop(
        route=_route(),
        validated_request=SimpleNamespace(tenant_id="default"),
        artifact_dir=run_root,
        target_company="Mock Co",
        target_role="SVP IT Strategy",
        job_description_text="Lead enterprise technology strategy.",
    )

    expected_root = (run_root / "apps_research" / "runs").resolve()
    assert ok, reason
    assert reason == "ResumeBriefingReady"
    briefing = Path(brief_path)
    assert briefing.is_file()
    assert briefing.parent.parent == expected_root
    response = json.loads((run_root / FILENAME_RESEARCH_BRIDGE_RESPONSE).read_text())
    assert response["artifact_runs_root"] == str(expected_root)
