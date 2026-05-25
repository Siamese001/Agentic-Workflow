"""Phase 1 — real in-process lane invocation under modular_r4/sections (mock provider)."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from unittest.mock import patch

from apps_rg.l2_recipe.modular_resume_generation import (
    LANE_DISPATCH_MODULES,
    ModularResumeInputPackage,
    ModularResumeProfile,
    run_modular_resume_generation,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV
from apps_rg.runtime.sections_root_manifest import (
    SECTIONS_ROOT_MANIFEST_FILENAME,
    assert_sections_root_manifest_document_shape,
)


def test_phase1_runs_seven_lanes_mock_provider_no_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"phase1_pytest_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)

    def _stub_lane_dispatch(**kwargs: object) -> dict[str, object]:
        lane = str(kwargs.get("section") or "")
        sections_root = Path(os.environ[MODULAR_R4_SECTIONS_ROOT_ENV])
        run_id = f"pytest_phase1_{lane}"
        run_dir = (sections_root / lane / run_id).resolve()
        run_rel = run_dir.relative_to(repo).as_posix()
        run_dir.mkdir(parents=True, exist_ok=True)
        l2 = {
            "section_id": lane,
            "runtime_generation_status": "REAL_LLM",
            "product_quality_status": "PASS",
        }
        (run_dir / "l2_output.json").write_text(json.dumps(l2), encoding="utf-8")
        (run_dir / "provider_request.json").write_text(
            json.dumps({"provider_requested": "qwen_vllm", "provider_attempted": True}),
            encoding="utf-8",
        )
        (run_dir / "x3_disposition.json").write_text(
            json.dumps({"x3_code": "X3_ALLOW", "pass": True}),
            encoding="utf-8",
        )
        ptr_dir = sections_root / lane
        ptr_dir.mkdir(parents=True, exist_ok=True)
        for ptr_name in ("latest_successful_real_run.json", "latest_real_run.json"):
            (ptr_dir / ptr_name).write_text(
                json.dumps({"run_dir": run_rel.replace("\\", "/")}),
                encoding="utf-8",
            )
        return {"exit_status": 0, "x3_code": "X3_ALLOW"}

    with (
        patch("apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope") as env_call,
        patch(
            "apps_rg.l2_recipe.modular_resume_generation.run_canonical_apps_rg_from_cli_primitives",
            side_effect=_stub_lane_dispatch,
        ),
    ):
        res = run_modular_resume_generation(
            ModularResumeInputPackage(repo_root=repo),
            art,
            "pytest_phase1",
            ModularResumeProfile(
                phase1_invoke_real_lanes=True,
                run_phase0_synthetic_assembly=False,
                validate_rg_output_fixture=False,
            ),
        )
    env_call.assert_not_called()
    assert res.extras.get("real_lane_invocation_attempted") is True
    calls_path = art / res.section_provider_calls_ref
    assert calls_path.is_file()
    raw = json.loads(calls_path.read_text(encoding="utf-8"))
    assert raw["schema_version"] == "apps_rg.section_provider_calls.phase1.v2"
    assert isinstance(raw.get("recipe_lane_policy"), dict)
    assert len(raw["records"]) == 7
    assert {r["section_lane"] for r in raw["records"]} == set(GENERATED_LANES)
    assert all(r.get("section_lane") != "full_resume" for r in raw["records"])
    assert res.locked_sections_provider_calls_detected is False
    sections = art / "modular_r4" / "sections"
    assert sections.is_dir()
    manifest_path = sections / SECTIONS_ROOT_MANIFEST_FILENAME
    assert manifest_path.is_file(), "W4.1 manifest must accompany scoped modular sections root"
    mf_doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert_sections_root_manifest_document_shape(mf_doc)
    assert mf_doc["source_env_var"] == MODULAR_R4_SECTIONS_ROOT_ENV
    for lane in GENERATED_LANES:
        assert (sections / lane).is_dir(), f"missing section tree for {lane}"
    lanes_executed = int(res.extras.get("lanes_executed") or 0)
    assert lanes_executed > 0
    if lanes_executed == len(GENERATED_LANES) and res.merge_receipt_ref is not None:
        assert res.merge_receipt_ref.startswith("modular_r4/")
    # Merged assembler JSON is not full rg_output_schema in Phase 1 — fail closed for recipe.
    assert res.final_schema_valid is False
    assert res.ok_for_recipe_context() is False
    assert res.decisive_status in {"PARTIAL", "FAIL"}
    assert res.extras.get("pass_source") != "fixture_rg_output"


def test_phase1_no_l2_envelope_import() -> None:
    """Regression: modular_resume_generation must not import l2 envelope."""
    src = Path("apps_rg/l2_recipe/modular_resume_generation.py")
    text = src.read_text(encoding="utf-8")
    assert "l2_envelope_adapter" not in text


def test_fixture_pass_not_used_as_phase1_pass_source() -> None:
    repo = find_repo_root()
    fx = repo / "tests" / "_fixtures" / "rg_output_phase0_min_valid.json"
    art0 = repo / "artifacts" / "apps_rg" / "runs" / f"phase1_cmp0_{uuid.uuid4().hex[:10]}"
    art0.mkdir(parents=True, exist_ok=True)
    r0 = run_modular_resume_generation(
        ModularResumeInputPackage(repo_root=repo, rg_output_fixture_path=fx),
        art0,
        "cmp0",
        ModularResumeProfile(),
    )
    assert r0.decisive_status == "PASS"
    assert r0.extras.get("pass_source") == "fixture_rg_output"

    art1 = repo / "artifacts" / "apps_rg" / "runs" / f"phase1_cmp1_{uuid.uuid4().hex[:10]}"
    art1.mkdir(parents=True, exist_ok=True)
    r1 = run_modular_resume_generation(
        ModularResumeInputPackage(repo_root=repo, rg_output_fixture_path=fx),
        art1,
        "cmp1",
        ModularResumeProfile(
            phase1_invoke_real_lanes=True,
            run_phase0_synthetic_assembly=False,
            validate_rg_output_fixture=True,
        ),
    )
    assert r1.extras.get("pass_source") != "fixture_rg_output"
    assert r1.final_schema_valid is False


def test_modular_env_scoped_to_run() -> None:
    """Env var must not leak after run_modular_resume_generation returns."""
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"phase1_env_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    prior = os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV)
    run_modular_resume_generation(
        ModularResumeInputPackage(repo_root=repo),
        art,
        "env",
        ModularResumeProfile(
            phase1_invoke_real_lanes=True,
            run_phase0_synthetic_assembly=False,
            validate_rg_output_fixture=False,
        ),
    )
    assert os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV) == prior


def test_lane_dispatch_modules_still_seven() -> None:
    assert len(LANE_DISPATCH_MODULES) == 7
