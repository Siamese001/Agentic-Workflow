"""apps-test-model: APP CONTRACT.

R3R4 whole-run reachability with apps_research delegation enabled.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.dispatch.spine_stage_receipts import (
    FILENAME_DELEGATED_BRIEFING,
    FILENAME_RESEARCH_BRIDGE_REQUEST,
    FILENAME_RESEARCH_BRIDGE_RESPONSE,
    FILENAME_SPINE_MANIFEST,
)
from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
    ROUTE_FAMILY_R3R4,
    apps_research_handoff_authorized,
    briefing_input_present,
    research_delegation_enabled,
    should_delegate_apps_research,
)
from apps_rg.runtime.section_failure_forensics import E2E_SECTION_FORENSICS_GATE_ID


def test_research_enabled_when_brief_missing_and_auto_research_on() -> None:
    assert research_delegation_enabled(auto_research_internal=True, research_via=None)
    assert should_delegate_apps_research(
        route_family=ROUTE_FAMILY_R3R4,
        manual_brief="",
        auto_research_internal=True,
        research_via=None,
    )


def _write_authorized_apps_research_handoff(tmp_path: Path) -> tuple[Path, Path]:
    brief_text = "Fresh apps_research handoff briefing for route-decision pytest."
    jd_text = "Target JD text for route-decision pytest."
    brief = tmp_path / "briefing.md"
    brief.write_text(brief_text, encoding="utf-8")
    jd = tmp_path / "jd.txt"
    jd.write_text(jd_text, encoding="utf-8")
    brief_sha = hashlib.sha256(brief_text.encode("utf-8")).hexdigest()
    jd_sha = hashlib.sha256(jd_text.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    envelope = {
        "schema_version": "apps_research.apps_rg_briefing_envelope.v1",
        "producer_app": "apps_research",
        "consumer_app": "apps_rg",
        "run_id": "research-run-route-pytest",
        "target_company": "Anthropic",
        "target_role": "Manager Applied AI Architecture Partnerships",
        "generated_at_utc": now.isoformat(),
        "expires_at_utc": (now + timedelta(days=7)).isoformat(),
        "dry_run": False,
        "stub_detected": False,
        "is_stale": False,
        "handoff_eligible": True,
        "brief_sha256": brief_sha,
        "jd_sha256": jd_sha,
        "apps_research_x1_x3_authorization": {
            "schema_version": "apps_research.apps_rg_handoff_x1_x3_authorization.v1",
            "run_id": "research-run-route-pytest",
            "brief_sha256": brief_sha,
            "jd_sha256": jd_sha,
            "x1": {"gate_id": "X1_TARGETING_BRIEF_CONTRACT", "status": "PASS"},
            "x2": {
                "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
                "status": "PASS",
                "score": 0.91,
                "threshold": 0.75,
                "judge_name": "gemini_pro",
                "judge_provider": "gemini_pro",
                "judge_model": "gemini-3.1-pro-preview",
                "model_backed": True,
                "provider_status": "MODEL_BACKED_PASS",
            },
            "x3": {
                "gate_id": "X3_HANDOFF_AUTHORIZATION",
                "status": "PASS",
                "disposition": "ALLOW",
            },
        },
    }
    (tmp_path / "apps_research_briefing_envelope.json").write_text(
        json.dumps(envelope, indent=2),
        encoding="utf-8",
    )
    return brief, jd


def test_no_delegation_when_auto_research_disabled_and_brief_present(tmp_path: Path) -> None:
    brief = tmp_path / "brief.txt"
    brief.write_text("Existing briefing content.\n", encoding="utf-8")
    assert briefing_input_present(str(brief))
    assert not should_delegate_apps_research(
        route_family=ROUTE_FAMILY_R3R4,
        manual_brief=str(brief),
        auto_research_internal=False,
        research_via=None,
    )


def test_auto_research_static_brief_requires_delegation() -> None:
    brief = Path("apps_rg/config/targeting/brief_anthropic_partnerships_2026.json")
    assert briefing_input_present(str(brief))
    assert should_delegate_apps_research(
        route_family=ROUTE_FAMILY_R3R4,
        manual_brief=str(brief),
        auto_research_internal=True,
        research_via=None,
        jd_ref="apps_rg/config/targeting/jd_anthropic_partnerships_2026.json",
    )


def test_auto_research_authorized_handoff_skips_delegation(tmp_path: Path) -> None:
    brief, jd = _write_authorized_apps_research_handoff(tmp_path)
    assert apps_research_handoff_authorized(str(brief), jd_ref=str(jd))
    assert not should_delegate_apps_research(
        route_family=ROUTE_FAMILY_R3R4,
        manual_brief=str(brief),
        auto_research_internal=True,
        research_via=None,
        jd_ref=str(jd),
    )


def test_whole_run_static_json_is_replaced_by_delegated_brief(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-static-json"
        request_id = "req-static-json"
        x3_disposition = "X3A"
        fault = "L2_EXECUTION_ERROR:test"
        terminal_r5 = False

    from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

    captured: dict[str, object] = {}

    def _fake_spine(**kwargs: object) -> _FakeResult:
        captured["raw_request"] = kwargs["raw_request"]
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
    monkeypatch.setattr(orch, "_default_artifact_dir", lambda explicit: tmp_path / "static_json_run")

    brief_json = Path("apps_rg/config/targeting/brief_anthropic_partnerships_2026.json")
    jd_json = Path("apps_rg/config/targeting/jd_anthropic_partnerships_2026.json")
    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd_json),
        manual_brief=str(brief_json),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "static_json_run"),
    )

    raw_request = captured["raw_request"]
    assert isinstance(raw_request, dict)
    assert result["route_decision"]["research_delegation_executed"] is True
    assert raw_request["manual_brief"].endswith("research\\delegated_briefing.txt") or raw_request[
        "manual_brief"
    ].endswith("research/delegated_briefing.txt")
    assert raw_request["manual_brief"] != str(brief_json)
    assert raw_request["briefing_artifact_ref"] == raw_request["manual_brief"]


def test_whole_run_research_failure_fails_closed_with_manual_brief(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-research-fallback"
        request_id = "req-research-fallback"
        x3_disposition = "X3A"
        fault = "L2_EXECUTION_ERROR:test"
        terminal_r5 = False

    from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

    def _fake_spine(**kwargs: object) -> _FakeResult:
        pytest.fail("draft spine must not run after apps_research failure")

    monkeypatch.setattr(orch, "run_integrated_single_action_spine", _fake_spine)
    monkeypatch.setattr(
        orch,
        "_run_r3r4_research_hop",
        lambda **kwargs: (False, "APPS_RESEARCH_BLOCKED", ""),
    )
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
    monkeypatch.setattr(orch, "_default_artifact_dir", lambda explicit: tmp_path / "fallback_run")

    brief = tmp_path / "manual_brief.md"
    brief.write_text("Manual Anthropic partner briefing with usable targeting context.", encoding="utf-8")
    jd = tmp_path / "jd.txt"
    jd.write_text("Run-specific JD for applied AI architecture partnerships.", encoding="utf-8")
    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd),
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "fallback_run"),
    )

    assert result["exit_status"] == "error"
    assert result["execution_status"] == "failed"
    assert result["fault"] == "APPS_RESEARCH_BLOCKED"
    assert not (tmp_path / "fallback_run" / "research" / "manual_brief_fallback_receipt.json").exists()
    spine = json.loads((tmp_path / "fallback_run" / FILENAME_SPINE_MANIFEST).read_text(encoding="utf-8"))
    route_decision = spine["route_decision"]
    assert route_decision["research_delegation_executed"] is True
    assert route_decision["research_failure"] == "APPS_RESEARCH_BLOCKED"
    assert "research_fallback_to_manual_brief" not in route_decision


def test_whole_run_route_mismatch_fails_closed_when_apps_research_required(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    def _fake_spine(**kwargs: object) -> object:
        pytest.fail("draft spine must not run when apps_research-required routing mismatches")

    def _fake_research_hop(**kwargs: object) -> tuple[bool, str, str]:
        pytest.fail("apps_research hop must not run on a non-R3R4 route family")

    def _simple_route(plan: object) -> SimpleNamespace:
        return SimpleNamespace(
            route_id="R3_SIMPLE_GROUNDED_READ",
            route_family="R3_SIMPLE_GROUNDED_READ",
            execution_form="single_action",
            l3_required=True,
            grounding_required=True,
            route_profile_ref="test://route-profile/simple",
            reason_codes=("pytest_route_mismatch",),
            request_id=getattr(plan, "request_id", "req-route-mismatch"),
            run_id=getattr(plan, "run_id", "run-route-mismatch"),
            trace_id=getattr(plan, "trace_id", "trace-route-mismatch"),
        )

    monkeypatch.setattr(orch, "l0_route_apps_rg", _simple_route)
    monkeypatch.setattr(orch, "run_integrated_single_action_spine", _fake_spine)
    monkeypatch.setattr(orch, "_run_r3r4_research_hop", _fake_research_hop)
    monkeypatch.setattr(orch, "emit_integrated_run_bundle_index", lambda *a, **k: None)
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_whole_run_cache_preflight_artifact",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_cache_miss_receipt",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(orch, "_default_artifact_dir", lambda explicit: tmp_path / "route_mismatch_run")

    brief = tmp_path / "manual_brief.md"
    brief.write_text("Static manual briefing that was not produced by apps_research.", encoding="utf-8")
    jd = tmp_path / "jd.txt"
    jd.write_text("Run-specific JD for applied AI architecture partnerships.", encoding="utf-8")
    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd),
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "route_mismatch_run"),
    )

    assert result["exit_status"] == "error"
    assert result["execution_status"] == "failed"
    assert result["fault"] == "APPS_RESEARCH_ROUTE_MISMATCH"
    assert result["route_family"] == "R3_SIMPLE_GROUNDED_READ"
    spine = json.loads((tmp_path / "route_mismatch_run" / FILENAME_SPINE_MANIFEST).read_text(encoding="utf-8"))
    route_decision = spine["route_decision"]
    assert route_decision["research_delegation_executed"] is False
    assert route_decision["research_failure"] == "APPS_RESEARCH_ROUTE_MISMATCH"
    assert route_decision["research_failure_reason"] == (
        "apps_research_required_without_authorized_handoff_on_R3_SIMPLE_GROUNDED_READ"
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

    brief, jd = _write_authorized_apps_research_handoff(tmp_path)

    result = orch.run_whole_run_with_route_governance(
        target_company="Brown & Brown",
        target_role="SVP IT Strategy",
        jd=str(jd),
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
            "markdown_path": Path(run_root) / "02_section_lane_summary_table.md",
            "bcg_markdown_path": Path(run_root) / "01_BCG_executive_output.md",
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

    brief, jd = _write_authorized_apps_research_handoff(tmp_path)

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd),
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "anthropic_custom_run"),
    )

    art = Path(result["artifact_dir"])
    assert status_calls == [art]
    assert mandatory_calls == [art]
    assert review_calls == [art]
    assert result["bcg_executive_output_md"].endswith("01_BCG_executive_output.md")


def test_whole_run_hard_fails_without_complete_section_forensics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APPS_RG_MOCK_RESEARCH", "1")
    monkeypatch.setenv("APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", "1")

    from apps_rg.runtime.orchestration import r3r4_whole_run_orchestration as orch

    class _FakeResult:
        run_id = "draft-run-missing-forensics"
        request_id = "req-missing-forensics"
        x3_disposition = "X3A"
        fault = "L2_EXECUTION_ERROR:test"
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
        "apps_rg.runtime.mandatory_run_outputs.emit_mandatory_run_outputs",
        lambda run_root, **kwargs: {
            "json_path": Path(run_root) / "APPS_RG_MANDATORY_RUN_OUTPUT.json",
            "markdown_path": Path(run_root) / "02_section_lane_summary_table.md",
            "bcg_markdown_path": Path(run_root) / "01_BCG_executive_output.md",
            "payload": {
                "section_failure_forensics": {
                    "gate_id": E2E_SECTION_FORENSICS_GATE_ID,
                    "required": True,
                    "pass": False,
                    "missing_or_incomplete": [{"section_id": "headline"}],
                }
            },
        },
    )
    monkeypatch.setattr(
        orch,
        "_default_artifact_dir",
        lambda explicit: tmp_path / "full_resume_missing_forensics",
    )

    brief, jd = _write_authorized_apps_research_handoff(tmp_path)

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd),
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "full_resume_missing_forensics"),
    )

    assert result["exit_status"] == "error"
    assert result["execution_status"] == "failed"
    assert result["outcome_authorized"] is False
    assert result["fault"] == E2E_SECTION_FORENSICS_GATE_ID
    assert result["x3_disposition"] == "X3_BLOCK"


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

    brief, jd = _write_authorized_apps_research_handoff(tmp_path)

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd),
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
    output_contract_calls: list[Path] = []

    def _fake_emit_final_resume_product_outputs(run_root: Path, **kwargs: object) -> dict[str, object]:
        root = Path(run_root)
        output_contract_calls.append(root)
        (root / "outputs").mkdir(parents=True, exist_ok=True)
        (root / "outputs" / "resume.docx").write_bytes(b"fake-docx")
        (root / "apps_rg_output_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "apps_rg_output_manifest.v1",
                    "resume_docx_relpath": "outputs/resume.docx",
                    "docx_verified": True,
                    "required_artifacts": {
                        "resume_docx": "verified",
                        "docx_verified": True,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {"status": "PASS", "manifest_path": str(root / "apps_rg_output_manifest.json")}

    def _fake_post_x3(**kwargs: object) -> dict[str, object]:
        art = Path(kwargs["artifact_dir"])
        manifest = json.loads((art / "apps_rg_output_manifest.json").read_text(encoding="utf-8"))
        assert manifest["docx_verified"] is True
        assert manifest["required_artifacts"]["resume_docx"] == "verified"
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
        "apps_rg.runtime.final_resume_outputs.emit_final_resume_product_outputs",
        _fake_emit_final_resume_product_outputs,
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

    brief, jd = _write_authorized_apps_research_handoff(tmp_path)

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd),
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "full_resume_success01"),
    )

    assert result["exit_status"] == "success"
    assert result["outcome_authorized"] is True
    assert output_contract_calls == [tmp_path / "full_resume_success01"]
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

    brief, jd = _write_authorized_apps_research_handoff(tmp_path)

    result = orch.run_whole_run_with_route_governance(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd=str(jd),
        manual_brief=str(brief),
        generation_mode="strategic_tailor",
        auto_research_internal=True,
        artifact_dir=str(tmp_path / "full_resume_no_l6"),
    )

    assert result["exit_status"] == "error"
    assert result["outcome_authorized"] is False
    assert result["fault"] == "l6_shadow_bridge"
