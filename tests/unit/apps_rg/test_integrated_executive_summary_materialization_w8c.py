"""W8C — executive_summary must materialize under integrated ``modular_r4/sections``."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from apps_rg.l2_recipe.modular_resume_generation import (
    GENERATED_LANES,
    ModularResumeInputPackage,
    ModularResumeProfile,
    run_modular_resume_generation,
)
from apps_rg.l2_recipe.modular_lane_adapter import (
    ModularLaneTargeting,
    phase1_jd_dispatch_refs,
    phase1_manual_brief_for_dispatch,
)
from apps_rg.runtime.briefing_resolution import BriefingResolutionError, resolve_briefing_for_lanes
from apps_rg.runtime.integrated_lane_evidence_packaging import (
    INTEGRATED_LANE_PRE_RUN_FAILURE_ARTIFACT,
    discover_integrated_modular_lane_bundle_refs,
    emit_integrated_lane_pre_run_failure,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES as ROLLUP_GENERATED_LANES
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.orchestration.canonical_dispatch import (
    _read_optional_brief,
    _run_executive_summary_lane_from_cli,
)


def test_generated_lanes_registry_includes_executive_summary() -> None:
    assert "executive_summary" in GENERATED_LANES
    assert "executive_summary" in ROLLUP_GENERATED_LANES
    assert GENERATED_LANES.index("executive_summary") == 1


def test_phase1_manual_brief_for_dispatch_prefers_filesystem_ref() -> None:
    repo = find_repo_root()
    brief_path = (
        repo / "apps_rg" / "config" / "targeting" / "brown_brown_svp_it_strategy_innovation_briefing.md"
    )
    targeting = ModularLaneTargeting(
        target_company="Brown & Brown",
        target_title="SVP IT Strategy",
        briefing_text="inline / text / with slashes",
        briefing_ref_used=str(brief_path.resolve()),
    )
    assert phase1_manual_brief_for_dispatch(targeting) == str(brief_path.resolve())
    jd_ref, jd_txt = phase1_jd_dispatch_refs(
        ModularLaneTargeting(
            jd_text="Role body",
            jd_ref_used=str(
                (
                    repo / "apps_rg" / "config" / "targeting" / "brown_brown_svp_it_strategy_innovation_jd.txt"
                ).resolve()
            ),
        )
    )
    assert jd_ref.endswith("brown_brown_svp_it_strategy_innovation_jd.txt")
    assert jd_txt == ""


def test_read_optional_brief_preserves_inline_text_with_slashes() -> None:
    inline = "Brown & Brown (NYSE: BRO) — Q1 2026 / remote / Plano, TX"
    assert _read_optional_brief(inline) == inline


def test_resolve_briefing_rejects_path_like_inline_under_require_run_specific() -> None:
    inline = "segment A / segment B / metrics dashboard"
    with pytest.raises(BriefingResolutionError, match="does not exist"):
        resolve_briefing_for_lanes(briefing_artifact_ref=inline, require_run_specific=True)


def test_executive_summary_dispatch_uses_inline_briefing_not_path_resolver() -> None:
    captured: dict[str, str] = {}

    def _fake_run(args, *, artifact_dir_override=None):
        captured["briefing"] = str(args.briefing)
        return {
            "artifact_dir": str(artifact_dir_override or Path("/tmp/exec_summary_test")),
            "runtime_payload": {"run_id": "exec_summary_test_run"},
            "x3": SimpleNamespace(pass_=True, x3_code="X3_ALLOW"),
            "output_text": "summary text",
        }

    inline_brief = "NYSE: BRO / IT strategy / innovation incubation"
    with patch(
        "apps_rg.runtime.sections.executive_summary_lane.run_executive_summary_execution",
        side_effect=_fake_run,
    ):
        out = _run_executive_summary_lane_from_cli(
            target_company="Brown & Brown",
            target_role="SVP IT Strategy",
            target_level="",
            jd="",
            job_description_ref="",
            job_description_text="Senior leader for enterprise architecture / AI platforms.",
            manual_brief=inline_brief,
            resume_path="",
            source_resume_text="",
            generation_mode="strategic_tailor",
            artifact_dir="",
            lane_provider="qwen_vllm",
            lane_provider_resolution_source="CLI_OVERRIDE",
            lane_temperature=0.45,
            lane_x1d_judges="gemini_pro",
            lane_mock_judges=True,
        )

    assert out.get("fault") != "missing_targeting_inputs"
    assert captured.get("briefing") == inline_brief


def test_emit_integrated_lane_pre_run_failure_writes_sections_tree() -> None:
    repo = find_repo_root()
    integrated = repo / "artifacts" / "apps_rg" / "runs" / f"w8c_fail_{uuid.uuid4().hex[:8]}"
    sections = integrated / "modular_r4" / "sections"
    sections.mkdir(parents=True, exist_ok=True)
    emit_integrated_lane_pre_run_failure(
        sections_root=sections,
        integrated_dir=integrated,
        repo_root=repo,
        lane_id="executive_summary",
        blocker="missing_targeting_inputs",
        dispatch_result={"fault": "missing_targeting_inputs", "exit_status": "error"},
        lane_exec_status="dispatch_error:missing_targeting_inputs",
    )
    fail_path = sections / "executive_summary" / INTEGRATED_LANE_PRE_RUN_FAILURE_ARTIFACT
    assert fail_path.is_file()
    doc = json.loads(fail_path.read_text(encoding="utf-8"))
    assert doc["lane_id"] == "executive_summary"
    assert doc["blocker"] == "missing_targeting_inputs"
    assert doc["status"] == "PRE_RUN_BLOCKED"


def test_discover_run_links_uses_pre_run_failure_blocker_not_phase1_only() -> None:
    repo = find_repo_root()
    integrated = repo / "artifacts" / "apps_rg" / "runs" / f"w8c_links_{uuid.uuid4().hex[:8]}"
    sections = integrated / "modular_r4" / "sections"
    sections.mkdir(parents=True, exist_ok=True)
    emit_integrated_lane_pre_run_failure(
        sections_root=sections,
        integrated_dir=integrated,
        repo_root=repo,
        lane_id="executive_summary",
        blocker="missing_targeting_inputs",
    )
    refs = discover_integrated_modular_lane_bundle_refs(repo, integrated)
    exec_row = next(r for r in refs if r["lane"] == "executive_summary")
    assert exec_row["status"] == "NOT_RUN"
    assert exec_row["missing_reason"] == "missing_targeting_inputs"
    assert exec_row.get("pre_run_failure_ref")


def test_phase1_attempts_executive_summary_under_modular_sections_root() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"w8c_phase1_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    inline_brief = "Brown & Brown / SVP IT Strategy / innovation path with / slashes"
    targeting = ModularLaneTargeting(
        target_company="Brown & Brown",
        target_title="SVP IT Strategy",
        jd_text="Role requires enterprise architecture and AI incubation.",
        briefing_text=inline_brief,
    )

    def _fake_lane(*, section: str, **kwargs):
        if section != "executive_summary":
            return {
                "exit_status": "success",
                "fault": "",
                "artifact_dir": str(
                    art / "modular_r4" / "sections" / section / "real" / f"{section}_stub"
                ),
            }
        run_dir = art / "modular_r4" / "sections" / "executive_summary" / "real" / "exec_summary_stub"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "l2_output.json").write_text(
            json.dumps(
                {
                    "section_id": "executive_summary",
                    "runtime_generation_status": "REAL_LLM",
                    "provider_requested": "qwen_vllm",
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "provider_request.json").write_text(
            json.dumps({"provider_requested": "qwen_vllm"}),
            encoding="utf-8",
        )
        (run_dir / "x3_disposition.json").write_text(
            json.dumps({"x3_code": "X3_ALLOW"}),
            encoding="utf-8",
        )
        (run_dir / "x2_gate_outputs.json").write_text(
            json.dumps({"x2_passed": 1, "x2_failed": 0}),
            encoding="utf-8",
        )
        (run_dir / "x1d_llm_judge_outputs.json").write_text("{}", encoding="utf-8")
        (run_dir / "l6_shadow_eval_package.json").write_text(
            json.dumps({"offline_only": True}),
            encoding="utf-8",
        )
        ptr = {
            "run_id": "exec_summary_stub",
            "run_dir": str(run_dir.relative_to(repo)).replace("\\", "/"),
        }
        lane_base = art / "modular_r4" / "sections" / "executive_summary"
        lane_base.mkdir(parents=True, exist_ok=True)
        (lane_base / "latest_successful_real_run.json").write_text(
            json.dumps(ptr),
            encoding="utf-8",
        )
        return {"exit_status": "success", "fault": "", "artifact_dir": str(run_dir)}

    with patch(
        "apps_rg.l2_recipe.modular_resume_generation.run_canonical_apps_rg_from_cli_primitives",
        side_effect=_fake_lane,
    ):
        res = run_modular_resume_generation(
            ModularResumeInputPackage(repo_root=repo),
            art,
            "w8c_phase1",
            ModularResumeProfile(
                phase1_invoke_real_lanes=True,
                run_phase0_synthetic_assembly=False,
                validate_rg_output_fixture=False,
            ),
            lane_targeting=targeting,
        )

    exec_dir = art / "modular_r4" / "sections" / "executive_summary"
    assert exec_dir.is_dir()
    assert (exec_dir / "real" / "exec_summary_stub" / "l2_output.json").is_file()
    calls = json.loads((art / res.section_provider_calls_ref).read_text(encoding="utf-8"))
    exec_rec = next(r for r in calls["records"] if r["section_lane"] == "executive_summary")
    assert exec_rec.get("provider_call_attempted") is True
    assert exec_rec.get("decisive_reason_code") != "PHASE1_NO_RUN_DIR"
