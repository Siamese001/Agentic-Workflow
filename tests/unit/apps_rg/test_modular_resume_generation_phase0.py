"""Phase 0 — modular R4 shared API (no GenerateResumeStep, no SSOT flip)."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

import pytest

from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult
from apps_rg.l2_recipe.modular_resume_generation import (
    LANE_DISPATCH_MODULES,
    ModularResumeInputPackage,
    ModularResumeProfile,
    run_modular_resume_generation,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES


def test_lane_modules_match_seven_dispatch_modules() -> None:
    assert len(LANE_DISPATCH_MODULES) == 7
    assert LANE_DISPATCH_MODULES[0].endswith("headline_lane")


def test_ok_for_recipe_context_contract() -> None:
    good = ModularR4GenerationResult(
        generated_resume={"schema_version": "master_resume_v2.16"},
        section_provider_calls_ref="modular_r4/section_provider_calls.json",
        section_output_refs={},
        merge_receipt_ref="modular_r4/final_resume_assembly/final_resume_receipt.json",
        schema_validation_receipt_ref="modular_r4/rg_output_schema_validation_receipt.json",
        final_schema_valid=True,
        decisive_status="PASS",
        failure_reason="",
        provider_call_count=0,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=True,
        final_merge_attempted=True,
    )
    assert good.ok_for_recipe_context() is True
    bad = ModularR4GenerationResult(
        generated_resume=None,
        section_provider_calls_ref="x",
        section_output_refs={},
        merge_receipt_ref=None,
        schema_validation_receipt_ref="y",
        final_schema_valid=False,
        decisive_status="PARTIAL",
        failure_reason="x",
        provider_call_count=0,
        locked_sections_provider_calls_detected=False,
    )
    assert bad.ok_for_recipe_context() is False


def test_run_modular_honors_artifact_dir_under_repo() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"phase0_pytest_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    fx = repo / "tests" / "_fixtures" / "rg_output_phase0_min_valid.json"
    prof = ModularResumeProfile()
    inp = ModularResumeInputPackage(repo_root=repo, rg_output_fixture_path=fx)
    res = run_modular_resume_generation(inp, art, "pytest_phase0", prof)
    assert res.decisive_status == "PASS"
    assert res.merge_receipt_ref is not None
    assert (art / res.section_provider_calls_ref).is_file()
    assert (art / res.schema_validation_receipt_ref).is_file()
    assert (art / res.merge_receipt_ref).is_file()
    sr = json.loads((art / res.schema_validation_receipt_ref).read_text(encoding="utf-8"))
    assert sr.get("final_schema_valid") is True
    assert res.ok_for_recipe_context() is True
    assert (art / "modular_r4").is_dir()


def test_artifact_dir_outside_repo_rejected() -> None:
    repo = find_repo_root()
    fx = repo / "tests" / "_fixtures" / "rg_output_phase0_min_valid.json"
    bad_art = Path(sys.executable).parent / f"_phase0_bad_art_{uuid.uuid4().hex[:8]}"
    with pytest.raises(ValueError, match="artifact_dir must be inside"):
        run_modular_resume_generation(
            ModularResumeInputPackage(repo_root=repo, rg_output_fixture_path=fx),
            bad_art,
            "bad",
            ModularResumeProfile(),
        )


def test_section_provider_calls_has_seven_lanes() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"phase0_pytest_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    fx = repo / "tests" / "_fixtures" / "rg_output_phase0_min_valid.json"
    res = run_modular_resume_generation(
        ModularResumeInputPackage(repo_root=repo, rg_output_fixture_path=fx),
        art,
        "t2",
        ModularResumeProfile(),
    )
    data = json.loads((art / res.section_provider_calls_ref).read_text(encoding="utf-8"))
    assert len(data["records"]) == 7
    lanes = {r["section_lane"] for r in data["records"]}
    assert lanes == set(GENERATED_LANES)


def test_lane_names_align_with_generated_lanes_order() -> None:
    def _lane_tail(mod: str) -> str:
        tail = mod.rsplit(".", 1)[-1]
        if tail.endswith("_lane"):
            return tail[: -len("_lane")]
        return tail.replace("_dispatch", "")

    tails = tuple(_lane_tail(m) for m in LANE_DISPATCH_MODULES)
    assert tails == GENERATED_LANES
