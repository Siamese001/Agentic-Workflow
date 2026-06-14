"""E2E contract for apps_rg modular section artifact evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.disposition_authority import (
    DISPOSITION_AUTHORITY_LANE,
    EXIT_DISPOSITION_RECEIPT_ARTIFACT,
)
from apps_rg.runtime.full_run_section_status import (
    FULL_RUN_SECTION_STATUS_MD,
    persist_full_run_section_status,
)
from apps_rg.runtime.integrated_lane_evidence_packaging import (
    INTEGRATED_LANE_EVIDENCE_STATUS_ARTIFACT,
    finalize_integrated_run_lane_evidence,
)
from apps_rg.runtime.internal.generated_lane_rollup import (
    GENERATED_LANES,
    collect_lane_from_run_dir,
)
from apps_rg.runtime.run_bundle_index import RUN_BUNDLE_INDEX_FILENAME
from apps_rg.runtime.run_correlation_links import (
    RUN_LINKS_FILENAME,
    assert_run_links_document_shape,
)
from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV
from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    SUBPHASE_COVERAGE_INDEX_ARTIFACT,
)

pytestmark = pytest.mark.e2e

GOLDEN_PATH_SECTIONS: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)

DISPLAY_TEXT_ARTIFACTS: dict[str, str] = {
    "headline": "headline_output.txt",
    "executive_summary": "resume_display_text.txt",
    "unify_bullets": "unify_bullets_output.txt",
    "unify_narrative": "unify_narrative_output.txt",
    "ibm_bullets": "ibm_bullets_output.txt",
    "ibm_narrative": "ibm_narrative_output.txt",
    "competencies": "competencies_display.txt",
}

TEST_PROVIDER = "test_harness"
TEST_MODEL = "apps_rg_e2e_synthetic"
COMPETENCIES_RCA_GATE = "x2_competencies_gap_prioritization_rca"
COMPETENCIES_REVIEW_X3 = "X3_REVIEW_TEST_RCA_REQUIRED"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_pipeline_defaults(repo: Path) -> None:
    cfg_dir = repo / "config" / "profiles" / "apps_rg"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "pipeline_defaults.yaml").write_text(
        'schema_version: "1.0"\n'
        "app_id: apps_rg\n"
        "profile_type: pipeline_defaults\n"
        "pipeline_config:\n"
        "  default_timeout_seconds: 900\n"
        "namespace_defaults:\n"
        '  artifact_namespace: "artifacts/apps_rg/runs"\n'
        '  log_namespace: "apps_rg/pipeline_logs"\n',
        encoding="utf-8",
    )


def _seed_parent_l7(integrated: Path) -> None:
    for name in (
        "agentic_core_how_trace.json",
        "agentic_core_l7_route_family_coverage.json",
        "agentic_core_spine_proof.json",
        "integrated_runtime_artifact_manifest.json",
        "runtime_trace_snapshot.json",
    ):
        _write_json(
            integrated / name,
            {
                "artifact": name,
                "proof_classification": "INTEGRATED_R4_PRODUCT_RUNTIME",
                "producer": "apps_rg_e2e_fixture",
            },
        )
    _write_json(integrated / RUN_BUNDLE_INDEX_FILENAME, {"run_id": integrated.name})


def _section_text(lane: str) -> str:
    if lane == "headline":
        return "Platform transformation leader | AI governance | cloud modernization"
    if lane == "executive_summary":
        return (
            "Executive summary: led AI governance, runtime modernization, and "
            "cross-functional delivery for regulated enterprise platforms."
        )
    if lane.endswith("_bullets"):
        return "- Built governed AI runtime evidence\n- Reduced platform delivery risk"
    if lane.endswith("_narrative"):
        return "Led modernization programs that tied runtime evidence to executive decisions."
    if lane == "competencies":
        return "Agentic AI: routing, evaluation, governance\nCloud: migration, observability"
    raise AssertionError(f"unexpected lane fixture: {lane}")


def _l2_payload(lane: str, run_id: str) -> dict[str, Any]:
    base: dict[str, Any] = {
        "section_id": lane,
        "run_id": run_id,
        "runtime_generation_status": "MOCKED",
        "provider_requested": TEST_PROVIDER,
        "model_requested": TEST_MODEL,
        "test_harness_only": True,
        "product_proof_claimed": False,
    }
    if lane == "headline":
        base["headline_line"] = _section_text(lane)
    elif lane == "executive_summary":
        base["resume_display_text"] = _section_text(lane)
    elif lane == "competencies":
        base["competencies"] = [
            {"name": "Agentic AI", "evidence": ["routing", "evaluation", "governance"]},
            {"name": "Cloud", "evidence": ["migration", "observability"]},
        ]
    elif lane.endswith("_bullets"):
        base["bullets"] = [
            "Built governed AI runtime evidence",
            "Reduced platform delivery risk",
        ]
    elif lane.endswith("_narrative"):
        base["narrative_sentence"] = _section_text(lane)
    return base


def _x2_payload(lane: str) -> dict[str, Any]:
    if lane == "competencies":
        return {
            "gates": [
                {"gate_id": "x2_schema_contract", "pass": True},
                {"gate_id": COMPETENCIES_RCA_GATE, "pass": False},
            ],
            "failed_gates": [COMPETENCIES_RCA_GATE],
            "x2_passed": 1,
            "x2_failed": 1,
            "total_x2_gates": 2,
        }
    return {
        "gates": [{"gate_id": f"x2_{lane}_artifact_contract", "pass": True}],
        "failed_gates": [],
        "x2_passed": 1,
        "x2_failed": 0,
        "total_x2_gates": 1,
    }


def _x3_payload(lane: str) -> dict[str, Any]:
    code = COMPETENCIES_REVIEW_X3 if lane == "competencies" else "X3_ALLOW"
    return {
        "x3_code": code,
        "product_quality_status": "NEEDS_REVIEW" if lane == "competencies" else "PASS",
        "runtime_generation_status": "MOCKED",
        "disposition_authority": DISPOSITION_AUTHORITY_LANE,
        "section_x3_mirror_only": True,
        "spine_x3_claimed": False,
        "proceed_to_runtime": code == "X3_ALLOW",
        "authorization_scope": "test_harness_only",
    }


def _x1d_payload() -> dict[str, Any]:
    return {
        "judges": [
            {"provider_key": "gemini_pro", "provider_status": "MOCKED", "pass": True},
            {"provider_key": "openai_chatgpt", "provider_status": "MOCKED", "pass": True},
            {"provider_key": "anthropic_claude", "provider_status": "MOCKED", "pass": True},
        ]
    }


def _seed_status_lane(integrated: Path, lane: str) -> None:
    lane_dir = integrated / "lanes" / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    (lane_dir / DISPLAY_TEXT_ARTIFACTS[lane]).write_text(_section_text(lane) + "\n", encoding="utf-8")
    _write_json(lane_dir / "run_manifest.json", _run_manifest(lane, run_id=f"{lane}_status"))
    _write_json(lane_dir / "x2_gate_outputs.json", _x2_payload(lane))
    _write_json(lane_dir / "x3_disposition.json", _x3_payload(lane))


def _run_manifest(lane: str, *, run_id: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "section_id": lane,
        "command": f"python -m apps_rg --section {lane}",
        "runtime_generation_status": "MOCKED",
        "provider_requested": TEST_PROVIDER,
        "provider_status": "MOCKED",
        "provider_attempted": False,
        "model_requested": TEST_MODEL,
        "test_harness_only": True,
        "product_proof_claimed": False,
    }


def _seed_modular_lane(repo: Path, integrated: Path, lane: str) -> Path:
    run_id = "r1"
    run_dir = integrated / "modular_r4" / "sections" / lane / "real" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    _write_json(run_dir / "l2_output.json", _l2_payload(lane, run_id))
    _write_json(run_dir / "run_manifest.json", _run_manifest(lane, run_id=run_id))
    _write_json(run_dir / "provider_request.json", _run_manifest(lane, run_id=run_id))
    _write_json(run_dir / "x2_gate_outputs.json", _x2_payload(lane))
    _write_json(run_dir / "x1d_llm_judge_outputs.json", _x1d_payload())
    _write_json(run_dir / "x3_disposition.json", _x3_payload(lane))
    _write_json(run_dir / EXIT_DISPOSITION_RECEIPT_ARTIFACT, _x3_payload(lane))
    _write_json(
        run_dir / "l6_shadow_eval_package.json",
        {"offline_only": True, "runtime_generation_status": "MOCKED", "test_harness_only": True},
    )
    _write_json(
        run_dir / RUN_BUNDLE_INDEX_FILENAME,
        {
            "correlation_id": integrated.name,
            "run_id": run_id,
            "section_id": lane,
            "runtime_generation_status": "MOCKED",
        },
    )

    ptr = {
        "run_id": run_id,
        "run_dir": run_dir.relative_to(repo).as_posix(),
        "section_id": lane,
        "runtime_generation_status": "MOCKED",
        "x3_code": _x3_payload(lane)["x3_code"],
    }
    lane_root = integrated / "modular_r4" / "sections" / lane
    _write_json(lane_root / "latest_real_run.json", ptr)
    _write_json(lane_root / "latest_successful_real_run.json", ptr)
    return run_dir


def test_apps_rg_e2e_artifact_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(MODULAR_R4_SECTIONS_ROOT_ENV, raising=False)
    repo = tmp_path / "r"
    repo.mkdir()
    _write_pipeline_defaults(repo)
    integrated = repo / "artifacts" / "apps_rg" / "runs" / "cli_e2e"
    integrated.mkdir(parents=True)
    _seed_parent_l7(integrated)

    lane_run_dirs = {}
    for lane in GOLDEN_PATH_SECTIONS:
        _seed_status_lane(integrated, lane)
        lane_run_dirs[lane] = _seed_modular_lane(repo, integrated, lane)

    status_result = persist_full_run_section_status(integrated, repo_root=repo)
    status_payload = status_result["payload"]
    status_rows = {row["lane"]: row for row in status_payload["lanes"]}

    assert (integrated / FULL_RUN_SECTION_STATUS_MD).is_file()
    assert {lane for lane, row in status_rows.items() if row["executed"]} == set(GOLDEN_PATH_SECTIONS)
    for lane in GOLDEN_PATH_SECTIONS:
        row = status_rows[lane]
        assert row["display_txt_relpath"] == f"lanes/{lane}/{DISPLAY_TEXT_ARTIFACTS[lane]}"
        assert row["runtime_generation_status"] == "MOCKED"
        assert row["x3_code"] == _x3_payload(lane)["x3_code"]

    assert status_rows["competencies"]["x2_pass"] == "FAIL"
    assert status_rows["competencies"]["x2_failed_gate_ids"] == COMPETENCIES_RCA_GATE
    status_md = (integrated / FULL_RUN_SECTION_STATUS_MD).read_text(encoding="utf-8")
    assert "lanes/executive_summary/resume_display_text.txt" in status_md
    assert COMPETENCIES_RCA_GATE in status_md

    summary = finalize_integrated_run_lane_evidence(
        repo,
        integrated,
        correlation_id=integrated.name,
    )

    links = json.loads((integrated / RUN_LINKS_FILENAME).read_text(encoding="utf-8"))
    assert_run_links_document_shape(links)
    refs = {row["lane"]: row for row in links["lane_bundle_refs"]}
    assert len(refs) == len(GENERATED_LANES)
    assert set(summary["finalized_lanes"]) == set(GOLDEN_PATH_SECTIONS)

    for lane in GOLDEN_PATH_SECTIONS:
        row = refs[lane]
        run_dir = lane_run_dirs[lane]
        assert row["status"] == "EXECUTED"
        assert row["root_path"] == run_dir.relative_to(repo).as_posix()
        assert row["evidence_package_index_ref"]
        assert row["section_l7_binding_manifest_ref"]
        assert row["spine_subphase_coverage_index_ref"]
        assert row["lane_outcome"] == _x3_payload(lane)["x3_code"]
        assert row["lane_x3"] == _x3_payload(lane)["x3_code"]
        assert row["evidence_package_index_sha256"]
        assert (run_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT).is_file()
        assert (run_dir / "section_l7_binding_manifest.json").is_file()
        assert (run_dir / SUBPHASE_COVERAGE_INDEX_ARTIFACT).is_file()

        manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["provider_status"] == "MOCKED"
        assert manifest["model_requested"] == TEST_MODEL
        assert manifest["product_proof_claimed"] is False

        rollup_row = collect_lane_from_run_dir(lane, run_dir, repo=repo)
        assert rollup_row["runtime_generation_status"] == "MOCKED"
        assert rollup_row["freshness"]["provider_requested"] == TEST_PROVIDER
        assert rollup_row["freshness"]["provider_attempted"] is False
        assert rollup_row["gemini_provider_status"] == "MOCKED"
        assert rollup_row["openai_provider_status"] == "MOCKED"
        assert rollup_row["anthropic_provider_status"] == "MOCKED"
        assert rollup_row["x3_code"] == _x3_payload(lane)["x3_code"]

    comp_rollup = collect_lane_from_run_dir("competencies", lane_run_dirs["competencies"], repo=repo)
    assert comp_rollup["x2_failed"] == 1
    assert comp_rollup["x2_failed_gate_ids"] == [COMPETENCIES_RCA_GATE]
    assert comp_rollup["x3_code"] == COMPETENCIES_REVIEW_X3

    non_golden = set(GENERATED_LANES) - set(GOLDEN_PATH_SECTIONS)
    assert non_golden
    for lane in non_golden:
        assert refs[lane]["status"] == "NOT_RUN"
        assert refs[lane]["missing_reason"] == "PHASE1_NO_RUN_DIR"

    evidence_status = json.loads(
        (integrated / INTEGRATED_LANE_EVIDENCE_STATUS_ARTIFACT).read_text(encoding="utf-8")
    )
    assert evidence_status["executed_lane_count"] == len(GOLDEN_PATH_SECTIONS)
    assert evidence_status["not_run_lane_count"] == len(non_golden)
    assert "product certification not upgraded by packaging alone" in evidence_status["explicit_non_claims"]
