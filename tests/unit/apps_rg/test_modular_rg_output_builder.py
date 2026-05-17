"""Deterministic modular rg_output merge — no providers, fail-closed on gaps/mocks."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from apps_rg.l2_recipe.modular_rg_output_builder import build_rg_output_from_modular_sections
from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult
from apps_rg.l2_recipe.rg_output_jsonschema_validate import validate_rg_output_object
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES


def _real_status() -> str:
    return "REAL_LLM"


def _lane_bundle() -> dict[str, dict]:
    """Minimal valid L2 shapes for all seven lanes (REAL_LLM — not plumbing-only)."""
    st = _real_status()
    headline = {
        "runtime_generation_status": st,
        "headline_line": "SVP Engineering | Agentic AI platforms and governed enterprise delivery",
    }
    exec_summ = {
        "runtime_generation_status": st,
        "resume_display_text": (
            "Executive leader delivering agentic AI platforms, retrieval systems, and "
            "governed runtime controls for regulated enterprises with measurable outcomes."
        ),
    }
    uni_n = {
        "runtime_generation_status": st,
        "narrative_sentence": (
            "At Unify, scaled governed agentic platforms with deterministic routing and "
            "enterprise retrieval upgrades across regulated workflows."
        ),
    }
    ibm_n = {
        "runtime_generation_status": st,
        "narrative_sentence": (
            "At IBM, delivered cloud-native AI and analytics platforms with strong uptime "
            "and modernization outcomes across financial services clients."
        ),
    }
    bullet = (
        "Delivered measurable platform outcomes including reliability, cost reductions, "
        "and revenue-facing modernization aligned to enterprise controls."
    )
    uni_b = {
        "runtime_generation_status": st,
        "bullets": [
            {"text": bullet, "source_fact_id": "bul_u1", "has_metric": True},
            {"text": bullet, "source_fact_id": "bul_u2", "has_metric": True},
            {"text": bullet, "source_fact_id": "bul_u3", "has_metric": True},
        ],
    }
    ibm_b = {
        "runtime_generation_status": st,
        "bullets": [
            {"text": bullet, "source_fact_id": "bul_i1", "has_metric": True},
            {"text": bullet, "source_fact_id": "bul_i2", "has_metric": True},
            {"text": bullet, "source_fact_id": "bul_i3", "has_metric": True},
        ],
    }
    comp = {
        "runtime_generation_status": st,
        "competencies": [
            {
                "category_label": "Platforms",
                "terms": [
                    {"text": "Agentic orchestration"},
                    {"text": "Retrieval and GraphRAG"},
                    {"text": "Policy gating"},
                ],
            }
        ],
    }
    return {
        "headline": headline,
        "executive_summary": exec_summ,
        "unify_narrative": uni_n,
        "ibm_narrative": ibm_n,
        "unify_bullets": uni_b,
        "ibm_bullets": ibm_b,
        "competencies": comp,
    }


@dataclass
class _Pkg:
    target_role: str = "SVP Engineering"
    target_company: str = "Example Corp"


def test_builder_positive_writes_schema_valid_final_resume(tmp_path: Path) -> None:
    repo = find_repo_root()
    art = tmp_path / "run"
    art.mkdir()
    modular_root = art / "modular_r4"
    modular_root.mkdir()
    base_path = repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    lanes = _lane_bundle()
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id=f"pytest_{uuid.uuid4().hex[:8]}",
        reject_mocked_lanes=True,
        generated_at_utc="2026-05-16T12:00:00+00:00",
    )
    assert res.ok is True
    assert res.schema_valid is True
    assert res.rg_output is not None
    ok, err = validate_rg_output_object(res.rg_output)
    assert ok is True and err == ""
    out = modular_root / "outputs" / "final_resume.json"
    assert out.is_file()
    disk_ok, disk_err = validate_rg_output_object(json.loads(out.read_text(encoding="utf-8")))
    assert disk_ok is True and disk_err == ""
    out_j = res.rg_output
    assert out_j.get("headline_line")
    assert out_j.get("contact_info", {}).get("email") == "amit.ayer@example.com"
    unify = next(x for x in out_j["sections"]["experience"] if x.get("company") == "Unify Consulting")
    ibm = next(x for x in out_j["sections"]["experience"] if x.get("company") == "IBM")
    insur = next(x for x in out_j["sections"]["experience"] if x.get("company") == "InsurTech Cloud Solutions")
    assert "At Unify" in (unify.get("role_narrative") or "")
    assert "At IBM" in (ibm.get("role_narrative") or "")
    insur_n = str(insur.get("role_narrative") or "").strip()
    assert len(insur_n) >= 20
    assert "AWS" in insur_n and "SOC 2" in insur_n
    skill_cat = out_j["sections"]["skills"]["categories"][0]
    assert skill_cat["name"] == "Platforms"
    assert "Agentic orchestration" in skill_cat["items"]


def test_missing_executive_summary_fails() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"merge_neg_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    modular_root = art / "modular_r4"
    modular_root.mkdir(parents=True, exist_ok=True)
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    lanes = _lane_bundle()
    lanes["executive_summary"] = {**lanes["executive_summary"], "resume_display_text": ""}
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id="neg_exec",
        reject_mocked_lanes=True,
    )
    assert res.ok is False
    assert "executive" in res.failure_reason.lower() or res.failure_reason.startswith("missing_")


def test_missing_headline_fails() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"merge_neg_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    modular_root = art / "modular_r4"
    modular_root.mkdir(parents=True, exist_ok=True)
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    lanes = _lane_bundle()
    lanes["headline"] = {**lanes["headline"], "headline_line": ""}
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id="neg_hl",
        reject_mocked_lanes=True,
    )
    assert res.ok is False
    assert "headline" in res.failure_reason


def test_missing_competencies_fails() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"merge_neg_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    modular_root = art / "modular_r4"
    modular_root.mkdir(parents=True, exist_ok=True)
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    lanes = _lane_bundle()
    lanes["competencies"] = {**lanes["competencies"], "competencies": []}
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id="neg_comp",
        reject_mocked_lanes=True,
    )
    assert res.ok is False
    assert "competenc" in res.failure_reason


def test_mocked_lane_rejected() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"merge_neg_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    modular_root = art / "modular_r4"
    modular_root.mkdir(parents=True, exist_ok=True)
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    lanes = _lane_bundle()
    lanes["headline"] = {**lanes["headline"], "runtime_generation_status": "MOCKED"}
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id="neg_mock",
        reject_mocked_lanes=True,
    )
    assert res.ok is False
    assert "mocked_lane_rejected" in res.failure_reason


def test_malformed_bullet_lane_fails() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"merge_neg_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    modular_root = art / "modular_r4"
    modular_root.mkdir(parents=True, exist_ok=True)
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    lanes = _lane_bundle()
    lanes["unify_bullets"] = {
        "runtime_generation_status": _real_status(),
        "bullets": [{"text": "short", "source_fact_id": "x"}],
    }
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id="neg_bul",
        reject_mocked_lanes=True,
    )
    assert res.ok is False


def test_ok_for_recipe_requires_lane_outputs_and_schema() -> None:
    payload = {"schema_version": "master_resume_v2.16", "candidate_name": "X"}
    no_lane = ModularR4GenerationResult(
        generated_resume=payload,
        section_provider_calls_ref="m",
        section_output_refs={},
        merge_receipt_ref="m",
        schema_validation_receipt_ref="s",
        final_schema_valid=True,
        decisive_status="PASS",
        failure_reason="",
        provider_call_count=0,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=False,
        final_merge_attempted=True,
    )
    assert no_lane.ok_for_recipe_context() is False

    no_schema = ModularR4GenerationResult(
        generated_resume=payload,
        section_provider_calls_ref="m",
        section_output_refs={},
        merge_receipt_ref="m",
        schema_validation_receipt_ref="s",
        final_schema_valid=False,
        decisive_status="PASS",
        failure_reason="",
        provider_call_count=0,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=True,
        final_merge_attempted=True,
    )
    assert no_schema.ok_for_recipe_context() is False


def test_early_career_included_with_single_locked_bullet(tmp_path: Path) -> None:
    """``exp_early_career_001`` may carry one SSOT bullet and still map into rg_output."""
    repo = find_repo_root()
    art = tmp_path / "run_ec"
    art.mkdir()
    modular_root = art / "modular_r4"
    modular_root.mkdir()
    base_path = repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_with_compact_early_career.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    lanes = _lane_bundle()
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id=f"pytest_ec_{uuid.uuid4().hex[:8]}",
        reject_mocked_lanes=True,
        generated_at_utc="2026-05-16T12:00:00+00:00",
    )
    assert res.ok is True
    rec = res.merge_receipt
    assert rec.get("no_synthetic_bullets_assertion") is True
    assert rec.get("locked_employment_source_count") == 4
    assert rec.get("locked_employment_mapped_count") == 4
    assert rec.get("compact_early_career_excluded_count") == 0
    assert not (rec.get("excluded_locked_roles") or [])
    assert res.rg_output is not None
    exp = res.rg_output["sections"]["experience"]
    assert len(exp) == 4
    companies = {str(x.get("company")) for x in exp}
    assert "Early Career Roles" in companies
    early = next(x for x in exp if str(x.get("company")) == "Early Career Roles")
    assert len(early.get("bullets") or []) == 1


def test_compact_early_career_maps_when_three_base_bullets(tmp_path: Path) -> None:
    """If base later adds three facts for early career, map as a normal locked role."""
    repo = find_repo_root()
    art = tmp_path / "run_ec3"
    art.mkdir()
    modular_root = art / "modular_r4"
    modular_root.mkdir()
    base_path = repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_with_compact_early_career.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    btxt = (
        "Additional locked early-career achievement with sufficient characters for schema minimum length rules"
    )
    emp = base["facts"]["employment"]
    early = next(e for e in emp if e.get("fact_id") == "exp_early_career_001")
    early["start_date"] = "1998-06"
    early["end_date"] = "2002-09"
    early["bullets"] = [
        early["bullets"][0],
        {"bullet_id": "bul_early_career_002", "text": btxt, "has_metric": False},
        {"bullet_id": "bul_early_career_003", "text": btxt, "has_metric": False},
    ]
    lanes = _lane_bundle()
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id=f"pytest_ec3_{uuid.uuid4().hex[:8]}",
        reject_mocked_lanes=True,
        generated_at_utc="2026-05-16T12:00:00+00:00",
    )
    assert res.ok is True
    assert res.merge_receipt.get("compact_early_career_excluded_count") == 0
    exp = res.rg_output["sections"]["experience"] if res.rg_output else []
    assert len(exp) == 4
    assert any(str(x.get("company")) == "Early Career Roles" for x in exp)


def test_non_compact_locked_role_still_fails_below_three_bullets(tmp_path: Path) -> None:
    repo = find_repo_root()
    art = tmp_path / "run_nb"
    art.mkdir()
    modular_root = art / "modular_r4"
    modular_root.mkdir()
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    base["facts"]["employment"].append(
        {
            "fact_id": "exp_other_lock_001",
            "employer": "Other Corp",
            "title": "Engineer",
            "location": "Remote",
            "start_date": "2010-01",
            "end_date": "2011-01",
            "is_current": False,
            "bullets": [
                {
                    "bullet_id": "bul_o1",
                    "text": "Single locked bullet with enough characters to pass minimum length threshold for schema",
                    "has_metric": False,
                }
            ],
        },
    )
    lanes = _lane_bundle()
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id="neg_nb",
        reject_mocked_lanes=True,
    )
    assert res.ok is False
    assert "locked_employment_insufficient_bullets:exp_other_lock_001" in res.failure_reason


def test_all_seven_lane_ids_required() -> None:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"merge_neg_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    modular_root = art / "modular_r4"
    modular_root.mkdir(parents=True, exist_ok=True)
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    lanes = _lane_bundle()
    del lanes["headline"]
    res = build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id="neg_miss",
        reject_mocked_lanes=True,
    )
    assert res.ok is False
    assert "missing_required_lanes" in res.failure_reason
    assert "headline" in res.failure_reason
