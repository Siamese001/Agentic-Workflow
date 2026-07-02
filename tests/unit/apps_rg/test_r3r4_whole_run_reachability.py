"""R3R4 whole-run reachability with apps_research delegation enabled."""
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
    assert research_delegation_enabled(auto_research_internal=True, research_via=None)
    assert should_delegate_apps_research(
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


def test_whole_run_custom_artifact_dir_emits_output_gates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-custom"
        request_id = "req-custom"
        x3_disposition = "X3A"
        fault = "L2_EXECUTION_ERROR:PoolSelectorUnavailableError:test"
        terminal_r5 = False

    from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

    def _fake_spine(**kwargs: object) -> _FakeResult:
        art = Path(kwargs["artifact_dir"])
        lane = art / "modular_r4" / "sections" / "competencies"
        lane.mkdir(parents=True, exist_ok=True)
        (art / "r4_run_manifest.json").write_text(
            json.dumps({"chain_kind": "R4_SINGLE_ACTION", "route_family": "R4_SINGLE_ACTION"}),
            encoding="utf-8",
        )
        (lane / "integrated_lane_pre_run_failure.json").write_text(
            json.dumps({"blocker": "EXECUTED_X3A"}),
            encoding="utf-8",
        )
        return _FakeResult()

    status_calls: list[Path] = []
    mandatory_calls: list[Path] = []
    review_calls: list[Path] = []

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
        "apps_rg.runtime.full_run_section_status.emit_full_run_section_status",
        lambda run_root, **kwargs: status_calls.append(Path(run_root))
        or {"markdown_path": str(Path(run_root) / "FULL_RUN_SECTION_STATUS.md")},
    )
    monkeypatch.setattr(
        "apps_rg.runtime.mandatory_run_outputs.emit_mandatory_run_outputs",
        lambda run_root, **kwargs: mandatory_calls.append(Path(run_root))
        or {
            "json_path": Path(run_root) / "APPS_RG_MANDATORY_RUN_OUTPUT.json",
            "markdown_path": Path(run_root) / "APPS_RG_MANDATORY_RUN_OUTPUT.md",
            "bcg_markdown_path": Path(run_root) / "BCG_EXECUTIVE_OUTPUT.md",
        },
    )
    monkeypatch.setattr(
        orch,
        "emit_full_resume_review_bundle",
        lambda run_root: review_calls.append(Path(run_root)) or Path(run_root) / "review_bundle.zip",
    )
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_whole_run_cache_preflight_artifact",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_cache_miss_receipt",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(orch, "_default_artifact_dir", lambda explicit: tmp_path / "anthropic_custom_run")

    brief = tmp_path / "brief.txt"
    brief.write_text("Existing authoritative briefing.\n", encoding="utf-8")

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd="Target JD text for testing.",
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "anthropic_custom_run"),
    )

    art = Path(result["artifact_dir"])
    assert status_calls == [art]
    assert mandatory_calls == [art]
    assert review_calls == [art]
    assert result["bcg_executive_output_md"].endswith("BCG_EXECUTIVE_OUTPUT.md")


def test_whole_run_fails_when_exec_summary_judge_not_certified(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-certified-looking"
        request_id = "req-certified-looking"
        x3_disposition = "X3D"
        fault = ""
        terminal_r5 = False

    from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

    def _fake_spine(**kwargs: object) -> _FakeResult:
        art = Path(kwargs["artifact_dir"])
        es_dir = art / "lanes" / "executive_summary"
        es_dir.mkdir(parents=True, exist_ok=True)
        (art / "r4_run_manifest.json").write_text(
            json.dumps({"chain_kind": "R4_SINGLE_ACTION", "route_family": "R4_SINGLE_ACTION"}),
            encoding="utf-8",
        )
        (es_dir / "x3_disposition.json").write_text(
            json.dumps(
                {
                    "x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL",
                    "pass": False,
                    "publish_disposition": "judge_certification_required",
                    "x1d_certified": False,
                    "blocking_judge_ids": ["gemini_pro"],
                }
            ),
            encoding="utf-8",
        )
        (es_dir / "publish_disposition.json").write_text(
            json.dumps(
                {
                    "publish_disposition": "judge_certification_required",
                    "x1d_certified": False,
                    "blocking_judge_ids": ["gemini_pro"],
                }
            ),
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
        lambda explicit: tmp_path / "full_resume_test02",
    )

    brief = tmp_path / "brief.txt"
    brief.write_text("Existing authoritative briefing.\n", encoding="utf-8")

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd="Target JD text for testing.",
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "full_resume_test02"),
    )

    assert result["exit_status"] == "error"
    assert result["execution_status"] == "failed"
    assert result["outcome_authorized"] is False
    assert result["x3_disposition"] == "X3_REVIEW_JUDGE_SOFT_FAIL"
    assert result["executive_summary_certification_block"]["blocking_judge_ids"] == ["gemini_pro"]


def test_whole_run_success_requires_post_x3_uwg_eval_l6(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-success"
        request_id = "req-success"
        x3_disposition = "X3D"
        fault = ""
        terminal_r5 = False

    from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

    def _fake_spine(**kwargs: object) -> _FakeResult:
        art = Path(kwargs["artifact_dir"])
        art.mkdir(parents=True, exist_ok=True)
        (art / "r4_run_manifest.json").write_text(
            json.dumps({"chain_kind": "R4_SINGLE_ACTION", "route_family": "R4_SINGLE_ACTION"}),
            encoding="utf-8",
        )
        (art / "agentic_core_how_trace.json").write_text("{}", encoding="utf-8")
        return _FakeResult()

    post_x3_calls: list[Path] = []

    def _fake_post_x3(**kwargs: object) -> dict[str, object]:
        art = Path(kwargs["artifact_dir"])
        post_x3_calls.append(art)
        return {
            "completed": True,
            "x3_to_uwg_to_eval_to_l6_completed": True,
            "uwg": {"artifacts": {"uwg_commit_receipt": "uwg/uwg_commit_receipt.json"}},
            "apps_eval": {"eval_record_ref": str(art / "apps_eval" / "eval_record.json")},
            "l6_shadow": {"l6_shadow_bridge_ref": str(art / "apps_eval" / "l6_shadow_bridge.json")},
        }

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
        "apps_rg.runtime.full_run_section_status.emit_full_run_section_status",
        lambda *a, **k: {"markdown_path": str(tmp_path / "FULL_RUN_SECTION_STATUS.md")},
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
        "apps_rg.runtime.post_x3_completion.complete_apps_rg_post_x3",
        _fake_post_x3,
    )
    monkeypatch.setattr(
        orch,
        "_default_artifact_dir",
        lambda explicit: tmp_path / "full_resume_success01",
    )

    brief = tmp_path / "brief.txt"
    brief.write_text("Existing authoritative briefing.\n", encoding="utf-8")

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd="Target JD text for testing.",
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "full_resume_success01"),
    )

    assert result["exit_status"] == "success"
    assert result["outcome_authorized"] is True
    assert post_x3_calls == [tmp_path / "full_resume_success01"]
    assert result["uwg_commit_receipt_ref"] == "uwg/uwg_commit_receipt.json"
    assert Path(result["apps_eval_record_ref"]).name == "eval_record.json"
    assert Path(result["apps_eval_record_ref"]).parent.name == "apps_eval"
    assert Path(result["l6_shadow_bridge_ref"]).name == "l6_shadow_bridge.json"
    assert Path(result["l6_shadow_bridge_ref"]).parent.name == "apps_eval"


def test_whole_run_blocks_when_post_x3_l6_bridge_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-no-l6"
        request_id = "req-no-l6"
        x3_disposition = "X3D"
        fault = ""
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
        "apps_rg.runtime.full_run_section_status.emit_full_run_section_status",
        lambda *a, **k: {"markdown_path": str(tmp_path / "FULL_RUN_SECTION_STATUS.md")},
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
        "apps_rg.runtime.post_x3_completion.complete_apps_rg_post_x3",
        lambda **kwargs: {
            "completed": True,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "l6_shadow_bridge",
        },
    )
    monkeypatch.setattr(
        orch,
        "_default_artifact_dir",
        lambda explicit: tmp_path / "full_resume_no_l6",
    )

    brief = tmp_path / "brief.txt"
    brief.write_text("Existing authoritative briefing.\n", encoding="utf-8")

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd="Target JD text for testing.",
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "full_resume_no_l6"),
    )

    assert result["exit_status"] == "error"
    assert result["outcome_authorized"] is False
    assert result["fault"] == "l6_shadow_bridge"
