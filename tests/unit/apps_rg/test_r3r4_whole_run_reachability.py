"""R3R4 whole-run reachability with apps_research delegation disabled."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.dispatch.spine_stage_receipts import (
    FILENAME_DELEGATED_BRIEFING,
    FILENAME_RESEARCH_BRIDGE_REQUEST,
    FILENAME_RESEARCH_BRIDGE_RESPONSE,
    FILENAME_SPINE_MANIFEST,
)
from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
    ROUTE_FAMILY_R3R4,
    briefing_input_present,
    research_delegation_enabled,
    should_delegate_apps_research,
)


def test_research_enabled_when_brief_missing_and_auto_research_on() -> None:
    assert not research_delegation_enabled(auto_research_internal=True, research_via=None)
    assert not should_delegate_apps_research(
        route_family=ROUTE_FAMILY_R3R4,
        manual_brief="",
        auto_research_internal=True,
        research_via=None,
    )


def test_no_delegation_when_brief_present(tmp_path: Path) -> None:
    brief = tmp_path / "brief.txt"
    brief.write_text("Existing briefing content.\n", encoding="utf-8")
    assert briefing_input_present(str(brief))
    assert not should_delegate_apps_research(
        route_family=ROUTE_FAMILY_R3R4,
        manual_brief=str(brief),
        auto_research_internal=True,
        research_via=None,
    )


def test_whole_run_r3r4_reachable_without_research_delegation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-1"
        request_id = "req-1"
        x3_disposition = "X3A"
        fault = "L2_EXECUTION_ERROR:AggregationPreflightError:test"
        terminal_r5 = False

    from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

    def _fake_spine(**kwargs: object) -> _FakeResult:
        art = Path(kwargs["artifact_dir"])
        art.mkdir(parents=True, exist_ok=True)
        (art / "r4_run_manifest.json").write_text(
            json.dumps({"chain_kind": "R4_SINGLE_ACTION", "route_family": "R4_SINGLE_ACTION"}),
            encoding="utf-8",
        )
        return _FakeResult()

    monkeypatch.setattr(orch, "run_integrated_single_action_spine", _fake_spine)
    monkeypatch.setattr(
        "apps_rg.cache.whole_run_entrypoint_preflight.run_whole_run_cache_preflight",
        lambda **kwargs: WholeRunCachePreflightOutcome(
            entrypoint="canonical_dispatch",
            generation_required=True,
        ),
    )
    monkeypatch.setattr(orch, "emit_integrated_run_bundle_index", lambda *a, **k: None)
    monkeypatch.setattr(
        "apps_rg.cache.whole_run_entrypoint_preflight.maybe_ingest_r1b_post_exit",
        lambda **k: None,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.full_resume_review_bundle.emit_full_resume_review_bundle",
        lambda run_root: run_root / "review_bundle.zip",
    )
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_whole_run_cache_preflight_artifact",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_cache_miss_receipt",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        orch,
        "_default_artifact_dir",
        lambda explicit: tmp_path / "full_resume_test01",
    )

    brief = tmp_path / "brief.txt"
    brief.write_text("Existing authoritative briefing.\n", encoding="utf-8")

    result = orch.run_whole_run_with_route_governance(
        target_company="Brown & Brown",
        target_role="SVP IT Strategy",
        jd="Target JD text for testing.",
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "full_resume_test01"),
    )

    assert result["route_family"] == ROUTE_FAMILY_R3R4
    assert result["research_delegation_executed"] is False
    art = Path(result["artifact_dir"])
    assert (art / FILENAME_SPINE_MANIFEST).is_file()
    assert not (art / FILENAME_RESEARCH_BRIDGE_REQUEST).exists()
    assert not (art / FILENAME_RESEARCH_BRIDGE_RESPONSE).exists()
    assert not (art / FILENAME_DELEGATED_BRIEFING).exists()

    spine = json.loads((art / FILENAME_SPINE_MANIFEST).read_text(encoding="utf-8"))
    assert spine["proof_authority"] == "spine_run_manifest.json"
    assert spine["draft_leg_proof_scope"] == "draft_leg_only"
    assert spine["route_family"] == ROUTE_FAMILY_R3R4

    r4 = json.loads((art / "r4_run_manifest.json").read_text(encoding="utf-8"))
    assert r4.get("apps_rg_proof_scope") == "draft_leg_only"
    assert r4.get("apps_rg_orchestration_manifest_ref") == FILENAME_SPINE_MANIFEST

    route_decision = result["route_decision"]
    assert route_decision["route_family"] == ROUTE_FAMILY_R3R4
    assert route_decision["briefing_input_present"] is True
