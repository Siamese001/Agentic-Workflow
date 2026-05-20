"""W8B — integrated modular lane evidence packages and parent RUN_LINKS binding."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_rg.runtime.integrated_lane_evidence_packaging import (
    finalize_integrated_run_lane_evidence,
    maybe_finalize_lane_evidence_package,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.run_correlation_links import (
    RUN_LINKS_FILENAME,
    assert_run_links_document_shape,
    build_run_links_document,
)
from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    discover_integrated_correlation,
)
from apps_rg.runtime.run_bundle_index import RUN_BUNDLE_INDEX_FILENAME


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
        (integrated / name).write_text(
            json.dumps({"artifact": name, "proof_classification": "INTEGRATED_R4_PRODUCT_RUNTIME"}),
            encoding="utf-8",
        )
    (integrated / RUN_BUNDLE_INDEX_FILENAME).write_text("{}", encoding="utf-8")


def _seed_lane_run(
    repo: Path,
    integrated: Path,
    lane: str,
    run_id: str,
    *,
    with_evidence: bool = False,
) -> Path:
    run_dir = integrated / "modular_r4" / "sections" / lane / "real" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "l2_output.json").write_text(
        json.dumps({"section_id": lane, "run_id": run_id}),
        encoding="utf-8",
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "section_id": lane,
                "command": f"python -m apps_rg --section {lane}",
                "runtime_generation_status": "REAL_LLM",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / RUN_BUNDLE_INDEX_FILENAME).write_text(
        json.dumps({"correlation_id": integrated.name, "run_id": run_id}),
        encoding="utf-8",
    )
    (run_dir / "exit_disposition_receipt.json").write_text(
        json.dumps({"x3_disposition": "X3_ALLOW"}),
        encoding="utf-8",
    )
    ptr = {
        "run_id": run_id,
        "run_dir": run_dir.relative_to(repo).as_posix(),
        "section_id": lane,
    }
    lane_root = integrated / "modular_r4" / "sections" / lane
    (lane_root / "latest_real_run.json").write_text(json.dumps(ptr), encoding="utf-8")
    (lane_root / "latest_successful_real_run.json").write_text(json.dumps(ptr), encoding="utf-8")
    if with_evidence:
        (run_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT).write_text("{}", encoding="utf-8")
        (run_dir / "section_l7_binding_manifest.json").write_text("{}", encoding="utf-8")
    return run_dir


def test_discover_integrated_cli_run_from_lane_path(tmp_path: Path) -> None:
    repo = tmp_path
    integrated = repo / "artifacts" / "apps_rg" / "runs" / "cli_test01"
    run_dir = _seed_lane_run(repo, integrated, "competencies", "competencies_20260520_120000")
    from apps_rg.runtime.integrated_lane_evidence_packaging import (
        discover_integrated_cli_run_from_path,
    )

    hit = discover_integrated_cli_run_from_path(repo, run_dir)
    assert hit is not None
    assert hit.name == "cli_test01"


def test_finalize_integrated_run_populates_run_links_and_not_run(tmp_path: Path) -> None:
    repo = tmp_path
    _write_pipeline_defaults(repo)
    integrated = repo / "artifacts" / "apps_rg" / "runs" / "cli_w8b01"
    integrated.mkdir(parents=True)
    _seed_parent_l7(integrated)
    _seed_lane_run(repo, integrated, "competencies", "competencies_20260520_120000")

    recipe_policy = {
        "fatal_lane_failures": [
            {
                "section_lane": "executive_summary",
                "decisive_reason_code": "PHASE1_NO_RUN_DIR",
                "reason": "generation_status=MISSING_LANE_RUN",
            }
        ]
    }
    section_calls = [
        {
            "section_lane": "executive_summary",
            "decisive_reason_code": "PHASE1_NO_RUN_DIR",
            "generation_status": "MISSING_LANE_RUN",
        },
        {
            "section_lane": "competencies",
            "decisive_reason_code": "X3_ALLOW",
            "generation_status": "REAL_LLM",
            "provider_call_attempted": True,
        },
    ]

    summary = finalize_integrated_run_lane_evidence(
        repo,
        integrated,
        correlation_id="cli_w8b01",
        section_call_records=section_calls,
        recipe_lane_policy=recipe_policy,
    )

    links_path = integrated / RUN_LINKS_FILENAME
    assert links_path.is_file()
    links = json.loads(links_path.read_text(encoding="utf-8"))
    assert_run_links_document_shape(links)
    assert len(links["lane_bundle_refs"]) == len(GENERATED_LANES)

    executed = [r for r in links["lane_bundle_refs"] if r.get("status") == "EXECUTED"]
    not_run = [r for r in links["lane_bundle_refs"] if r.get("status") == "NOT_RUN"]
    assert len(executed) >= 1
    assert any(r["lane"] == "competencies" for r in executed)
    exec_row = next(r for r in executed if r["lane"] == "competencies")
    assert exec_row.get("evidence_package_index_ref")
    assert exec_row.get("section_l7_binding_manifest_ref")
    assert exec_row.get("evidence_package_index_sha256")
    assert exec_row.get("parent_l7_artifact_refs")
    assert any(ref.get("exists") for ref in exec_row["parent_l7_artifact_refs"])

    exec_es = next(r for r in not_run if r["lane"] == "executive_summary")
    assert exec_es["missing_reason"] == "PHASE1_NO_RUN_DIR"
    assert exec_es["status"] == "NOT_RUN"
    assert "expected_run_dir" in exec_es

    comp_run = integrated / "modular_r4" / "sections" / "competencies" / "real" / "competencies_20260520_120000"
    assert (comp_run / EVIDENCE_PACKAGE_INDEX_ARTIFACT).is_file()
    assert (comp_run / "section_l7_binding_manifest.json").is_file()
    assert (comp_run / "spine_subphase_coverage_index.json").is_file()

    status_path = integrated / "integrated_lane_evidence_status.json"
    assert status_path.is_file()
    assert summary["executive_summary_status"] == "NOT_RUN"


def test_run_links_rejects_shadow_aggregate_as_lane_evidence(tmp_path: Path) -> None:
    repo = tmp_path
    _write_pipeline_defaults(repo)
    integrated = repo / "artifacts" / "apps_rg" / "runs" / "cli_shadow"
    integrated.mkdir(parents=True)
    _seed_parent_l7(integrated)
    (integrated / "orchestrate_full_resume_rollup_hint.json").write_text(
        json.dumps({"kind": "orchestrate_full_resume"}),
        encoding="utf-8",
    )
    doc = build_run_links_document(
        repo,
        integrated,
        integrated_run_id="cli_shadow",
        correlation_id=None,
    )
    for row in doc["lane_bundle_refs"]:
        root = str(row.get("root_path") or "")
        assert "orchestrate_full_resume" not in root
        assert "executive_summary_demo" not in root


def test_correlation_discovers_ancestor_cli_run(tmp_path: Path) -> None:
    repo = tmp_path
    integrated = repo / "artifacts" / "apps_rg" / "runs" / "cli_corr"
    run_dir = _seed_lane_run(repo, integrated, "headline", "headline_20260520_120000")
    corr = discover_integrated_correlation(repo, run_dir, section_id="headline")
    assert corr.integrated_dir is not None
    assert corr.integrated_dir.name == "cli_corr"


def test_maybe_finalize_skips_when_already_present(tmp_path: Path) -> None:
    repo = tmp_path
    integrated = repo / "artifacts" / "apps_rg" / "runs" / "cli_skip"
    run_dir = _seed_lane_run(
        repo, integrated, "competencies", "competencies_20260520_130000", with_evidence=True
    )
    os.environ["APPS_RG_WHOLE_RUN_ENVELOPE"] = "1"
    try:
        out = maybe_finalize_lane_evidence_package(
            repo,
            run_dir,
            section_id="competencies",
            run_id="competencies_20260520_130000",
        )
        assert out is not None
        assert out.get("skipped") == "already_finalized"
    finally:
        os.environ.pop("APPS_RG_WHOLE_RUN_ENVELOPE", None)
